from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token, create_password_reset_token, verify_password_reset_token, decode_token
from app.dependencies import get_current_user, require_user, require_admin
from app.models.user import User, UserRole, UserStatus
from app.schemas.auth import UserCreate, UserLogin, UserResponse, UserUpdate, Token, MessageResponse, PasswordResetRequest, PasswordResetConfirm
from app.services.email import send_admin_notification, send_approval_notification, send_registration_confirmation, send_password_reset_email
from app.utils.ratelimit import rate_limit

router = APIRouter(prefix='/auth', tags=['authentication'])

@router.post('/register', response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    rate_limit(request, "register", max_hits=5, window_seconds=600)
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail='Email already registered')
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail='Username already taken')
    
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        user_type=user_data.user_type,
        institution_type=user_data.institution_type,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    send_registration_confirmation(user.email, user.full_name or user.username)
    send_admin_notification(user.email, user.full_name or user.username, user_type=user_data.user_type, institution_type=user_data.institution_type)
    
    return MessageResponse(message='Registration successful. Pending admin approval.')

@router.post('/login', response_model=Token)
async def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    rate_limit(request, "login", max_hits=10, window_seconds=300)
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    if user.status == UserStatus.PENDING:
        raise HTTPException(status_code=403, detail='Account pending approval')
    if user.status == UserStatus.REJECTED:
        raise HTTPException(status_code=403, detail='Account has been rejected')
    token = create_access_token(data={'sub': str(user.id), 'email': user.email, 'role': user.role.value})
    return Token(access_token=token)

@router.post('/forgot-password', response_model=MessageResponse)
async def forgot_password(data: PasswordResetRequest, request: Request, db: Session = Depends(get_db)):
    # Rate-limit to prevent email bombing / enumeration via this endpoint.
    rate_limit(request, "forgot_password", max_hits=3, window_seconds=900)
    # Always return a generic response so we don't reveal which emails exist.
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        token = create_password_reset_token(user.id, user.hashed_password)
        reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
        send_password_reset_email(user.email, user.full_name or user.username, reset_url)
    return MessageResponse(message='If that email is registered, a password reset link has been sent.')

@router.post('/reset-password', response_model=MessageResponse)
async def reset_password(data: PasswordResetConfirm, request: Request, db: Session = Depends(get_db)):
    rate_limit(request, "reset_password", max_hits=10, window_seconds=900)
    payload = decode_token(data.token)
    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(status_code=400, detail='Invalid or expired reset token')
    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail='Invalid or expired reset token')
    user = db.query(User).filter(User.id == user_id).first()
    # verify_password_reset_token re-checks type/expiry and binds to the current
    # password hash, so an already-used link no longer works.
    if not user or verify_password_reset_token(data.token, user.hashed_password) is None:
        raise HTTPException(status_code=400, detail='This reset link is invalid, expired, or already used')
    user.hashed_password = hash_password(data.new_password)
    db.commit()
    return MessageResponse(message='Password updated successfully. You can now log in.')

@router.get('/me', response_model=UserResponse)
async def get_current_user_info(user: User = Depends(require_user)):
    return user

@router.get('/users', response_model=List[UserResponse])
async def list_users(status_filter: Optional[UserStatus] = None, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    query = db.query(User).order_by(User.created_at.desc())
    if status_filter: query = query.filter(User.status == status_filter)
    return query.all()

@router.post('/users/{user_id}/approve', response_model=MessageResponse)
async def approve_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail='User not found')
    user.status = UserStatus.ACTIVE
    db.commit()
    send_approval_notification(user.email, approved=True)
    return MessageResponse(message=f'User approved')

@router.post('/users/{user_id}/reject', response_model=MessageResponse)
async def reject_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail='User not found')
    user.status = UserStatus.REJECTED
    db.commit()
    send_approval_notification(user.email, approved=False)
    return MessageResponse(message=f'User rejected')
