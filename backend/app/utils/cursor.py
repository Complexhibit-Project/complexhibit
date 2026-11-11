import base64
from typing import Optional, Tuple

def encode_cursor(label: str, uri: str) -> str:
    """
    Encodes a cursor from a label and a URI.
    Format: base64(label|uri)
    """
    # Ensure we handle None or empty values gracefully, though in our case label and uri should exist
    if not label:
        label = ""
    if not uri:
        uri = ""
        
    combined = f"{label}|{uri}"
    return base64.b64encode(combined.encode('utf-8')).decode('utf-8')

def decode_cursor(cursor: str) -> Optional[Tuple[str, str]]:
    """
    Decodes a cursor into a (label, uri) tuple.
    Returns None if cursor is invalid.
    """
    if not cursor:
        return None
    
    try:
        decoded = base64.b64decode(cursor).decode('utf-8')
        parts = decoded.split('|')
        if len(parts) != 2:
            return None
        return parts[0], parts[1]
    except Exception:
        return None
