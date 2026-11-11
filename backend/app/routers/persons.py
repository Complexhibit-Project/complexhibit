"""
Person/Actor router endpoints.

Provides REST API endpoints for accessing and managing person/actor data.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.dependencies import get_sparql_client, require_user
from app.models.domain import Persona
from app.models.user import User
from app.models.responses import ErrorResponseModel, StandardResponseModel
from app.routers.pagination import paginated_query
from app.utils.sparql_safe import escape_sparql_iri
from app.services.queries.persons import PersonQueries
from app.services.sparql_client import SparqlClient
from app.utils.cursor import decode_cursor
from app.utils.parsers import group_by_uri, parse_sparql_response

router = APIRouter(prefix=f"{settings.DEPLOY_PATH}", tags=["personas"])


@router.get(
    "/all_persons", 
    summary="Individuals of class person", 
    response_class=ORJSONResponse
)
async def all_persons(
    cursor: Optional[str] = None,
    page_size: int = 20, 
    q: Optional[str] = None,
    birth_place: Optional[str] = None,
    birth_date: Optional[str] = None,
    death_date: Optional[str] = None,
    gender: Optional[str] = None,
    activity: Optional[str] = None,
    entity_type: Optional[str] = None,
    client: SparqlClient = Depends(get_sparql_client)
):
    """
    Get paginated list of persons/actors with optional filtering.
    
    Uses cursor-based pagination for stable, efficient results.
    Supports entity_type filter: 'person' for individuals, 'group' for groups.
    """
    # Decode cursor
    last_label, last_uri = None, None
    if cursor:
        decoded = decode_cursor(cursor)
        if decoded:
            last_label, last_uri = decoded

    # Build IDs query with all filters
    query_ids = PersonQueries.get_personas_ids(
        limit=page_size + 1, 
        last_label=last_label, 
        last_uri=last_uri, 
        text_search=q,
        birth_place=birth_place,
        birth_date=birth_date,
        death_date=death_date,
        gender=gender,
        activity=activity,
        entity_type=entity_type
    )
    
    # Use shared pagination utility
    result = await paginated_query(
        client=client,
        get_ids_query=query_ids,
        get_details_func=PersonQueries.get_personas_details,
        page_size=page_size,
        label_field="label"
    )
    
    return ORJSONResponse(content=result)


@router.get("/count_persons", summary="Count of individuals of class actant/person")
async def count_persons(client: SparqlClient = Depends(get_sparql_client)):
    """Get total count of persons/actors in the knowledge graph."""
    try:
        query = PersonQueries.COUNT_ACTANTS
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


@router.get("/get_person/{id:path}")
async def get_person(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get detailed information for a specific person by ID."""
    query = PersonQueries.GET_PERSONS_AND_GROUPS % escape_sparql_iri(id)
    try:
        response = await client.query(query)
        flat_data = parse_sparql_response(response)
        grouped_data = group_by_uri(flat_data, list_fields=["label_place", "label_date"])
        return {"data": grouped_data, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create_person", status_code=status.HTTP_201_CREATED)
async def create_person(
    persona: Persona, 
    client: SparqlClient = Depends(get_sparql_client),
    user: User = Depends(require_user)
):
    """Create a new person in the knowledge graph."""
    try:
        query, uri = PersonQueries.add_persona(persona)
        response = await client.update(query)
        return {"uri": uri, "label": persona.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding person: {str(e)}")


@router.put("/update_person", status_code=status.HTTP_200_OK)
async def update_person(
    persona: Persona, 
    client: SparqlClient = Depends(get_sparql_client),
    user: User = Depends(require_user)
):
    """Update an existing person in the knowledge graph.
    
    This performs a delete of existing triples followed by re-insert with new data.
    """
    try:
        if not persona.uri:
            raise HTTPException(status_code=400, detail="URI is required for update")
        
        # Delete existing triples for this entity (execute each query separately)
        delete_queries = PersonQueries.delete_persona(persona.uri)
        for delete_query in delete_queries:
            await client.update(delete_query)
        
        # Insert new triples with updated data
        insert_query, uri = PersonQueries.add_persona(persona)
        await client.update(insert_query)
        
        return {"uri": uri, "label": persona.name, "updated": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating person: {str(e)}")


@router.get("/get_actor_roles/{id:path}")
async def get_actor_roles(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get all exhibitions and artworks where the actor participated in any role."""
    query = PersonQueries.get_actor_roles(id)
    try:
        response = await client.query(query)
        flat_data = parse_sparql_response(response)
        
        # Group by role type
        roles_by_type: Dict[str, List[Dict]] = {}
        for item in flat_data:
            role_type = item.get("role_type", "Participant")
            if role_type not in roles_by_type:
                roles_by_type[role_type] = []
            roles_by_type[role_type].append({
                "uri": item.get("item_uri"),
                "label": item.get("item_label"),
                "type": item.get("item_type", "exhibition")
            })
        
        return {"data": roles_by_type, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_person_collaborators/{id:path}")
async def get_person_collaborators(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get all persons and institutions that collaborate with this person, grouped by relationship type."""
    query = PersonQueries.get_person_collaborators(id)
    try:
        response = await client.query(query)
        flat_data = parse_sparql_response(response)
        
        # Group by relationship type and collaborator type
        result = {
            "collaborations": [], # Person <-> Person (generic)
            "memberships": [],    # Person <-> Group
            "affiliations": []    # Person <-> Institution
        }
        
        for item in flat_data:
            relationship = item.get("relationship_type", "collaboration")
            collab_type = item.get("collaborator_type", "unknown")
            
            entry = {
                "uri": item.get("collaborator_uri"),
                "label": item.get("collaborator_label"),
                "type": collab_type
            }
            
            if relationship == "membership":
                result["memberships"].append(entry)
            elif relationship == "affiliation":
                result["affiliations"].append(entry)
            # Remove fallback to generic collaborations as user requested strict semantics
        
        return {"data": result, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_person_executive_positions/{id:path}")
async def get_person_executive_positions(id: str, client: SparqlClient = Depends(get_sparql_client)):
    """Get institutions where this person holds an executive position."""
    query = PersonQueries.get_person_executive_positions(id)
    try:
        response = await client.query(query)
        flat_data = parse_sparql_response(response)
        
        positions = []
        for item in flat_data:
            positions.append({
                "uri": item.get("institution_uri"),
                "label": item.get("institution_label")
            })
        
        return {"data": positions, "sparql": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
