from urllib.parse import quote

from rdflib import RDF, RDFS

from app.core.config import settings
from app.models.domain import ObraDeArte
from app.services.queries.base import PREFIXES, URI_ONTOLOGIA, uri_ontologia
from app.services.queries.utils import add_any_type, escape_sparql_string
from app.utils.helpers import hash_sha256, normalize_name, validar_fecha


class ArtworkQueries:
    COUNT_OBRAS = f"""
        {PREFIXES}
        SELECT (count(distinct ?uri) as ?count) WHERE 
        {{   
            ?uri rdf:type <https://w3id.org/OntoExhibit#Work_Manifestation>
        }}
    """

    @staticmethod
    def get_obras_ids(limit: int, last_label: str = None, last_uri: str = None, text_search: str = None, 
                      author_name: str = None, type_filter: str = None, start_date: str = None, owner: str = None,
                      topic: str = None, exhibition: str = None,
                      author_uri: str = None, owner_uri: str = None, exhibition_uri: str = None,
                      production_place: str = None) -> str:
        
        filters = []
        inner_joins = []
        
        # Always need label for sorting
        inner_joins.append("?uri rdfs:label ?inner_label .")
        
        if text_search:
            e_text = escape_sparql_string(text_search)
            filters.append(f'(regex(?inner_label, "{e_text}", "i") || regex(?inner_author, "{e_text}", "i") || regex(?inner_type, "{e_text}", "i"))')
            inner_joins.append("OPTIONAL { ?uri <https://w3id.org/OntoExhibit#type> ?inner_type . }")
            inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasProduction> ?prod_ts .
                    OPTIONAL { ?prod_ts <https://w3id.org/OntoExhibit#hasProductionAuthor> ?uri_author_ts . ?uri_author_ts rdfs:label ?inner_author . }
                }
            """)
        
        if author_name and not text_search:
             filters.append(f'regex(?inner_author, "{escape_sparql_string(author_name)}", "i")')
             inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasProduction> ?prod_an .
                    OPTIONAL { ?prod_an <https://w3id.org/OntoExhibit#hasProductionAuthor> ?uri_author_an . ?uri_author_an rdfs:label ?inner_author . }
                }
            """)

        if type_filter:
             filters.append(f'regex(?inner_type, "{escape_sparql_string(type_filter)}", "i")')
             if not text_search:
                 inner_joins.append("OPTIONAL { ?uri <https://w3id.org/OntoExhibit#type> ?inner_type . }")

        if start_date:
             filters.append(f'regex(str(?inner_label_starting_date), "{escape_sparql_string(start_date)}", "i")')
             inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasProduction> ?prod_sd .
                    OPTIONAL { ?prod_sd <https://w3id.org/OntoExhibit#hasTimeSpan> ?tr_sd . ?tr_sd <https://w3id.org/OntoExhibit#hasStartingDate> ?date_sd . ?date_sd rdfs:label ?inner_label_starting_date . }
                }
             """)

        if owner:
             filters.append(f'regex(?inner_owner, "{escape_sparql_string(owner)}", "i")')
             inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasOwner> ?uri_owner_ow .
                    ?uri_owner_ow <https://w3id.org/OntoExhibit#isRoleOf> ?uri_owner_role_ow .
                    ?uri_owner_role_ow rdfs:label ?inner_owner
                }
             """)

        if topic:
             filters.append(f'regex(?inner_topic, "{escape_sparql_string(topic)}", "i")')
             inner_joins.append("""
                OPTIONAL { ?uri <https://w3id.org/OntoExhibit#hasTheme> ?uri_topic_tp . ?uri_topic_tp rdfs:label ?inner_topic }
             """)

        if exhibition:
             filters.append(f'regex(?inner_exhibition, "{escape_sparql_string(exhibition)}", "i")')
             inner_joins.append("""
                OPTIONAL { ?uri <https://w3id.org/OntoExhibit#isDisplayedAt> ?uri_exhibition_ex . ?uri_exhibition_ex rdfs:label ?inner_exhibition }
             """)

        if production_place:
             filters.append(f'regex(?inner_production_place, "{escape_sparql_string(production_place)}", "i")')
             inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasProduction> ?prod_pp .
                    ?prod_pp <https://w3id.org/OntoExhibit#takesPlaceAt> ?place_pp .
                    ?place_pp rdfs:label ?inner_production_place .
                }
             """)

        if author_uri:
             inner_joins.append(f"""
                ?uri <https://w3id.org/OntoExhibit#hasProduction> ?prod_au .
                ?prod_au <https://w3id.org/OntoExhibit#hasProductionAuthor> ?author_role_au .
                <{author_uri}> <https://w3id.org/OntoExhibit#hasRole> ?author_role_au .
             """)

        if owner_uri:
             inner_joins.append(f"""
                ?uri <https://w3id.org/OntoExhibit#hasOwner> ?owner_role_ow .
                <{owner_uri}> <https://w3id.org/OntoExhibit#hasRole> ?owner_role_ow .
             """)

        if exhibition_uri:
             inner_joins.append(f"""
                ?uri <https://w3id.org/OntoExhibit#isDisplayedAt> <{exhibition_uri}> .
             """)

        filter_clause = f"FILTER ({' && '.join(filters)})" if filters else ""
        
        pagination_filter = ""
        if last_label and last_uri:
            # Use URI-only comparison which is safe from special character issues
            pagination_filter = f"""
                FILTER (?uri > <{last_uri}>)
            """

        inner_joins_str = "\n".join(inner_joins)

        return f"""
            {PREFIXES}
            SELECT DISTINCT ?uri ?inner_label
            WHERE 
            {{
                ?uri rdf:type <https://w3id.org/OntoExhibit#Work_Manifestation> .
                {inner_joins_str}
                {filter_clause}
                {pagination_filter}
            }} 
            ORDER BY ?uri
            LIMIT {limit}
        """

    @staticmethod
    def get_obras_details(uris: list[str]) -> str:
        if not uris:
            return ""
        
        uris_str = " ".join([f"<{u}>" for u in uris])
        
        return f"""
            {PREFIXES}
            SELECT ?uri (SAMPLE(COALESCE(?inner_title_label, ?inner_label, "")) as ?label) 
                   (GROUP_CONCAT(DISTINCT ?inner_type; separator="|") as ?type)
                   (SAMPLE(?inner_apelation) as ?apelation)
                   (SAMPLE(?inner_label_starting_date) as ?label_starting_date)
                   (SAMPLE(?inner_label_ending_date) as ?label_ending_date)
                   (SAMPLE(?inner_production_place) as ?production_place)
                   (GROUP_CONCAT(DISTINCT CONCAT(?inner_author, ":::", STR(?uri_author)); separator="|") as ?authors)
                   (GROUP_CONCAT(DISTINCT CONCAT(?inner_owner, ":::", STR(?uri_owner_role)); separator="|") as ?owners)
                   (GROUP_CONCAT(DISTINCT ?inner_topic; separator="|") as ?topic)
                   (GROUP_CONCAT(DISTINCT CONCAT(?inner_exhibition, ":::", STR(?uri_exhibition)); separator="|") as ?exhibitions)
            WHERE 
            {{
                VALUES ?uri {{ {uris_str} }}
                
                OPTIONAL {{ ?uri rdfs:label ?inner_label . }}
                OPTIONAL {{ 
                    ?uri <https://w3id.org/OntoExhibit#hasTitle> ?title_entity .
                    ?title_entity rdfs:label ?inner_title_label .
                }}

                OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#type> ?inner_type . }}
                OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#apelation> ?inner_apelation }}

                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#hasOwner> ?uri_owner .
                    ?uri_owner_role <https://w3id.org/OntoExhibit#hasRole> ?uri_owner .
                    ?uri_owner_role rdfs:label ?inner_owner
                }}
                OPTIONAL {{
                     ?uri <https://w3id.org/OntoExhibit#hasProduction> ?prod .
                     OPTIONAL {{
                        ?prod <https://w3id.org/OntoExhibit#hasProductionAuthor> ?author_role .
                        ?uri_author <https://w3id.org/OntoExhibit#hasRole> ?author_role .
                        ?uri_author rdfs:label ?inner_author .
                     }}
                     OPTIONAL {{
                        ?prod <https://w3id.org/OntoExhibit#hasTimeSpan> ?tr .
                        ?tr <https://w3id.org/OntoExhibit#hasStartingDate> ?start_date .
                        ?start_date rdfs:label ?inner_label_starting_date .
                     }}
                     OPTIONAL {{
                        ?prod <https://w3id.org/OntoExhibit#hasTimeSpan> ?tr .
                        ?tr <https://w3id.org/OntoExhibit#hasEndingDate> ?end_date .
                        ?end_date rdfs:label ?inner_label_ending_date .
                     }}
                     OPTIONAL {{
                        ?prod <https://w3id.org/OntoExhibit#takesPlaceAt> ?place_uri .
                        ?place_uri rdfs:label ?inner_production_place .
                     }}
                }}
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#isDisplayedAt> ?uri_exhibition .
                    ?uri_exhibition rdfs:label ?inner_exhibition
                }}
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#hasTheme> ?uri_topic .
                    ?uri_topic rdfs:label ?inner_topic
                }}
            }} 
            GROUP BY ?uri
        """

    @staticmethod
    def add_obra(obra: ObraDeArte) -> str:
        normalized = normalize_name(obra.name)
        if obra.type:
            if isinstance(obra.type, list):
                type_str = obra.type[0]
            else:
                type_str = obra.type
            data_to_hash = f"{normalized} - {type_str}"
        else:
            data_to_hash = f"{normalized} - work manifestation"

        sujeto = f'{uri_ontologia}{quote("work_manifestation")}/{hash_sha256(data_to_hash)}'
        sujeto_uri = f"<https://w3id.org/OntoExhibit#{quote('work_manifestation')}/{hash_sha256(data_to_hash)}>"

        triples = []
        
        # RDF type
        triples.append(f"<{sujeto}> <{RDF.type}> <https://w3id.org/OntoExhibit#Work_Manifestation> .")
        
        # Name/label
        triples.append(f'<{sujeto}> <{RDFS.label}> "{escape_sparql_string(obra.name.title())}"^^<http://www.w3.org/2001/XMLSchema#string> .')

        # Title entity
        uri_title = f"{uri_ontologia}title/{hash_sha256(obra.name)}"
        triples.append(f"<{uri_title}> <{RDF.type}> <{uri_ontologia}Title> .")
        triples.append(f'<{uri_title}> <{RDFS.label}> "{escape_sparql_string(obra.name.title())}"^^<http://www.w3.org/2001/XMLSchema#string> .')
        triples.append(f"<{sujeto}> <{uri_ontologia}hasTitle> <{uri_title}> .")
        triples.append(f"<{uri_title}> <{uri_ontologia}isTitleOf> <{sujeto}> .")

        # Apelation (alternative name)
        if obra.apelation:
            triples.append(f'<{sujeto}> <https://w3id.org/OntoExhibit#apelation> "{escape_sparql_string(obra.apelation)}"^^<http://www.w3.org/2001/XMLSchema#string> .')

        # Type
        if obra.type:
            types = obra.type if isinstance(obra.type, list) else [obra.type]
            for t in types:
                triples.append(f'<{sujeto}> <https://w3id.org/OntoExhibit#type> "{escape_sparql_string(t)}"^^<http://www.w3.org/2001/XMLSchema#string> .')

        # Production (for author, dates, and place)
        if obra.author or obra.production_start_date or obra.production_end_date or obra.production_place:
            prod_hash = hash_sha256(f"{obra.name}_production")
            uri_prod = f"{uri_ontologia}production/{prod_hash}"
            
            triples.append(f"<{uri_prod}> <{RDF.type}> <{uri_ontologia}Production> .")
            triples.append(f"<{sujeto}> <{uri_ontologia}hasProduction> <{uri_prod}> .")
            triples.append(f"<{uri_prod}> <{uri_ontologia}isProductionOf> <{sujeto}> .")

            # Author
            if obra.author:
                author_name = obra.author.get("name", "") if isinstance(obra.author, dict) else str(obra.author)
                if author_name:
                    # Create author role
                    author_role_hash = hash_sha256(f"{author_name}_author_role")
                    uri_author_role = f"{uri_ontologia}author_role/{author_role_hash}"
                    
                    # Create or reference human actant
                    author_actant_hash = hash_sha256(f"{author_name} - person")
                    uri_author_actant = f"{uri_ontologia}human_actant/{author_actant_hash}"
                    
                    triples.append(f"<{uri_author_role}> <{RDF.type}> <{uri_ontologia}Author_Role> .")
                    triples.append(f"<{uri_prod}> <{uri_ontologia}hasProductionAuthor> <{uri_author_role}> .")
                    triples.append(f"<{uri_author_role}> <{uri_ontologia}isProductionAuthorOf> <{uri_prod}> .")
                    
                    # Link role to actant
                    triples.append(f"<{uri_author_role}> <{uri_ontologia}isRoleOf> <{uri_author_actant}> .")
                    triples.append(f"<{uri_author_actant}> <{uri_ontologia}hasRole> <{uri_author_role}> .")
                    
                    # Create actant entity
                    triples.append(f"<{uri_author_actant}> <{RDF.type}> <{uri_ontologia}Human_Actant> .")
                    triples.append(f'<{uri_author_actant}> <{RDFS.label}> "{escape_sparql_string(author_name.title())}"^^<http://www.w3.org/2001/XMLSchema#string> .')

            # Production dates (time span)
            if obra.production_start_date or obra.production_end_date:
                timespan_hash = hash_sha256(f"{obra.name}_timespan")
                uri_timespan = f"{uri_ontologia}time_range/{timespan_hash}"
                
                triples.append(f"<{uri_timespan}> <{RDF.type}> <{uri_ontologia}Time_Range> .")
                triples.append(f"<{uri_prod}> <{uri_ontologia}hasTimeSpan> <{uri_timespan}> .")
                triples.append(f"<{uri_timespan}> <{uri_ontologia}isTimeSpanOf> <{uri_prod}> .")

                if obra.production_start_date:
                    fecha = validar_fecha(obra.production_start_date)
                    if fecha:
                        fecha_str = fecha.strftime("%Y-%m-%d")
                        date_hash = hash_sha256(fecha_str)
                        uri_start_date = f"<https://w3id.org/OntoExhibit#exactdate/{date_hash}>"
                        
                        triples.append(f"{uri_start_date} <{RDF.type}> <https://w3id.org/OntoExhibit#ExactDate> .")
                        triples.append(f'{uri_start_date} <{RDFS.label}> "{fecha_str}"^^<http://www.w3.org/2001/XMLSchema#date> .')
                        triples.append(f"<{uri_timespan}> <{uri_ontologia}hasStartingDate> {uri_start_date} .")
                        triples.append(f"{uri_start_date} <{uri_ontologia}isStartingDateOf> <{uri_timespan}> .")

                if obra.production_end_date:
                    fecha = validar_fecha(obra.production_end_date)
                    if fecha:
                        fecha_str = fecha.strftime("%Y-%m-%d")
                        date_hash = hash_sha256(fecha_str)
                        uri_end_date = f"<https://w3id.org/OntoExhibit#exactdate/{date_hash}>"
                        
                        triples.append(f"{uri_end_date} <{RDF.type}> <https://w3id.org/OntoExhibit#ExactDate> .")
                        triples.append(f'{uri_end_date} <{RDFS.label}> "{fecha_str}"^^<http://www.w3.org/2001/XMLSchema#date> .')
                        triples.append(f"<{uri_timespan}> <{uri_ontologia}hasEndingDate> {uri_end_date} .")
                        triples.append(f"{uri_end_date} <{uri_ontologia}isEndingDateOf> <{uri_timespan}> .")

            # Production place
            if obra.production_place:
                place_hash = hash_sha256(obra.production_place)
                uri_place = f"{uri_ontologia}territorialEntity/{place_hash}"
                
                triples.append(f"<{uri_place}> <{RDF.type}> <{uri_ontologia}TerritorialEntity> .")
                triples.append(f'<{uri_place}> <{RDFS.label}> "{escape_sparql_string(obra.production_place.title())}"^^<http://www.w3.org/2001/XMLSchema#string> .')
                triples.append(f"<{uri_prod}> <https://w3id.org/OntoExhibit#takesPlaceAt> <{uri_place}> .")
        
        # Build final query
        query = f"INSERT DATA\n{{\n\tGRAPH <{settings.DEFAULT_GRAPH_URL}> {{\n"
        for triple in triples:
            query += f"\t\t{triple}\n"
        query += "\t}\n}"
        
        return query, f"https://w3id.org/OntoExhibit#{quote('work_manifestation')}/{hash_sha256(data_to_hash)}"

    @staticmethod
    def delete_obra(uri: str) -> list:
        """Generate SPARQL DELETE queries to remove all triples for an artwork."""
        clean_uri = uri.strip().lstrip('<').rstrip('>')
        graph_url = settings.DEFAULT_GRAPH_URL
        
        queries = []
        queries.append(f"""
            WITH <{graph_url}>
            DELETE {{
                <{clean_uri}> ?p ?o .
            }}
            WHERE {{
                <{clean_uri}> ?p ?o .
            }}
        """)
        queries.append(f"""
            WITH <{graph_url}>
            DELETE {{
                ?s ?p <{clean_uri}> .
            }}
            WHERE {{
                ?s ?p <{clean_uri}> .
            }}
        """)
        return queries

    GET_ARTWORK_BY_ID = f"""
        {PREFIXES}
        SELECT ?uri 
               (SAMPLE(COALESCE(?inner_title_label, ?inner_label, "")) as ?label)
               (GROUP_CONCAT(DISTINCT ?inner_type; separator="|") as ?type)
               (SAMPLE(?inner_apelation) as ?apelation)
               (SAMPLE(?inner_label_starting_date) as ?label_starting_date)
               (SAMPLE(?inner_label_ending_date) as ?label_ending_date)
               (SAMPLE(?inner_production_place) as ?production_place)
               (GROUP_CONCAT(DISTINCT CONCAT(?inner_author, ":::", STR(?uri_author)); separator="|") as ?authors)
               (GROUP_CONCAT(DISTINCT CONCAT(?inner_owner, ":::", STR(?uri_owner)); separator="|") as ?owners)
               (GROUP_CONCAT(DISTINCT ?inner_topic; separator="|") as ?topic)
               (GROUP_CONCAT(DISTINCT CONCAT(?inner_exhibition, ":::", STR(?uri_exhibition)); separator="|") as ?exhibitions)
        WHERE 
        {{
            ?uri rdf:type <https://w3id.org/OntoExhibit#Work_Manifestation> .
            
            OPTIONAL {{ ?uri rdfs:label ?inner_label . }}
            OPTIONAL {{ 
                ?uri <https://w3id.org/OntoExhibit#hasTitle> ?title_entity .
                ?title_entity rdfs:label ?inner_title_label .
            }}
            
            FILTER (regex(str(?uri), "%s", "i"))
            
            OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#type> ?inner_type . }}
            OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#apelation> ?inner_apelation }}
            
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasOwner> ?owner_role .
                ?uri_owner <https://w3id.org/OntoExhibit#hasRole> ?owner_role .
                ?uri_owner rdfs:label ?inner_owner
            }}
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasProduction> ?prod .
                OPTIONAL {{
                    ?prod <https://w3id.org/OntoExhibit#hasProductionAuthor> ?author_role .
                    ?uri_author <https://w3id.org/OntoExhibit#hasRole> ?author_role .
                    ?uri_author rdfs:label ?inner_author
                }}
                OPTIONAL {{
                    ?prod <https://w3id.org/OntoExhibit#hasTimeSpan> ?tr .
                    ?tr <https://w3id.org/OntoExhibit#hasStartingDate> ?start_date .
                    ?start_date rdfs:label ?inner_label_starting_date .
                }}
                OPTIONAL {{
                    ?prod <https://w3id.org/OntoExhibit#hasTimeSpan> ?tr .
                    ?tr <https://w3id.org/OntoExhibit#hasEndingDate> ?end_date .
                    ?end_date rdfs:label ?inner_label_ending_date .
                }}
                OPTIONAL {{
                    ?prod <https://w3id.org/OntoExhibit#takesPlaceAt> ?place_uri .
                    ?place_uri rdfs:label ?inner_production_place .
                }}
            }}
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#isDisplayedAt> ?uri_exhibition .
                ?uri_exhibition rdfs:label ?inner_exhibition
            }}
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasTheme> ?uri_topic .
                ?uri_topic rdfs:label ?inner_topic
            }}
        }} 
        GROUP BY ?uri
    """


