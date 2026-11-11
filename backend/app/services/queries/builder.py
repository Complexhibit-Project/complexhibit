"""
Shared SPARQL query building utilities.

This module provides reusable functions for building common SPARQL query patterns,
reducing code duplication across entity-specific query classes.
"""

from typing import Optional, List
from app.services.queries.base import PREFIXES


def build_text_filter(field: str, search_term: Optional[str]) -> str:
    """
    Build a case-insensitive regex filter for text search.
    
    Args:
        field: The SPARQL variable name (without ?)
        search_term: The text to search for
        
    Returns:
        SPARQL FILTER clause or empty string if no search term
    """
    if not search_term:
        return ""
    # Escape special regex characters for SPARQL
    escaped = search_term.replace('\\', '\\\\').replace('"', '\\"')
    return f'FILTER regex(?{field}, "{escaped}", "i")'


def build_pagination_filter(
    last_label: Optional[str], 
    last_uri: Optional[str],
    label_field: str = "label"
) -> str:
    """
    Build a cursor-based pagination filter.
    
    Uses keyset pagination (label + uri) for efficient, stable ordering.
    
    Args:
        last_label: The label from the last item of the previous page
        last_uri: The URI from the last item of the previous page
        label_field: The SPARQL variable name for the label (default: "label")
        
    Returns:
        SPARQL FILTER clause for pagination or empty string
    """
    if not last_label or not last_uri:
        return ""
    
    # Escape quotes in label for SPARQL string literal
    safe_label = last_label.replace('"', '\\"')
    
    return f"""
        FILTER (
            lcase(?{label_field}) > lcase("{safe_label}") || 
            (lcase(?{label_field}) = lcase("{safe_label}") && ?uri > <{last_uri}>)
        )
    """


def build_values_clause(uris: List[str], variable: str = "uri") -> str:
    """
    Build a VALUES clause for batch URI lookups.
    
    Args:
        uris: List of URIs to include
        variable: SPARQL variable name (without ?)
        
    Returns:
        VALUES clause string or empty string if no URIs
    """
    if not uris:
        return ""
    
    uris_str = " ".join([f"<{u}>" for u in uris])
    return f"VALUES ?{variable} {{ {uris_str} }}"


def build_optional_filter(field: str, value: Optional[str], pattern_type: str = "regex") -> str:
    """
    Build an optional filter that's only added if value is provided.
    
    Args:
        field: SPARQL variable name (without ?)
        value: Value to filter by (None means no filter)
        pattern_type: Type of matching - "regex" (case-insensitive) or "exact"
        
    Returns:
        SPARQL FILTER clause or empty string
    """
    if not value:
        return ""
    
    escaped = value.replace('\\', '\\\\').replace('"', '\\"')
    
    if pattern_type == "exact":
        return f'FILTER (?{field} = "{escaped}")'
    else:  # regex (default)
        return f'FILTER regex(?{field}, "{escaped}", "i")'


def build_date_filter(
    field: str, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None
) -> str:
    """
    Build a date range filter.
    
    Args:
        field: SPARQL variable name for the date
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        
    Returns:
        SPARQL FILTER clause or empty string
    """
    filters = []
    
    if start_date:
        filters.append(f'?{field} >= "{start_date}"')
    if end_date:
        filters.append(f'?{field} <= "{end_date}"')
    
    if not filters:
        return ""
    
    return f"FILTER ({' && '.join(filters)})"


def build_year_filter(field: str, year: Optional[str]) -> str:
    """
    Build a year extraction filter for date fields.
    
    Args:
        field: SPARQL variable name for the date
        year: Year to match (as string)
        
    Returns:
        SPARQL FILTER clause or empty string
    """
    if not year:
        return ""
    
    return f'FILTER (YEAR(?{field}) = {year})'
