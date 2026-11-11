"""
Company router endpoints.

Provides REST API endpoints for accessing company data.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.dependencies import get_sparql_client
from app.models.responses import ErrorResponseModel, StandardResponseModel
from app.routers.pagination import paginated_query
from app.utils.sparql_safe import escape_sparql_iri
from app.services.queries.companies import CompanyQueries
from app.services.sparql_client import SparqlClient
from app.utils.cursor import decode_cursor
from app.utils.parsers import group_by_uri, parse_sparql_response

router = APIRouter(prefix=f"{settings.DEPLOY_PATH}", tags=["companies"])


@router.get("/count_companies", summary="Count of individuals of class company")
async def count_companies(client: SparqlClient = Depends(get_sparql_client)):
    """Get total count of companies in the knowledge graph."""
    try:
        query = CompanyQueries.COUNT_COMPANIES
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
    "/all_companies", 
    summary="Individuals of class company", 
    response_class=ORJSONResponse
)
async def all_companies(
    cursor: Optional[str] = None,
    page_size: int = 20, 
    q: Optional[str] = None,
    isic4_category: Optional[str] = None,
    size: Optional[str] = None,
    location: Optional[str] = None,
    client: SparqlClient = Depends(get_sparql_client)
):
    """
    Get paginated list of companies with optional filtering.
    
    Uses cursor-based pagination for stable, efficient results.
    """
    # Decode cursor
    last_label, last_uri = None, None
    if cursor:
        decoded = decode_cursor(cursor)
        if decoded:
            last_label, last_uri = decoded

    # Build IDs query with text search filter
    query_ids = CompanyQueries.get_companies_ids(
        limit=page_size + 1, 
        last_label=last_label, 
        last_uri=last_uri, 
        text_search=q,
        isic4_category=isic4_category,
        size=size,
        location=location
    )
    
    # Use shared pagination utility
    result = await paginated_query(
        client=client,
        get_ids_query=query_ids,
        get_details_func=CompanyQueries.get_companies_details,
        page_size=page_size,
        label_field="label"
    )
    
    return ORJSONResponse(content=result)


@router.get("/get_company/{id:path}")
async def get_company(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get detailed information for a specific company by ID."""
    query = CompanyQueries.GET_COMPANY % escape_sparql_iri(id)
    try:
        response = await client.query(query)
        flat_data = parse_sparql_response(response)
        grouped_data = group_by_uri(flat_data)
        return {"data": grouped_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_company_museographer_exhibitions/{id:path}")
async def get_company_museographer_exhibitions(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get exhibitions where this company was the museographer."""
    query = CompanyQueries.get_museographer_exhibitions(id)
    try:
        response = await client.query(query)
        flat_data = parse_sparql_response(response)
        
        exhibitions = []
        for item in flat_data:
            exhibitions.append({
                "uri": item.get("exhibition_uri"),
                "label": item.get("exhibition_label"),
                "start_date": item.get("start_date")
            })
        
        return {"data": exhibitions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
