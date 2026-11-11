import logging
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.dependencies import get_sparql_client
from app.services.queries.misc import MiscQueries
from app.services.sparql_client import SparqlClient
from app.utils.parsers import group_by_uri, parse_sparql_response
from app.utils.ratelimit import rate_limit
from app.utils.sparql_safe import escape_sparql_iri
from fastapi import Request
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.DEPLOY_PATH}", tags=["misc"])
security = HTTPBearer(auto_error=False)


def is_modifying_query(query: str) -> bool:
    """
    Check if SPARQL query contains INSERT, UPDATE, DELETE, or other modifying operations.
    Returns True if the query attempts to modify data.
    """
    pattern = r'\b(INSERT|DELETE|UPDATE|CLEAR|DROP|CREATE|LOAD|ADD|MOVE|COPY)\b'
    return bool(re.search(pattern, query.upper()))


@router.get("/semantic_search")
async def semantic_search(
    q: str,
    entity_type: Optional[str] = None,
    limit: int = 40,
    client: SparqlClient = Depends(get_sparql_client),
):
    if not q:
        return {"error": "Consulta no proporcionada"}

    # Delegate to the query builder, which tokenizes the terms and escapes them
    # for SPARQL (prevents injection). Honors the optional entity_type filter.
    query = MiscQueries.semantic_search(q, limit=limit, entity_type=entity_type)
    try:
        response = await client.query(query)
        data = parse_sparql_response(response)
        return {"data": data, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filter_options/{filter_type}")
async def get_filter_options(filter_type: str, client: SparqlClient = Depends(get_sparql_client)):
    # Handle static options that don't require SPARQL query
    if filter_type == "entity_type":
        return {"data": ["Person", "Group"]}

    if filter_type == "institution_type":
        return {"data": [
            "Cultural Institution",
            "Academy of Fine Arts",
            "Archive",
            "Art Center",
            "Cultural Center",
            "Exhibition Space",
            "Foundation (Institution)",
            "Interpretation Center",
            "Library",
            "Museographic Collection",
            "Museum",
            "Educational Institution",
            "Art School",
            "University"
        ]}
    
    query = ""
    if filter_type == "gender":
        query = MiscQueries.GET_DISTINCT_GENDERS
    elif filter_type == "activity":
         query = MiscQueries.GET_DISTINCT_ACTIVITIES
    elif filter_type == "artwork_type":
        query = MiscQueries.GET_DISTINCT_ARTWORK_TYPES
    elif filter_type == "topic":
        query = MiscQueries.GET_DISTINCT_TOPICS
    elif filter_type == "exhibition_type":
        query = MiscQueries.GET_DISTINCT_EXHIBITION_TYPES
    elif filter_type == "exhibition_theme":
        query = MiscQueries.GET_DISTINCT_EXHIBITION_THEMES
    elif filter_type == "institution_type":
        query = MiscQueries.GET_INSTITUTION_TYPES
    elif filter_type == "company_isic4_category":
        query = MiscQueries.GET_COMPANY_ISIC4_CATEGORIES
    elif filter_type == "company_size":
        query = MiscQueries.GET_COMPANY_SIZES
    else:
        raise HTTPException(status_code=400, detail="Invalid filter type")

    try:
        response = await client.query(query)
        data = parse_sparql_response(response)
        # Flatten list of dicts to list of values
        values = [item.get('value') for item in data if item.get('value')]
        return {"data": values}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/all_classes",
    tags=["ontologia"],
    description="Obtiene todas las clases de la ontología",
    summary="Clases de la ontología",
)
async def all_classes(client: SparqlClient = Depends(get_sparql_client)):
    query = MiscQueries.ALL_CLASSES
    try:
        response = await client.query(query)
        data = parse_sparql_response(response)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sparql")
async def execute_sparql(
    request: dict,
    client: SparqlClient = Depends(get_sparql_client),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Execute a SPARQL query.
    
    SELECT, ASK, CONSTRUCT, DESCRIBE queries are allowed for all users.
    INSERT, DELETE, UPDATE and other modifying queries require authentication.
    """
    query = request.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    try:
        # Check if this is a modifying query
        if is_modifying_query(query):
            # Require authentication for modifying queries
            if not credentials:
                raise HTTPException(
                    status_code=401, 
                    detail="Authentication required for INSERT/UPDATE/DELETE queries. Please log in first."
                )
            
            # Validate token
            payload = decode_token(credentials.credentials)
            if not payload:
                raise HTTPException(
                    status_code=401, 
                    detail="Invalid or expired token. Please log in again."
                )
            
            # Verify user exists and is active
            from app.models.user import User, UserStatus
            user_id = payload.get("sub")
            try:
                user_id = int(user_id)
            except (TypeError, ValueError):
                raise HTTPException(status_code=401, detail="Invalid token")
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            if user.status != UserStatus.ACTIVE:
                raise HTTPException(status_code=403, detail="Account not active")
            
            # Use update method for modifying queries
            response = await client.update(query)
            # Update responses might be different format
            if isinstance(response, dict) and "message" in response:
                return {"data": [], "message": response.get("message", "Update successful")}
            data = parse_sparql_response(response) if response else []
        else:
            # SELECT/ASK/CONSTRUCT queries allowed for everyone
            response = await client.query(query)
            data = parse_sparql_response(response)
        
        return {"data": data}
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report")
async def report_incident(
    report: dict,
    request: Request,
):
    # Rate-limit to prevent log flooding / spam from anonymous callers.
    rate_limit(request, "report", max_hits=5, window_seconds=600)
    # Cap the logged payload size to avoid log injection / flooding.
    print(f"INCIDENT REPORT: {str(report)[:2000]}")
    return {"status": "received", "message": "Report submitted successfully"}

@router.get("/get_object_any_type/{type}/{id:path}")
async def get_object_any_type(
    type: str, id: str, client: SparqlClient = Depends(get_sparql_client)
):
    type = type.lower()
    if type in ["exposicion", "exhibition"]:
        type = "exhibition"
    elif type in ["persona", "person", "human_actant", "actant", "actor"]:
        type = "human_actant"
    elif type in ["institucion", "institution"]:
        type = "institution"
    elif type in ["empresa", "company"]:
        type = "company"
    elif type in ["artwork", "obra", "work", "work_manifestation"]:
        type = "work_manifestation"

    safe_type = escape_sparql_iri(type)
    safe_id = escape_sparql_iri(id)
    query = MiscQueries.GET_OBJECT_ANY_TYPE % (safe_type, safe_id, safe_type, safe_id, safe_type, safe_id)
    try:
        response = await client.query(query)
        flat_data = parse_sparql_response(response)
        logger.debug("get_object_any_type(%s, %s): %d triples", type, id, len(flat_data))
        
        # Pivot data: convert list of {p, o} to single dict {p: o}
        # This matches what frontend expects (properties object)
        properties = {}
        for item in flat_data:
            p = item.get("p")
            o = item.get("o")
            if p and o:
                # If multiple values exist for same property, you might want a list, 
                # but frontend seems to take first or simple value. 
                # We'll just overwrite or keep first. Let's keep first for simplicity or overwrite?
                # Frontend loop iterates keys, so we need keys to be predicates.
                properties[p] = o
                
        return {"data": [properties]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
