"""
Initialize database with admin user.

Run this script to create the first admin user.
Usage: python -m app.scripts.init_admin
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import SessionLocal, create_tables
from app.core.security import hash_password
from app.core.config import settings
from app.models.user import User, UserRole, UserStatus


def init_admin():
    """Create initial admin user if not exists."""
    create_tables()
    
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        # Don't block startup: skip admin bootstrap so the API still boots. Set
        # ADMIN_EMAIL and ADMIN_PASSWORD in the environment to create the admin.
        print("WARNING: ADMIN_EMAIL/ADMIN_PASSWORD not set - skipping admin user creation.")
        return

    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        
        if admin:
            print(f"Admin user already exists: {admin.email}")
            if admin.role != UserRole.ADMIN:
                admin.role = UserRole.ADMIN
                admin.status = UserStatus.ACTIVE
                db.commit()
                print(f"Updated {admin.email} to admin role")
            return
        
        # Create admin user
        admin = User(
            email=settings.ADMIN_EMAIL,
            username="admin",
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            full_name="Administrator",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        
        db.add(admin)
        db.commit()
        
        print(f"Created admin user: {admin.email}")
        print("⚠️  Password was set from ADMIN_PASSWORD env var - change it after first login.")
        
    finally:
        db.close()


if __name__ == "__main__":
    init_admin()
