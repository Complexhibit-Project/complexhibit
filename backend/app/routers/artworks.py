"""
Artwork router endpoints.

Provides REST API endpoints for accessing and managing artwork data.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.dependencies import get_sparql_client, require_user
from app.models.domain import ObraDeArte
from app.models.user import User
from app.models.responses import ErrorResponseModel, StandardResponseModel
from app.routers.pagination import paginated_query
from app.utils.sparql_safe import escape_sparql_iri
from app.services.queries.artworks import ArtworkQueries
from app.services.sparql_client import SparqlClient
from app.utils.cursor import decode_cursor
from app.utils.parsers import parse_sparql_response

router = APIRouter(prefix=f"{settings.DEPLOY_PATH}", tags=["obras"])


@router.get("/count_artworks", summary="Count of individuals of class artwork")
async def count_artworks(client: SparqlClient = Depends(get_sparql_client)):
    """Get total count of artworks in the knowledge graph."""
    try:
        query = ArtworkQueries.COUNT_OBRAS
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
    "/all_artworks", 
    summary="Individuals of class artwork", 
    response_class=ORJSONResponse
)
async def all_artworks(
    cursor: Optional[str] = None,
    page_size: int = 20, 
    q: Optional[str] = None,
    author_name: Optional[str] = None,
    type_filter: Optional[str] = None,
    start_date: Optional[str] = None,
    owner: Optional[str] = None,
    topic: Optional[str] = None,
    exhibition: Optional[str] = None,
    author_uri: Optional[str] = None,
    owner_uri: Optional[str] = None,
    exhibition_uri: Optional[str] = None,
    production_place: Optional[str] = None,
    client: SparqlClient = Depends(get_sparql_client)
):
    """
    Get paginated list of artworks with optional filtering.
    
    Uses cursor-based pagination for stable, efficient results.
    """
    # Decode cursor
    last_label, last_uri = None, None
    if cursor:
        decoded = decode_cursor(cursor)
        if decoded:
            last_label, last_uri = decoded

    # Build IDs query with filters
    query_ids = ArtworkQueries.get_obras_ids(
        limit=page_size + 1, 
        last_label=last_label, 
        last_uri=last_uri, 
        text_search=q,
        author_name=author_name,
        type_filter=type_filter,
        start_date=start_date,
        owner=owner,
        topic=topic,
        exhibition=exhibition,
        author_uri=author_uri,
        owner_uri=owner_uri,
        exhibition_uri=exhibition_uri,
        production_place=production_place
    )
    
    # Use shared pagination utility
    result = await paginated_query(
        client=client,
        get_ids_query=query_ids,
        get_details_func=ArtworkQueries.get_obras_details,
        page_size=page_size,
        label_field="label"
    )
    
    return ORJSONResponse(content=result)
@router.post("/create_artwork", status_code=status.HTTP_201_CREATED)
async def create_artwork(
    obra: ObraDeArte, 
    client: SparqlClient = Depends(get_sparql_client),
    user: User = Depends(require_user)
):
    """Create a new artwork in the knowledge graph."""
    try:
        query, uri = ArtworkQueries.add_obra(obra)
        response = await client.update(query)
        return {"uri": uri, "label": obra.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding artwork: {str(e)}")


@router.put("/update_artwork", status_code=status.HTTP_200_OK)
async def update_artwork(
    obra: ObraDeArte, 
    client: SparqlClient = Depends(get_sparql_client),
    user: User = Depends(require_user)
):
    """Update an existing artwork in the knowledge graph."""
    try:
        if not obra.uri:
            raise HTTPException(status_code=400, detail="URI is required for update")
        
        # Delete existing triples for this entity (execute each query separately)
        delete_queries = ArtworkQueries.delete_obra(obra.uri)
        for delete_query in delete_queries:
            await client.update(delete_query)
        
        # Insert new triples with updated data
        insert_query, uri = ArtworkQueries.add_obra(obra)
        await client.update(insert_query)
        
        return {"uri": uri, "label": obra.name, "updated": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating artwork: {str(e)}")


@router.get("/get_artwork/{id:path}")
async def get_artwork(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get detailed information for a specific artwork by ID."""
    query = ArtworkQueries.GET_ARTWORK_BY_ID % escape_sparql_iri(id)
    try:
        response = await client.query(query)
        flat_data = parse_sparql_response(response)
        return {"data": flat_data, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
