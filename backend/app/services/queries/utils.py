from urllib.parse import quote

from rdflib import RDF, RDFS

from app.core.config import settings
from app.services.queries.base import OBJECT_PROPERTIES, URI_ONTOLOGIA, uri_ontologia
from app.utils.helpers import convertir_fecha, hash_sha256, normalize_name, pascal_case_to_camel_case


def escape_sparql_string(value: str) -> str:
    """
    Escape special characters for SPARQL string literals.
    
    According to SPARQL spec, inside a string literal delimited by double quotes:
    - Backslash (\) must be escaped as \\
    - Double quote (") must be escaped as \"
    - Newline, carriage return, tab should also be escaped
    """
    if not value:
        return ""
    # Order matters: escape backslashes first, then quotes
    result = value.replace('\\', '\\\\')  # Escape backslashes
    result = result.replace('"', '\\"')    # Escape double quotes
    result = result.replace('\n', '\\n')   # Escape newlines
    result = result.replace('\r', '\\r')   # Escape carriage returns
    result = result.replace('\t', '\\t')   # Escape tabs
    return result

def generate_sentences(arg, sujeto) -> list:
    sentences = []
    # arg is a Pydantic model, so we can use .dict() or iterate over fields
    # The original code iterates over arg which implies it might be a list of tuples or dict items?
    # In original code: for field in arg: key = field[0], value = field[1]
    # So it iterates over model fields.

    for key, value in arg:
        key = pascal_case_to_camel_case(key)

        # Property Mapping to Ontology
        PROPERTY_MAPPING = {
            "organiza": "hasOrganizer",
            "exposicionPatrocinadaPor": "hasSponsor",
            "comisario": "hasCurator",
            "lugarCelebracion": "takesPlaceAt", # Assuming data property usage or legacy compatibility
            "tieneDispositivoDeInscripcion": "hasMediationDispositif",
            # Add others if needed
        }
        if key in PROPERTY_MAPPING:
            key = PROPERTY_MAPPING[key]

        if "id" != key and "type" not in key and key not in OBJECT_PROPERTIES and value:
            if isinstance(value, list):
                for v in value:
                    if isinstance(v, str):
                        sentence = (
                            f"{sujeto} <{URI_ONTOLOGIA}{key}> "
                            f'"{v.capitalize()}"^^<http://www.w3.org/2001/XMLSchema#string> .'
                        )
                        sentences.append(sentence)
            else:
                if "name" in key:
                    sentence = (
                        f"{sujeto} <{URI_ONTOLOGIA}{key}> "
                        f'"{value.title()}"^^<http://www.w3.org/2001/XMLSchema#string> .'
                    )
                    if "name" == key:
                        sentence = (
                            f"{sentence}\n\t\t{sujeto} <{RDFS.label}> "
                            f'"{value.title()}"^^<http://www.w3.org/2001/XMLSchema#string> .'
                        )
                elif "date" in key or "Date" in key:
                    value = convertir_fecha(value)
                    sentence = f'{sujeto} <{URI_ONTOLOGIA}{key}> "{value}"^^<http://www.w3.org/2001/XMLSchema#date> .'
                elif "lugarCelebracion" in key:
                    sentence = f'{sujeto} <{URI_ONTOLOGIA}{key}> "{value}"^^<http://www.w3.org/2001/XMLSchema#string> .'
                else:
                    if "website" == key:
                        sentence = (
                            f"{sujeto} <{URI_ONTOLOGIA}{key}> "
                            f'"{value}"^^<http://www.w3.org/2001/XMLSchema#anyURI> .'
                        )
                    elif key in ["flyer", "poster", "review", "pressrelease", "catalogue"]:
                        sentence = (
                            f"{sujeto} <{URI_ONTOLOGIA}{key}> "
                            f'"{value}"^^<http://www.w3.org/2001/XMLSchema#string> .'
                        )
                    else:
                        if isinstance(value, str):
                            sentence = (
                                f"{sujeto} <{URI_ONTOLOGIA}{key}> "
                                f'"{value.capitalize()}"^^<http://www.w3.org/2001/XMLSchema#string> .'
                            )
                        else:
                            # Fallback for non-string values if any
                            sentence = (
                                f"{sujeto} <{URI_ONTOLOGIA}{key}> "
                                f'"{str(value)}"^^<http://www.w3.org/2001/XMLSchema#string> .'
                            )
                sentences.append(sentence)

    return sentences


def add_any_type(arg, type_arg):
    from app.models.domain import ObraDeArte, Persona

    tipo_sujeto = ""

    if isinstance(arg, Persona):
        tipo_sujeto = "human_actant"
    elif isinstance(arg, ObraDeArte):
        tipo_sujeto = "work_manifestation"
    else:
        # Fallback or default
        tipo_sujeto = type_arg.lower().replace(" ", "_") if type_arg else "thing"

    normalized = normalize_name(arg.name) if hasattr(arg, "name") and arg.name else ""
    if hasattr(arg, "type") and arg.type:
        # If type is a list, take the first one or join? Original code uses arg.type directly in string
        # Assuming arg.type is a string here based on usage
        if isinstance(arg.type, list):
            t = arg.type[0]
        else:
            t = arg.type
        data_to_hash = f"{normalized} - {t}"
    else:
        data_to_hash = f"{normalized} - {tipo_sujeto.replace('_', ' ')}"

    sujeto = f"{uri_ontologia}{quote(tipo_sujeto)}/{hash_sha256(data_to_hash)}>"

    sentences = generate_sentences(arg, sujeto)

    triples = []
    triples.extend(sentences)

    if "Group" == type_arg.capitalize():
        triples.append(
            f"{sujeto} <{RDF.type}> <https://cidoc-crm.org/cidoc-crm/7.1.1/E74_Group> ."
        )
    elif "Individual" == type_arg.capitalize():
        triples.append(
            f"{sujeto} <{RDF.type}> <https://cidoc-crm.org/cidoc-crm/7.1.1/E21_Person> ."
        )
    else:
        # Handle complex types split by underscore
        tipo_sujeto_parts = tipo_sujeto.split("_")
        tipo_parts = [palabra.strip().capitalize() for palabra in tipo_sujeto_parts]
        tipo = "_".join(tipo_parts)

        triples.append(f"{sujeto} <{RDF.type}> <{URI_ONTOLOGIA}{tipo}> .")

    return triples
