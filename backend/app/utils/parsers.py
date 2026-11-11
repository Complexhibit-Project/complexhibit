from typing import Any, Dict, List, Optional


def parse_sparql_response(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parses a standard SPARQL JSON response into a list of dictionaries.
    Extracts the 'value' from each binding.
    Optimized using list comprehensions.
    """
    if not response or "results" not in response or "bindings" not in response["results"]:
        return []

    return [
        {key: value.get("value") for key, value in binding.items()}
        for binding in response["results"]["bindings"]
    ]


def group_by_uri(data: List[Dict[str, Any]], list_fields: List[str] = None) -> List[Dict[str, Any]]:
    """
    Groups a list of flat dictionaries by 'uri'.
    Merges fields specified in `list_fields` into lists.
    Optimized using sets for O(1) deduplication.
    """
    if list_fields is None:
        list_fields = []

    grouped = {}
    # Use a separate structure to track seen values for list fields to avoid O(N) lookup
    # seen_values[uri][field] = set()
    seen_values = {}

    for item in data:
        uri = item.get("uri")
        if not uri:
            continue

        if uri not in grouped:
            grouped[uri] = item.copy()
            seen_values[uri] = {}
            for field in list_fields:
                val = item.get(field)
                if val:
                    grouped[uri][field] = [val]
                    seen_values[uri][field] = {val}
                else:
                    grouped[uri][field] = []
                    seen_values[uri][field] = set()
        else:
            for field in list_fields:
                val = item.get(field)
                if val:
                    # Check against set for O(1) lookup
                    if field not in seen_values[uri]:
                         seen_values[uri][field] = set()
                    
                    if val not in seen_values[uri][field]:
                        grouped[uri][field].append(val)
                        seen_values[uri][field].add(val)

    return list(grouped.values())
