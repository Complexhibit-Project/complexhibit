"""
Map router - Provides geolocated data for the interactive world map.
"""
import random
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import settings
from app.dependencies import get_sparql_client
from app.services.sparql_client import SparqlClient
from app.utils.parsers import parse_sparql_response
from app.services.queries.base import PREFIXES

router = APIRouter(prefix=f"{settings.DEPLOY_PATH}/map", tags=["map"])

# --- Queries ---

GET_EXHIBITIONS = f"""
    {PREFIXES}
    SELECT DISTINCT ?uri ?label ?lat ?long ?date_start ?date_end
    WHERE {{
        ?uri rdf:type <https://w3id.org/OntoExhibit#Exhibition> .
        ?uri <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat .
        ?uri <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?long .
        
        OPTIONAL {{ ?uri rdfs:label ?direct_label }}
        OPTIONAL {{ 
            ?uri <https://w3id.org/OntoExhibit#hasTitle> ?title_node . 
            ?title_node rdfs:label ?title_label 
        }}
        BIND(COALESCE(?title_label, ?direct_label, "Untitled Exhibition") AS ?label)
        
        OPTIONAL {{
            ?uri <https://w3id.org/OntoExhibit#hasOpening> ?opening .
            ?opening <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_opening .
            ?time_opening rdfs:label ?date_start
        }}
        OPTIONAL {{
            ?uri <https://w3id.org/OntoExhibit#hasClosing> ?closing .
            ?closing <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_closing .
            ?time_closing rdfs:label ?date_end
        }}
    }}
"""

GET_INSTITUTIONS = f"""
    {PREFIXES}
    SELECT DISTINCT ?uri ?label ?lat ?long
    WHERE {{
        ?uri rdf:type <https://w3id.org/OntoExhibit#Institution> .
        ?uri <https://w3id.org/OntoExhibit#hasHeadquarters> ?hq .
        ?hq <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat .
        ?hq <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?long .
        
        ?uri rdfs:label ?label .
    }}
"""

GET_PERSONS = f"""
    {PREFIXES}
    SELECT DISTINCT ?uri ?label ?lat ?long ?date_start ?date_end ?loc_type
    WHERE {{
        # Relaxed Type Check: Removed completely to allow any entity with location properties
        # {{
        #     ?uri rdf:type <https://w3id.org/OntoExhibit#Human_Actant> .
        # }} UNION {{
        #     ?uri rdf:type <https://w3id.org/OntoExhibit#Person> .
        # }} UNION {{
        #     ?uri rdf:type <https://w3id.org/OntoExhibit#Group> .
        # }}

        # Get Locations (UNION to get multiple per person)
        {{
            ?uri <https://w3id.org/OntoExhibit#hasResidency> ?place .
            BIND("residence" AS ?loc_type)
        }} UNION {{
            ?uri <https://w3id.org/OntoExhibit#hasPlaceOfBirth> ?place .
            BIND("birth" AS ?loc_type)
        }} UNION {{ 
            ?uri <https://w3id.org/OntoExhibit#hasFoundation> ?evt_f . 
            ?evt_f <https://w3id.org/OntoExhibit#hasPlaceOfFoundation> ?place .
            BIND("birth" AS ?loc_type)
        }} UNION {{
            ?uri <https://w3id.org/OntoExhibit#hasBirth> ?evt_b .
            ?evt_b <https://w3id.org/OntoExhibit#hasPlaceOfBirth> ?place .
            BIND("birth" AS ?loc_type)
        }}
        
        ?place <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat .
        ?place <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?long .
        
        ?uri rdfs:label ?label .
        
        # Birth / Foundation Date
        OPTIONAL {{
            {{
                ?uri <https://w3id.org/OntoExhibit#hasBirth> ?start_event .
            }} UNION {{
                ?uri <https://w3id.org/OntoExhibit#hasFoundation> ?start_event .
            }}
            ?start_event <https://w3id.org/OntoExhibit#hasTimeSpan> ?start_time .
            ?start_time rdfs:label ?date_start
        }}
        
        # Death / Dissolution Date
        OPTIONAL {{
            {{
                ?uri <https://w3id.org/OntoExhibit#hasDeath> ?end_event .
            }} UNION {{
                ?uri <https://w3id.org/OntoExhibit#hasDissolution> ?end_event .
            }}
            ?end_event <https://w3id.org/OntoExhibit#hasTimeSpan> ?end_time .
            ?end_time rdfs:label ?date_end
        }}
    }}
"""

