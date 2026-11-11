"""
Common Utilities for ETL Pipeline

Provides shared configuration, decorators, and utility functions.
"""
import hashlib
import os
import time
from re import sub
from dotenv import load_dotenv

load_dotenv()

# Ontology configuration
URI_ONTOLOGIA = os.getenv('URI_ONTOLOGIA', 'https://w3id.org/OntoExhibit#')

# Virtuoso configuration (replacing Stardog)
VIRTUOSO_URL = os.getenv('VIRTUOSO_URL', 'http://localhost:8890/sparql')
VIRTUOSO_GRAPH = os.getenv('VIRTUOSO_GRAPH_URI', 'http://localhost:8890/DAV/home/dba/rdf_sink')

# Special fields that need custom handling
SPECIALS = ['fuenteInformacion', 'institucionColeccionista', 'personaColeccionista']


def mide_tiempo(funcion):
    """Timing decorator that prints execution time."""
    def funcion_medida(*args, **kwargs):
        inicio = time.time()
        c = funcion(*args, **kwargs)
        print(f'Function "{funcion.__name__}" completed in {round(time.time() - inicio, 2)} seconds')
        return c
    return funcion_medida


def camel_case(s: str) -> str:
    """Convert string to camelCase."""
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]])


def normalizar(s: str) -> str:
    """Normalize Spanish characters and special characters for URIs."""
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
        ('º', ""),
        (':', "")
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s


def pascal_case_to_camel_case(string: str) -> str:
    """Convert PascalCase or snake_case to camelCase."""
    string = string.replace('_', ' ')
    string = camel_case(normalizar(string))
    return string


def hash_sha256(data: str) -> str:
    """Generate deterministic SHA256 hash for URI generation."""
    try:
        return hashlib.sha256(data.encode()).hexdigest()
    except Exception:
        print(f"Error calculating hash for: {data}")
        return ""


def normalize_name(name: str) -> str:
    """Normalize a name for consistent URI generation.
    
    Applies strip, collapses multiple whitespace, and title-cases
    so that 'pablo picasso', 'PABLO PICASSO', and ' Pablo  Picasso '
    all produce the same hash input.
    """
    if not name:
        return ""
    return sub(r'\s+', ' ', name.strip()).title()


def desglozarJSON(diccionario: dict, num_param_dict: int) -> dict:
    """Parse SPARQL JSON results into a simpler format."""
    result = {}
    data = []

    if num_param_dict == 2:
        for elem in diccionario['results']['bindings']:
            predicado = str(elem['p']['value'])
            objeto = str(elem['o']['value'])

            if '#label' in predicado:
                predicado = 'label'
            elif '#type' in predicado:
                predicado = 'tipo'
            else:
                predicado = predicado.replace(URI_ONTOLOGIA, '')

            if predicado in result.keys():
                if isinstance(result.get(predicado), list):
                    lista = list(result.get(predicado))
                    lista.append(objeto)
                else:
                    lista = [result.get(predicado), objeto]
                result[predicado] = lista
            else:
                result[predicado] = objeto
        data.append(result)

    elif num_param_dict == 1:
        for elem in diccionario['results']['bindings']:
            temp_dict = {}
            uri = str(elem['subject']['value'])
            label = str(elem['label']['value'])
            temp_dict['label'] = label
            temp_dict['uri'] = uri
            data.append(temp_dict)

    return {'data': data}


def generar_nuevo_json(diccionario: dict) -> dict:
    """Generate a new JSON structure from SPARQL results."""
    data = []
    
    for individuo in list(diccionario):
        individuo = dict(individuo)
        individuo_generado = {
            'label': individuo['label']['value'],
            'uri': individuo['uri']['value']
        }
        data.append(individuo_generado)
    
    return {'data': data}
