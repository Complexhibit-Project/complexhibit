"""
Place Normalization Module

Normalizes place names in the database with improved title casing,
Unicode normalization, and common abbreviation handling.
"""
import sqlite3
import unicodedata
import re


# Common country/place normalization mapping
PLACE_NORMALIZATIONS = {
    'Eeuu': 'Estados Unidos',
    'Usa': 'Estados Unidos',
    'United States': 'Estados Unidos',
    'U.s.a.': 'Estados Unidos',
    'Uk': 'Reino Unido',
    'United Kingdom': 'Reino Unido',
    'Nyc': 'Nueva York',
    'New York': 'Nueva York',
    'La': 'Los Ángeles',
    'Los Angeles': 'Los Ángeles',
    'España': 'España',
    'Spain': 'España',
}


def levenshtein_similarity(s1: str, s2: str) -> float:
    """Calculate Levenshtein similarity between two strings."""
    try:
        import Levenshtein
        if s1 is None or s2 is None:
            return 0.0
        maxlen = max(len(s1), len(s2))
        if maxlen == 0:
            return 1.0
        distance = Levenshtein.distance(s1, s2)
        return 1.0 - distance / maxlen
    except ImportError:
        # Fallback if Levenshtein not available
        return 1.0 if s1 == s2 else 0.0


def normalizar_lugar(lugar_completo: str) -> str:
    """
    Normalize a semicolon-separated place string.
    
    Improvements over original:
    - Unicode normalization (NFC)
    - Strips extra whitespace
    - Applies title case
    - Maps common abbreviations
    """
    if not lugar_completo:
        return lugar_completo
    
    # Unicode normalization
    lugar_completo = unicodedata.normalize('NFC', lugar_completo)
    
    # Split by semicolon
    lugares = lugar_completo.split(';')
    lugares_normalizados = []
    
    for lugar in lugares:
        # Strip and collapse multiple spaces
        lugar = ' '.join(lugar.split())
        
        if not lugar:
            continue
            
        # Apply title case
        lugar_normalizado = lugar.title()
        
        # Apply known normalizations
        lugar_normalizado = PLACE_NORMALIZATIONS.get(lugar_normalizado, lugar_normalizado)
        
        lugares_normalizados.append(lugar_normalizado)
    
    # Rejoin with proper separator
    return "; ".join(lugares_normalizados)


def normalize_all_places(db_path: str = 'pathwise.db'):
    """Normalize all place fields in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Standard tables with common field patterns
    consultas = [
        'SELECT id, `lugar de origen` FROM PERSONA WHERE `lugar de origen` IS NOT NULL AND `lugar de origen` != ""',
        'SELECT id, `lugar donde se celebra` FROM EXPOSICION WHERE `lugar donde se celebra` IS NOT NULL AND `lugar donde se celebra` != ""',
        'SELECT id, `lugar de la sede` FROM INSTITUCION WHERE `lugar de la sede` IS NOT NULL AND `lugar de la sede` != ""',
        'SELECT id, `lugar de la sede` FROM EMPRESA WHERE `lugar de la sede` IS NOT NULL AND `lugar de la sede` != ""',
    ]
    
    total_updated = 0
    
    # Process standard tables
    for consulta in consultas:
        cursor.execute(consulta)
        column_name = cursor.description[1][0]
        registros = cursor.fetchall()
        nombre_tabla = consulta.split("FROM")[1].strip().split()[0]
        
        for registro in registros:
            id_registro = registro[0]
            lugar = registro[1]
            lugar_normalizado = normalizar_lugar(lugar)
            
            if lugar != lugar_normalizado:
                cursor.execute(
                    f"UPDATE {nombre_tabla} SET `{column_name}` = ? WHERE id = ?",
                    (lugar_normalizado, id_registro)
                )
                total_updated += 1
    
    # Process OBRA DE ARTE separately (table name with spaces)
    consulta = 'SELECT id, `lugar de creación de la obra` FROM `OBRA DE ARTE` WHERE `lugar de creación de la obra` IS NOT NULL AND `lugar de creación de la obra` != ""'
    cursor.execute(consulta)
    column_name = cursor.description[1][0]
    registros = cursor.fetchall()
    
    for registro in registros:
        id_registro = registro[0]
        lugar = registro[1]
        lugar_normalizado = normalizar_lugar(lugar)
        
        if lugar != lugar_normalizado:
            cursor.execute(
                f"UPDATE `OBRA DE ARTE` SET `{column_name}` = ? WHERE id = ?",
                (lugar_normalizado, id_registro)
            )
            total_updated += 1
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"Normalized {total_updated} place fields")
    return total_updated


# Run when imported as module or executed directly
if __name__ == '__main__':
    normalize_all_places()
else:
    # Auto-run when imported
    normalize_all_places()