GET_ARTWORKS = f"""
    {PREFIXES}
    SELECT DISTINCT ?uri ?label ?lat ?long ?date_start ?date_end
    WHERE {{
        ?uri rdf:type <https://w3id.org/OntoExhibit#Work_Manifestation> .
        
        # Find owner
        ?uri <https://w3id.org/OntoExhibit#hasOwner> ?role .
        ?owner <https://w3id.org/OntoExhibit#hasRole> ?role .
        
        # Get owner's location (Inst HQ or Person Residence)
        {{
            ?owner <https://w3id.org/OntoExhibit#hasHeadquarters> ?loc .
        }} UNION {{
            ?owner <https://w3id.org/OntoExhibit#hasResidency> ?loc .
            # ?loc rdf:type <https://w3id.org/OntoExhibit#Place_Of_Residence> . REMOVED STRICT CHECK
        }}
        
        ?loc <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat .
        ?loc <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?long .
        
        OPTIONAL {{ ?uri rdfs:label ?direct_label }}
        OPTIONAL {{ 
            ?uri <https://w3id.org/OntoExhibit#hasTitle> ?title_node . 
            ?title_node rdfs:label ?title_label 
        }}
        BIND(COALESCE(?title_label, ?direct_label, "Untitled Artwork") AS ?label)

        # Artwork dates (Production)
        OPTIONAL {{
             ?uri <https://w3id.org/OntoExhibit#hasProduction> ?prod .
             OPTIONAL {{
                ?prod <https://w3id.org/OntoExhibit#hasTimeSpan> ?tr_s .
                ?tr_s <https://w3id.org/OntoExhibit#hasStartingDate> ?start_date_node .
                ?start_date_node rdfs:label ?date_start .
             }}
             OPTIONAL {{
                ?prod <https://w3id.org/OntoExhibit#hasTimeSpan> ?tr_e .
                ?tr_e <https://w3id.org/OntoExhibit#hasEndingDate> ?end_date_node .
                ?end_date_node rdfs:label ?date_end .
             }}
        }}
    }}
"""

def process_entities(data: List[dict], entity_type: str) -> List[dict]:
    result = []
    for item in data:
        uri = item.get("uri", "")
        # Extract ID from URI (last part after / or #)
        id_part = uri.split("/")[-1] if "/" in uri else uri.split("#")[-1]
        
        # Check for location type (residence/birth) to generate unique ID for multiple points
        loc_type = item.get("loc_type")
        if loc_type:
            id_part = f"{id_part}_{loc_type}"

        lat = item.get("lat")
        long = item.get("long")
        
        if not lat or not long:
            continue
            
        try:
            # Jitter: Add small random noise to coordinates to prevent exact overlaps
            # +/- 0.0001 degrees is roughly 11 meters
            jitter_amount = 0.0001
            lat_float = float(lat) + random.uniform(-jitter_amount, jitter_amount)
            long_float = float(long) + random.uniform(-jitter_amount, jitter_amount)
        except (ValueError, TypeError):
            continue
        
        result.append({
            "id": id_part,
            "uri": uri,
            "type": entity_type,
            "label": item.get("label", f"Unknown {entity_type}"),
            "lat": lat_float,
            "long": long_float,
            "date_start": item.get("date_start"),
            "date_end": item.get("date_end")
        })
    return result

