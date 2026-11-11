"""
Institution router endpoints.

Provides REST API endpoints for accessing and managing institution data.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.dependencies import get_sparql_client, require_user
from app.models.domain import Institucion
from app.models.user import User
from app.models.responses import ErrorResponseModel, StandardResponseModel
from app.routers.pagination import paginated_query
from app.utils.sparql_safe import escape_sparql_iri
from app.services.queries.institutions import InstitutionQueries
from app.services.sparql_client import SparqlClient
from app.utils.cursor import decode_cursor
from app.utils.parsers import group_by_uri, parse_sparql_response

router = APIRouter(prefix=f"{settings.DEPLOY_PATH}", tags=["instituciones"])


@router.get("/count_institutions", summary="Count of individuals of class institution")
async def count_institutions(client: SparqlClient = Depends(get_sparql_client)):
    """Get total count of institutions in the knowledge graph."""
    try:
        query = InstitutionQueries.COUNT_INSTITUCIONES
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
    "/all_institutions",
    summary="Individuals of class institution",
    response_class=ORJSONResponse
)
async def all_institutions(
    cursor: Optional[str] = None,
    page_size: int = 20,
    q: Optional[str] = None,
    place: Optional[str] = None,
    apelation: Optional[str] = None,
    institution_type: Optional[str] = None,
    client: SparqlClient = Depends(get_sparql_client)
):
    """
    Get paginated list of institutions with optional filtering.
    
    Uses cursor-based pagination for stable, efficient results.
    """
    # Decode cursor
    last_label, last_uri = None, None
    if cursor:
        decoded = decode_cursor(cursor)
        if decoded:
            last_label, last_uri = decoded

    # Build IDs query with filters
    query_ids = InstitutionQueries.get_instituciones_ids(
        limit=page_size + 1,
        last_label=last_label,
        last_uri=last_uri,
        text_search=q,
        place=place,
        apelation=apelation,
        institution_type=institution_type
    )
    
    # Use shared pagination utility
    result = await paginated_query(
        client=client,
        get_ids_query=query_ids,
        get_details_func=InstitutionQueries.get_instituciones_details,
        page_size=page_size,
        label_field="label"
    )
    
    return ORJSONResponse(content=result)
@router.post("/create_institution", status_code=status.HTTP_201_CREATED)
async def create_institution(
    entidad: Institucion, 
    client: SparqlClient = Depends(get_sparql_client),
    user: User = Depends(require_user)
):
    """Create a new institution in the knowledge graph."""
    try:
        query = InstitutionQueries.add_institucion(entidad)
        await client.update(query)
        return {
            "label": entidad.nombre,
            "uri": f"{settings.URI_ONTOLOGIA}institution/{entidad.id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding institution: {str(e)}")


@router.put("/update_institution", status_code=status.HTTP_200_OK)
async def update_institution(
    entidad: Institucion, 
    client: SparqlClient = Depends(get_sparql_client),
    user: User = Depends(require_user)
):
    """Update an existing institution in the knowledge graph."""
    try:
        if not entidad.uri:
            raise HTTPException(status_code=400, detail="URI is required for update")
        
        # Delete existing triples for this entity (execute each query separately)
        delete_queries = InstitutionQueries.delete_institucion(entidad.uri)
        for delete_query in delete_queries:
            await client.update(delete_query)
        
        # Insert new triples with updated data
        insert_query = InstitutionQueries.add_institucion(entidad)
        await client.update(insert_query)
        
        return {"uri": entidad.uri, "label": entidad.nombre, "updated": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating institution: {str(e)}")


@router.get("/get_institution/{id:path}")
async def get_institution(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get detailed information for a specific institution by ID."""
    # The query in InstitutionQueries.GET_INSTITUTION uses regex.
    query = InstitutionQueries.GET_INSTITUTION % escape_sparql_iri(id)
    try:
        response = await client.query(query)
        data = parse_sparql_response(response)
        return {"data": data, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_institution_exhibitions/{id:path}")
async def get_institution_exhibitions(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get exhibitions hosted by or organized by the institution, grouped by role."""
    query = InstitutionQueries.GET_HOSTED_EXHIBITIONS % escape_sparql_iri(id)
    try:
        response = await client.query(query)
        data = parse_sparql_response(response)
        
        # Group by role
        grouped = {
            "venue": [],
            "organizer": [],
            "funder": []
        }
        
        for item in data:
            role = (item.get("role") or "").lower()
            exhibition = {
                "uri": item.get("uri"),
                "label": item.get("label"),
                "start_date": item.get("start_date")
            }
            if role == "venue":
                grouped["venue"].append(exhibition)
            elif role == "organizer":
                grouped["organizer"].append(exhibition)
            elif role == "funder":
                grouped["funder"].append(exhibition)
        
        return {"data": grouped, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_institution_lender_exhibitions/{id:path}")
async def get_institution_lender_exhibitions(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get exhibitions where the institution was a lender."""
    query = InstitutionQueries.GET_LENDER_EXHIBITIONS % escape_sparql_iri(id)
    try:
        response = await client.query(query)
        data = parse_sparql_response(response)
        return {"data": data, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_institution_owned_artworks/{id:path}")
async def get_institution_owned_artworks(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get artworks owned by the institution."""
    query = InstitutionQueries.GET_OWNED_ARTWORKS % escape_sparql_iri(id)
    try:
        response = await client.query(query)
        data = parse_sparql_response(response)
        return {"data": data, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_institution_collaborators/{id:path}")
async def get_institution_collaborators(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get persons who collaborate with this institution."""
    query = InstitutionQueries.get_institution_collaborators(id)
    try:
        response = await client.query(query)
        flat_data = parse_sparql_response(response)
        
        collaborators = []
        for item in flat_data:
            collaborators.append({
                "uri": item.get("collaborator_uri"),
                "label": item.get("collaborator_label")
            })
        
        return {"data": collaborators, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_institution_executives/{id:path}")
async def get_institution_executives(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get executive position holders at this institution."""
    query = InstitutionQueries.get_institution_executives(id)
    try:
        response = await client.query(query)
        flat_data = parse_sparql_response(response)
        
        executives = []
        for item in flat_data:
            executives.append({
                "uri": item.get("person_uri"),
                "label": item.get("person_label")
            })
        
        return {"data": executives, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_institution_parent/{id:path}")
async def get_institution_parent(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get the parent organization of this institution."""
    query = InstitutionQueries.get_parent_organization(id)
    try:
        response = await client.query(query)
        flat_data = parse_sparql_response(response)
        
        parent = None
        if flat_data and len(flat_data) > 0:
            item = flat_data[0]
            parent = {
                "uri": item.get("parent_uri"),
                "label": item.get("parent_label")
            }
        
        return {"data": parent, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_institution_children/{id:path}")
async def get_institution_children(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get child organizations of this institution."""
    query = InstitutionQueries.get_child_organizations(id)
    try:
        response = await client.query(query)
        flat_data = parse_sparql_response(response)
        
        children = []
        for item in flat_data:
            children.append({
                "uri": item.get("child_uri"),
                "label": item.get("child_label")
            })
        
        return {"data": children, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
