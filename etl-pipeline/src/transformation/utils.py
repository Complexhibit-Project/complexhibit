"""
Transformation Utilities

Common utility functions used across entity transformers.
"""
import datetime
import hashlib
from sqlite3 import Cursor
from urllib.parse import urlparse

import pandas as pd


# Date validation counters
_date_stats = {
    'total': 0,
    'success': 0,
    'fail': 0
}


def hash_sha256(data) -> str:
    """Generate deterministic SHA256 hash for URI generation."""
    # Handle various input types
    if data is None:
        data = ''
    elif not isinstance(data, str):
        data = str(data)
    return hashlib.sha256(data.encode()).hexdigest()


def dataframe_from_cursor(cursor: Cursor) -> pd.DataFrame:
    """Convert SQL query results to a pandas DataFrame."""
    rows = cursor.fetchall()
    if not rows:
        return pd.DataFrame()
    
    df = pd.DataFrame(rows)
    field_names = [col[0] for col in cursor.description]
    df.columns = field_names
    return df


def validar_fecha(value) -> datetime.date | None:
    """
    Validate and parse a date string in YYYY-MM-DD format.
    
    Returns None for null dates (0001-01-01) or invalid dates.
    Handles various input types (str, float, int, None).
    """
    # Handle None or empty values
    if value is None:
        return None
    
    # Convert to string and handle NaN/float values
    if isinstance(value, float):
        if pd.isna(value):
            return None
        value = str(value)
    elif not isinstance(value, str):
        value = str(value)
    
    # Strip whitespace
    value = value.strip()
    
    if not value or value == '0001-01-01' or value.lower() == 'nan':
        return None
    
    _date_stats['total'] += 1
    
    try:
        # Handle date with time component
        if ' ' in value:
            value = value.split(' ')[0]
        date = datetime.datetime.strptime(value, '%Y-%m-%d').date()
        _date_stats['success'] += 1
        return date
    except ValueError:
        _date_stats['fail'] += 1
        return None


def procesar_coordenadas(coordenadas: str) -> tuple[str, str]:
    """
    Process coordinates string and return (latitude, longitude).
    
    Handles formats like "lat,lon" or "lat,lon,altitude".
    """
    parts = coordenadas.split(',')[:2]
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return '', ''


def is_valid_url(s: str) -> bool:
    """Return True if s looks like a http(s) URL with a netloc."""
    try:
        p = urlparse(s)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def is_valid_name(name) -> bool:
    """Check if a name is valid (not None, not empty, not 'sin determinar')."""
    if name is None:
        return False
    name_str = str(name)
    return (
        name_str != 'None' 
        and name_str.strip() != ''
        and 'sin determinar' not in name_str.lower()
    )


def obtener_primer_texto(cadena: str) -> str | None:
    """Get the first non-empty text segment from a semicolon-separated string."""
    if not cadena:
        return None
    for parte in cadena.split(';'):
        if parte.strip():
            return parte.strip()
    return None


def parse_lugar(lugar: str) -> tuple[str | None, str | None, str | None]:
    """
    Parse a semicolon-separated place string into (city, state, country).
    
    Example: "Madrid;Comunidad de Madrid;España" -> ("Madrid", "Comunidad de Madrid", "España")
    """
    if not lugar:
        return None, None, None
    
    partes = lugar.split(';')
    ciudad = partes[0].strip() if len(partes) >= 1 else None
    estado = partes[1].strip() if len(partes) >= 2 else None
    pais = partes[2].strip() if len(partes) >= 3 else None
    
    # Filter out 'desconocido'
    if ciudad and ciudad.lower() == 'desconocido':
        ciudad = None
    if estado and estado.lower() == 'desconocido':
        estado = None
    if pais and pais.lower() == 'desconocido':
        pais = None
    
    return ciudad, estado, pais


def is_approximate_date(date: datetime.date) -> bool:
    """
    Check if a date is approximate (Jan 1 or Dec 31).
    
    Dates on Jan 1 or Dec 31 are often used to indicate
    "sometime in that year" rather than exact dates.
    """
    return (
        (date.month == 1 and date.day == 1) or
        (date.month == 12 and date.day == 31)
    )


def get_date_stats() -> dict:
    """Get date parsing statistics."""
    total = _date_stats['total']
    if total == 0:
        return {'total': 0, 'success': 0, 'fail': 0, 'success_pct': 0, 'fail_pct': 0}
    
    return {
        'total': total,
        'success': _date_stats['success'],
        'fail': _date_stats['fail'],
        'success_pct': round(_date_stats['success'] * 100 / total, 1),
        'fail_pct': round(_date_stats['fail'] * 100 / total, 1)
    }


def reset_date_stats():
    """Reset date parsing counters."""
    _date_stats['total'] = 0
    _date_stats['success'] = 0
    _date_stats['fail'] = 0


# Banned list for filtering invalid data
BANNED_LIST = [
    "CASI",
    "COMPLETADA",
    "GaleríaInforme",
    "Cofradía",
    "Contemporánea",
    "REL",
    "NR",
]