@router.get("/all")
async def get_all_geolocated_entities(
    types: Optional[List[str]] = Query(None),
    client: SparqlClient = Depends(get_sparql_client)
):
    """
    Get geolocated entities.
    Optional 'types' valid values: 'exhibition', 'institution', 'person', 'artwork'.
    If not provided, returns all.
    """
    try:
        if types is None:
            types = ['exhibition', 'institution', 'person', 'artwork']
        
        # Helper to run query safely
        async def fetch_type(etype, query):
            resp = await client.query(query)
            data = parse_sparql_response(resp)
            return process_entities(data, etype)

        tasks = []
        if 'exhibition' in types:
            tasks.append(fetch_type('exhibition', GET_EXHIBITIONS))
        if 'institution' in types:
            tasks.append(fetch_type('institution', GET_INSTITUTIONS))
        if 'person' in types:
            tasks.append(fetch_type('person', GET_PERSONS))
        if 'artwork' in types:
            tasks.append(fetch_type('artwork', GET_ARTWORKS))
            
        if not tasks:
            return {"data": [], "count": 0}

        results = await asyncio.gather(*tasks)
        
        # Flatten list
        all_entities = []
        for res in results:
            all_entities.extend(res)
        
        return {"data": all_entities, "count": len(all_entities)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

GET_MAP_META = f"""
    {PREFIXES}
    SELECT (MIN(?min_date) as ?min_year) (MAX(?max_date) as ?max_year)
    WHERE {{
        {{
            SELECT (MIN(?date) as ?min_date) (MAX(?date) as ?max_date)
            WHERE {{
                {{
                    ?s <https://w3id.org/OntoExhibit#hasTimeSpan> ?ts .
                    ?ts rdfs:label ?date .
                }} UNION {{
                     # Fallback for direct dates if any
                    ?s <https://w3id.org/OntoExhibit#date> ?date .
                }}
                FILTER (REGEX(?date, "^\\\\d{{4}}"))
            }}
        }}
    }}
"""

@router.get("/meta")
async def get_map_metadata(client: SparqlClient = Depends(get_sparql_client)):
    """
    Get metadata for the map, specifically the global min and max years for the time slider.
    """
    try:
        # Optimized query to just get min/max years from likely candidates
        # We focus on the range that actually matters for the entities shown
        query = f"""
            {PREFIXES}
            SELECT (MIN(?year) as ?min_year) (MAX(?year) as ?max_year)
            WHERE {{
                {{
                    SELECT ?val WHERE {{
                        ?s <https://w3id.org/OntoExhibit#hasTimeSpan> ?ts .
                        ?ts rdfs:label ?val .
                    }} LIMIT 10000
                }}
                BIND(STR(?val) AS ?date_str)
                BIND(STRDT(SUBSTR(?date_str, 1, 4), xsd:integer) AS ?year)
                FILTER(?year > 1000 && ?year < 3000) 
            }}
        """
        # Note: The above generic query is a bit heavy. Let's try a lighter path specific to our entities.
        # Actually, let's just grab the min/max from the main entities we display.
        
        query = f"""
            {PREFIXES}
            SELECT (MIN(?year) as ?min_year) (MAX(?year) as ?max_year)
            WHERE {{
                {{
                    # Exhibition dates
                    ?uri rdf:type <https://w3id.org/OntoExhibit#Exhibition> .
                    ?uri <https://w3id.org/OntoExhibit#hasOpening>|<https://w3id.org/OntoExhibit#hasClosing> ?evt .
                    ?evt <https://w3id.org/OntoExhibit#hasTimeSpan> ?ts .
                    ?ts rdfs:label ?label .
                    BIND(xsd:integer(SUBSTR(STR(?label), 1, 4)) AS ?year)
                }} UNION {{
                    # Person dates (birth/death)
                    {{ ?p rdf:type <https://w3id.org/OntoExhibit#Person> }} UNION {{ ?p rdf:type <https://w3id.org/OntoExhibit#Group> }}
                    ?p <https://w3id.org/OntoExhibit#hasBirth>|<https://w3id.org/OntoExhibit#hasDeath>|<https://w3id.org/OntoExhibit#hasFoundation>|<https://w3id.org/OntoExhibit#hasDissolution> ?evt .
                    ?evt <https://w3id.org/OntoExhibit#hasTimeSpan> ?ts .
                    ?ts rdfs:label ?label .
                    BIND(xsd:integer(SUBSTR(STR(?label), 1, 4)) AS ?year)
                }} UNION {{
                     # Artwork dates
                     ?w rdf:type <https://w3id.org/OntoExhibit#Work_Manifestation> .
                     ?w <https://w3id.org/OntoExhibit#hasProduction> ?prod .
                     ?prod <https://w3id.org/OntoExhibit#hasTimeSpan> ?ts .
                     ?ts <https://w3id.org/OntoExhibit#hasStartingDate>|<https://w3id.org/OntoExhibit#hasEndingDate> ?d .
                     ?d rdfs:label ?label .
                     BIND(xsd:integer(SUBSTR(STR(?label), 1, 4)) AS ?year)
                }}
                FILTER(?year > 1000 && ?year <= year(now()))
            }}
        """
        
        resp = await client.query(query)
        data = parse_sparql_response(resp)
        
        if data:
            return {
                "min_year": int(data[0].get("min_year", 1900)),
                "max_year": int(data[0].get("max_year", 2025))
            }
        return {"min_year": 1900, "max_year": 2025}
        
    except Exception as e:
        print(f"Error fetching map metadata: {e}")
        # Return safe defaults if DB fails
        return {"min_year": 1900, "max_year": 2025}
