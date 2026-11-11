"""
Shared router utilities for paginated SPARQL queries.

This module provides a generic function for handling cursor-based pagination
that's reused across all entity routers.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

from fastapi import HTTPException
from fastapi.responses import ORJSONResponse

from app.services.sparql_client import SparqlClient
from app.utils.cursor import decode_cursor, encode_cursor
from app.utils.parsers import parse_sparql_response


async def paginated_query(
    client: SparqlClient,
    get_ids_query: str,
    get_details_func: Callable[[List[str]], str],
    cursor: Optional[str] = None,
    page_size: int = 10,
    label_field: str = "label",
) -> Dict[str, Any]:
    """
    Execute a paginated SPARQL query with cursor-based pagination.
    
    This is the generic implementation of the two-step query pattern:
    1. Get filtered/paginated IDs
    2. Fetch details for those IDs
    
    Args:
        client: SparqlClient instance
        get_ids_query: SPARQL query to get IDs (should return uri and label fields)
        get_details_func: Function that takes list of URIs and returns details query
        cursor: Pagination cursor from previous page (or None for first page)
        page_size: Number of items per page
        label_field: Field name used for cursor (default: "label")
        
    Returns:
        Dict with 'data' (list of items) and 'next_cursor' (string or None)
    """
    try:
        # Step 1: Get IDs
        response_ids = await client.query(get_ids_query)
        data_ids = parse_sparql_response(response_ids)
        
        if not data_ids:
            return {"data": [], "next_cursor": None}
        
        # Cursor logic - check if there are more results
        next_cursor = None
        if len(data_ids) > page_size:
            data_ids = data_ids[:page_size]
            last_item = data_ids[-1]
            
            # Handle different label field names (label, inner_label, etc.)
            label_value = last_item.get(label_field) or last_item.get("inner_label") or last_item.get("label")
            uri_value = last_item.get("uri")
            
            if label_value and uri_value:
                next_cursor = encode_cursor(label_value, uri_value)
        
        # Extract URIs
        uris = [item["uri"] for item in data_ids if "uri" in item]
        
        if not uris:
            return {"data": data_ids, "next_cursor": next_cursor}
        
        # Step 2: Get details
        query_details = get_details_func(uris)
        response_details = await client.query(query_details)
        data_details = parse_sparql_response(response_details)
        
        # Merge: Map details by URI
        details_map = {item["uri"]: item for item in data_details}
        
        # Reconstruct list maintaining original order
        final_data = []
        for item_id in data_ids:
            uri = item_id.get("uri")
            if uri and uri in details_map:
                final_data.append(details_map[uri])
            else:
                final_data.append(item_id)
        
        return {"data": final_data, "next_cursor": next_cursor}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def paginated_response(data: Dict[str, Any]) -> ORJSONResponse:
    """
    Wrap paginated query results in an ORJSONResponse.
    
    Args:
        data: Dict with 'data' and 'next_cursor' keys
        
    Returns:
        ORJSONResponse with the data
    """
    return ORJSONResponse(content=data)
