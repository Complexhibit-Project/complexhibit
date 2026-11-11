"""
Exhibition router endpoints.

Provides REST API endpoints for accessing and managing exhibition data.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.dependencies import get_sparql_client, require_user
from app.models.domain import Exposicion
from app.models.user import User
from app.models.responses import ErrorResponseModel, StandardResponseModel
from app.routers.pagination import paginated_query
from app.utils.sparql_safe import escape_sparql_iri
from app.services.queries.exhibitions import ExhibitionQueries
from app.services.sparql_client import SparqlClient
from app.utils.cursor import decode_cursor
from app.utils.parsers import parse_sparql_response

router = APIRouter(prefix=f"{settings.DEPLOY_PATH}", tags=["exposiciones"])


@router.get("/count_exhibitions", summary="Count of individuals of class exhibition")
async def count_exhibitions(client: SparqlClient = Depends(get_sparql_client)):
    """Get total count of exhibitions in the knowledge graph."""
    try:
        query = ExhibitionQueries.COUNT_EXPOSICIONES
        response = await client.query(query)
        parsed = parse_sparql_response(response)
        count = parsed[0]["count"] if parsed else 0
        return StandardResponseModel(data={"count": count}, message="Operation successful")
    except Exception as e:
        error_response = ErrorResponseModel(
            error_code="INTERNAL_SERVER_ERROR",
            error_message="Internal Server Error",
            error_details={"error": str(e)},
        )
        raise HTTPException(status_code=500, detail=error_response.dict())

@router.get(
    "/all_exhibitions", 
    summary="Individuals of class exhibition", 
    response_class=ORJSONResponse
)
async def all_exhibitions(
    cursor: Optional[str] = None,
    page_size: int = 20, 
    q: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    curator_name: Optional[str] = None,
    place: Optional[str] = None,
    organizer: Optional[str] = None,
    sponsor: Optional[str] = None,
    theme: Optional[str] = None,
    exhibition_type: Optional[str] = None,
    participating_actant: Optional[str] = None,
    displayed_artwork: Optional[str] = None,
    curator: Optional[str] = None,
    organizer_uri: Optional[str] = None,
    sponsor_uri: Optional[str] = None,
    client: SparqlClient = Depends(get_sparql_client)
):
    """
    Get paginated list of exhibitions with optional filtering.
    
    Uses cursor-based pagination for stable, efficient results.
    """
    # Decode cursor
    last_label, last_uri = None, None
    if cursor:
        decoded = decode_cursor(cursor)
        if decoded:
            last_label, last_uri = decoded

    # Build IDs query with filters
    query_ids = ExhibitionQueries.get_exposiciones_ids(
        limit=page_size + 1, 
        last_label=last_label, 
        last_uri=last_uri, 
        text_search=q,
        start_date=start_date,
        end_date=end_date,
        curator_name=curator_name,
        place=place,
        organizer=organizer,
        sponsor=sponsor,
        theme=theme,
        exhibition_type=exhibition_type,
        participating_actant=participating_actant,
        displayed_artwork=displayed_artwork,
        curator=curator,
        organizer_uri=organizer_uri,
        sponsor_uri=sponsor_uri
    )
    
    # Use shared pagination utility
    result = await paginated_query(
        client=client,
        get_ids_query=query_ids,
        get_details_func=ExhibitionQueries.get_exposiciones_details,
        page_size=page_size,
        label_field="inner_label"
    )
    
    return ORJSONResponse(content=result)
@router.post("/create_exhibition", status_code=status.HTTP_201_CREATED)
async def create_exhibition(
    exposicion: Exposicion, 
    client: SparqlClient = Depends(get_sparql_client),
    user: User = Depends(require_user)
):
    """Create a new exhibition in the knowledge graph."""
    try:
        query, uri = ExhibitionQueries.add_exposicion(exposicion)
        response = await client.update(query)
        return {"uri": uri, "label": exposicion.name, "message": "Exhibition created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding exhibition: {str(e)}")


@router.put("/update_exhibition", status_code=status.HTTP_200_OK)
async def update_exhibition(
    exposicion: Exposicion, 
    client: SparqlClient = Depends(get_sparql_client),
    user: User = Depends(require_user)
):
    """Update an existing exhibition in the knowledge graph."""
    try:
        if not exposicion.uri:
            raise HTTPException(status_code=400, detail="URI is required for update")
        
        # Delete existing triples for this entity (execute each query separately)
        delete_queries = ExhibitionQueries.delete_exposicion(exposicion.uri)
        for delete_query in delete_queries:
            await client.update(delete_query)
        
        # Insert new triples with updated data
        insert_query, uri = ExhibitionQueries.add_exposicion(exposicion)
        await client.update(insert_query)
        
        return {"uri": uri, "label": exposicion.name, "updated": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating exhibition: {str(e)}")


@router.get("/get_exhibition_museographers/{id:path}")
async def get_exhibition_museographers(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get companies that provided museography services for this exhibition."""
    query = ExhibitionQueries.get_exhibition_museographers(id)
    try:
        response = await client.query(query)
        flat_data = parse_sparql_response(response)
        
        museographers = []
        for item in flat_data:
            museographers.append({
                "uri": item.get("company_uri"),
                "label": item.get("company_label")
            })
        
        return {"data": museographers, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_exhibition/{id:path}")
async def get_exhibition(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get detailed information for a specific exhibition by ID."""
    query = ExhibitionQueries.GET_EXHIBITION_BY_ID % escape_sparql_iri(id)
    try:
        response = await client.query(query)
        flat_data = parse_sparql_response(response)
        
        result = []
        if flat_data:
            result = [flat_data[0]]
            
        return {"data": result, "sparql": query}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

