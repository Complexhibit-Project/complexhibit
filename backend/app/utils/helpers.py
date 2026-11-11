import datetime
import hashlib
import re
from typing import Optional
from urllib.parse import quote


def hash_sha256(data: str) -> Optional[str]:
    result = None
    try:
        result = hashlib.sha256(data.encode()).hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {data}: {e}")
    return result


def normalize_name(name: str) -> str:
    """Normalize a name for consistent URI generation.
    
    Applies strip, collapses multiple whitespace, and title-cases
    so that 'pablo picasso', 'PABLO PICASSO', and ' Pablo  Picasso '
    all produce the same hash input.
    """
    if not name:
        return ""
    return re.sub(r'\s+', ' ', name.strip()).title()


def validar_fecha(value: str) -> Optional[datetime.date]:
    """Parse date string in multiple formats: YYYY-MM-DD, DD/MM/YYYY, or just YYYY."""
    valid_date = None
    formats = [
        "%Y-%m-%d",    # ISO format (from HTML date inputs)
        "%d/%m/%Y",    # European format
        "%Y",          # Just year
    ]
    if value:
        value = value.strip()
        for fmt in formats:
            try:
                valid_date = datetime.datetime.strptime(value, fmt).date()
                break
            except ValueError:
                continue
        if not valid_date:
            print(f"Error transforming date {value}")
    return valid_date


def convertir_fecha(date: str) -> str:
    fecha_regex = r"^\d{2}/\d{2}/\d{4}$"
    if re.match(fecha_regex, date):
        # Convert dd/mm/yyyy to yyyy-mm-dd
        date = date[6:] + "-" + date[3:5] + "-" + date[:2]
    return date


def camel_case(s: str) -> str:
    s = re.sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return "".join([s[0].lower(), s[1:]])


def normalizar(s: str) -> str:
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("ñ", "nh"),
        (" ", "_"),
        ("(", ""),
        (")", ""),
        ("/", " "),
        ("º", ""),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s


def pascal_case_to_camel_case(string: str) -> str:
    string = string.replace("_", " ")
    string = camel_case(normalizar(string))
    return string


def generate_hashed_id() -> str:
    import sys
    from random import randint

    now = datetime.datetime.now()
    timestamp = datetime.datetime.timestamp(now)
    random_number = randint(0, sys.maxsize)
    random_number2 = randint(0, sys.maxsize)
    timestamp2 = datetime.datetime.timestamp(now)
    id_generated = hash_sha256(f"{timestamp}-{random_number}-{timestamp2}-{random_number2}")
    return id_generated
