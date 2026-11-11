from urllib.parse import quote

from rdflib import RDF, RDFS

from app.core.config import settings
from app.models.domain import Exposicion
from app.services.queries.base import PREFIXES, URI_ONTOLOGIA, uri_ontologia
from app.services.queries.utils import escape_sparql_string
from app.utils.helpers import hash_sha256, normalize_name, validar_fecha


class ExhibitionQueries:
    COUNT_EXPOSICIONES = f"""
        {PREFIXES}
        SELECT (count(distinct ?uri) as ?count) WHERE 
        {{   
            ?uri rdf:type <https://w3id.org/OntoExhibit#Exhibition>
        }}
    """

    @staticmethod
    def get_exposiciones_ids(limit: int, last_label: str = None, last_uri: str = None, text_search: str = None, 
                             start_date: str = None, end_date: str = None, curator_name: str = None, place: str = None,
                             organizer: str = None, sponsor: str = None, theme: str = None, exhibition_type: str = None,
                             participating_actant: str = None, displayed_artwork: str = None,
                             curator: str = None, organizer_uri: str = None, sponsor_uri: str = None) -> str:
        
        filters = []
        inner_joins = []

        # Always bind label for sorting
        inner_joins.append("""
            OPTIONAL { ?uri <http://www.w3.org/2000/01/rdf-schema#label> ?direct_label }
            OPTIONAL { 
                ?uri <https://w3id.org/OntoExhibit#hasTitle> ?title_node . 
                ?title_node <http://www.w3.org/2000/01/rdf-schema#label> ?title_label 
            }
            BIND(COALESCE(?title_label, ?direct_label, "Untitled Exhibition") AS ?inner_label)
        """)

        if text_search:
            e_text = escape_sparql_string(text_search)
            filters.append(f'(regex(?inner_label, "{e_text}", "i") || regex(?inner_curator_name, "{e_text}", "i") || regex(?inner_organizer, "{e_text}", "i"))')
            inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasExhibitionMaking> ?making_ts .
                    OPTIONAL { ?making_ts <https://w3id.org/OntoExhibit#hasCurator> ?curator_ts . ?actor_ts_c <https://w3id.org/OntoExhibit#hasRole> ?curator_ts . ?actor_ts_c rdfs:label ?inner_curator_name }
                    OPTIONAL { ?making_ts <https://w3id.org/OntoExhibit#hasOrganizer> ?org_uri_ts . ?actor_ts_o <https://w3id.org/OntoExhibit#hasRole> ?org_uri_ts . ?actor_ts_o rdfs:label ?inner_organizer }
                }
            """)
        
        if participating_actant:
             inner_joins.append(f"""
                ?uri <https://w3id.org/OntoExhibit#hasExhibitionMaking> ?making_pa .
                ?making_pa ?role_prop_pa ?role_pa .
                <{participating_actant}> <https://w3id.org/OntoExhibit#hasRole> ?role_pa .
             """)

        if curator:
             inner_joins.append(f"""
                ?uri <https://w3id.org/OntoExhibit#hasExhibitionMaking> ?making_c .
                ?making_c <https://w3id.org/OntoExhibit#hasCurator> ?curator_role_c .
                <{curator}> <https://w3id.org/OntoExhibit#hasRole> ?curator_role_c .
             """)

        if organizer_uri:
             inner_joins.append(f"""
                ?uri <https://w3id.org/OntoExhibit#hasExhibitionMaking> ?making_o .
                ?making_o <https://w3id.org/OntoExhibit#hasOrganizer> ?organizer_role_o .
                <{organizer_uri}> <https://w3id.org/OntoExhibit#hasRole> ?organizer_role_o .
             """)
             
        if sponsor_uri:
             inner_joins.append(f"""
                ?uri <https://w3id.org/OntoExhibit#hasExhibitionMaking> ?making_s .
                ?making_s <https://w3id.org/OntoExhibit#hasFunder> ?sponsor_role_s .
                <{sponsor_uri}> <https://w3id.org/OntoExhibit#hasRole> ?sponsor_role_s .
             """)

        if displayed_artwork:
             inner_joins.append(f"""
                ?uri <https://w3id.org/OntoExhibit#displays> <{displayed_artwork}> .
             """)

        # Date range filtering: start_date and end_date filter based on exhibition start/end dates
        if start_date or end_date:
            inner_joins.append("""
                OPTIONAL { ?uri <https://w3id.org/OntoExhibit#hasOpening> ?opening_sd . ?opening_sd <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_opening_sd . ?time_opening_sd rdfs:label ?inner_label_starting_date }
                OPTIONAL { ?uri <https://w3id.org/OntoExhibit#hasClosing> ?closing_ed . ?closing_ed <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_closing_ed . ?time_closing_ed rdfs:label ?inner_label_ending_date }
            """)

            # Build date filters
            # start_date: filter exhibitions by their start date >= start_date
            # end_date: filter exhibitions by their end date <= end_date
            date_conditions = []
            if start_date:
                # Exhibition starts on or after the given start_date (must have start_date)
                date_conditions.append(f'(BOUND(?inner_label_starting_date) && str(?inner_label_starting_date) >= "{escape_sparql_string(start_date)}")')
            if end_date:
                # Exhibition ends on or before the given end_date (must have end_date)
                date_conditions.append(f'(BOUND(?inner_label_ending_date) && str(?inner_label_ending_date) <= "{escape_sparql_string(end_date)}")')

            if date_conditions:
                filters.append(f'({" && ".join(date_conditions)})')
            
        if curator_name and not text_search:
             filters.append(f'regex(?inner_curator_name, "{escape_sparql_string(curator_name)}", "i")')
             inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasExhibitionMaking> ?making_cn .
                    OPTIONAL { ?making_cn <https://w3id.org/OntoExhibit#hasCurator> ?curator_cn . ?actor_cn <https://w3id.org/OntoExhibit#hasRole> ?curator_cn . ?actor_cn rdfs:label ?inner_curator_name }
                }
             """)

        if place:
            filters.append(f'regex(?inner_label_place, "{escape_sparql_string(place)}", "i")')
            inner_joins.append("""
                OPTIONAL { ?uri <https://w3id.org/OntoExhibit#takesPlaceAt> ?place_p . ?place_p rdfs:label ?inner_label_place }
            """)

        if organizer and not text_search:
            filters.append(f'regex(?inner_organizer, "{escape_sparql_string(organizer)}", "i")')
            inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasExhibitionMaking> ?making_org .
                    OPTIONAL { ?making_org <https://w3id.org/OntoExhibit#hasOrganizer> ?org_uri_org . ?actor_org <https://w3id.org/OntoExhibit#hasRole> ?org_uri_org . ?actor_org rdfs:label ?inner_organizer }
                }
            """)

        if sponsor:
             filters.append(f'regex(?inner_sponsor, "{escape_sparql_string(sponsor)}", "i")')
             inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasExhibitionMaking> ?making_sp .
                    OPTIONAL { ?making_sp <https://w3id.org/OntoExhibit#hasFunder> ?spon_uri_sp . ?actor_sp <https://w3id.org/OntoExhibit#hasRole> ?spon_uri_sp . ?actor_sp rdfs:label ?inner_sponsor }
                }
             """)

        if theme:
             filters.append(f'regex(?inner_theme_label, "{escape_sparql_string(theme)}", "i")')
             inner_joins.append("""
                OPTIONAL { ?uri <https://w3id.org/OntoExhibit#hasTheme> ?theme_node_th . OPTIONAL { ?theme_node_th rdfs:label ?inner_theme_label . } }
             """)

        if exhibition_type:
             filters.append(f'regex(?inner_type_label, "{escape_sparql_string(exhibition_type)}", "i")')
             inner_joins.append("""
                OPTIONAL { ?uri <https://w3id.org/OntoExhibit#type> ?inner_type_label . }
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
            WHERE {{
                ?uri rdf:type <https://w3id.org/OntoExhibit#Exhibition> .
                {inner_joins_str}
                {filter_clause}
                {pagination_filter}
            }}
            ORDER BY ?uri
            LIMIT {limit}
        """


    @staticmethod
    def get_exposiciones_details(uris: list[str]) -> str:
        if not uris:
            return ""
        
        # Escape URIs properly and join them for the VALUES clause or FILTER IN
        uris_str = " ".join([f"<{u}>" for u in uris])
        
        # We need to Select everything and Aggregate
        return f"""
            {PREFIXES}
            SELECT ?uri (SAMPLE(?inner_label) as ?label) 
                   (SAMPLE(?inner_label_place) as ?label_place) 
                   (SAMPLE(?inner_label_starting_date) as ?label_starting_date) 
                   (SAMPLE(?inner_label_ending_date) as ?label_ending_date) 
                   (GROUP_CONCAT(DISTINCT CONCAT(?inner_curator_name, ":::", STR(?actor_c)); separator="|") as ?curators) 
                   (GROUP_CONCAT(DISTINCT CONCAT(?inner_organizer, ":::", STR(?actor_o)); separator="|") as ?organizers) 
                   (GROUP_CONCAT(DISTINCT CONCAT(?inner_funder, ":::", STR(?actor_f)); separator="|") as ?funders) 
                   (GROUP_CONCAT(DISTINCT ?inner_theme_label; separator="|") as ?theme_label) 
                   (GROUP_CONCAT(DISTINCT ?inner_type_label; separator="|") as ?type_label)
                   (GROUP_CONCAT(DISTINCT CONCAT(?inner_pa_name, ":::", STR(?actor_pa)); separator="|") as ?participating_actants)
                   (GROUP_CONCAT(DISTINCT CONCAT(?inner_art_label, ":::", STR(?artwork)); separator="|") as ?exhibited_artworks)
            WHERE 
            {{
                VALUES ?uri {{ {uris_str} }}
                
                OPTIONAL {{ ?uri <http://www.w3.org/2000/01/rdf-schema#label> ?direct_label }}
                OPTIONAL {{ 
                    ?uri <https://w3id.org/OntoExhibit#hasTitle> ?title_node . 
                    ?title_node <http://www.w3.org/2000/01/rdf-schema#label> ?title_label 
                }}
                BIND(COALESCE(?title_label, ?direct_label, "Untitled Exhibition") AS ?inner_label)

                OPTIONAL {{ 
                    ?uri <https://w3id.org/OntoExhibit#takesPlaceAt> ?place .
                    ?place rdfs:label ?inner_label_place
                }}
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#hasOpening> ?opening .
                    ?opening <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_opening .
                    ?time_opening rdfs:label ?inner_label_starting_date
                }}
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#hasClosing> ?closing .
                    ?closing <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_closing .
                    ?time_closing rdfs:label ?inner_label_ending_date
                }}

                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#hasTheme> ?theme_node .
                    OPTIONAL {{ ?theme_node rdfs:label ?inner_theme_label . }}
                }}

                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#type> ?inner_type_label .
                }}

                # Link to ExhibitionMaking
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#hasExhibitionMaking> ?making .
                    
                    OPTIONAL {{
                        ?making <https://w3id.org/OntoExhibit#hasCurator> ?curator .
                        ?actor_c <https://w3id.org/OntoExhibit#hasRole> ?curator .
                        ?actor_c rdfs:label ?inner_curator_name
                    }}
                    OPTIONAL {{
                        ?making <https://w3id.org/OntoExhibit#hasOrganizer> ?org_uri .
                        ?actor_o <https://w3id.org/OntoExhibit#hasRole> ?org_uri .
                        ?actor_o rdfs:label ?inner_organizer
                    }}
                    OPTIONAL {{
                        ?making <https://w3id.org/OntoExhibit#hasFunder> ?funder_uri .
                        ?actor_f <https://w3id.org/OntoExhibit#hasRole> ?funder_uri .
                        ?actor_f rdfs:label ?inner_funder
                    }}
                    # Generic Participating Actant (any role)
                    OPTIONAL {{
                        ?making ?p_pa ?role_pa .
                        ?actor_pa <https://w3id.org/OntoExhibit#hasRole> ?role_pa .
                        ?actor_pa rdfs:label ?inner_pa_name .
                        # Filter to only Role subclasses if needed, but safe here
                    }}
                }}
                
                # Exhibited Artworks
                OPTIONAL {{
                     ?uri <https://w3id.org/OntoExhibit#displays> ?artwork .
                     ?artwork rdfs:label ?inner_art_label
                }}
            }} 
            GROUP BY ?uri
        """

    @staticmethod
    def add_exposicion(exposicion: Exposicion) -> str:
        POST_EXHIBITION = f"INSERT DATA\n\t{{\n\t\tGRAPH <{settings.DEFAULT_GRAPH_URL}> {{\n"

        normalized = normalize_name(exposicion.name)
        data_to_hash = f"exhibition - {normalized}"
        sujeto = f"{uri_ontologia}exhibition/{hash_sha256(data_to_hash)}"
        uri_exposicion = f"{URI_ONTOLOGIA}exhibition/{hash_sha256(data_to_hash)}"

        POST_EXHIBITION += f"\t\t<{sujeto}> <{RDF.type}> <{uri_ontologia}Exhibition> .\n"
        POST_EXHIBITION += f'\t\t<{sujeto}> <{RDFS.label}> "{escape_sparql_string(exposicion.name.title())}"^^<http://www.w3.org/2001/XMLSchema#string> .\n'

        # Title entity
        uri_title = f"{uri_ontologia}title/{hash_sha256(exposicion.name)}"
        POST_EXHIBITION += f"\t\t<{uri_title}> <{RDF.type}> <{uri_ontologia}Title> .\n"
        POST_EXHIBITION += f'\t\t<{uri_title}> <{RDFS.label}> "{escape_sparql_string(exposicion.name.title())}"^^<http://www.w3.org/2001/XMLSchema#string> .\n'
        POST_EXHIBITION += f"\t\t<{sujeto}> <{uri_ontologia}hasTitle> <{uri_title}> .\n"
        POST_EXHIBITION += f"\t\t<{uri_title}> <{uri_ontologia}isTitleOf> <{sujeto}> .\n"

        # Exhibition Type
        if exposicion.tipo_exposicion:
            for tipo in (exposicion.tipo_exposicion if isinstance(exposicion.tipo_exposicion, list) else [exposicion.tipo_exposicion]):
                if tipo:
                    POST_EXHIBITION += f'\t\t<{sujeto}> <{URI_ONTOLOGIA}type> "{escape_sparql_string(tipo)}"^^<http://www.w3.org/2001/XMLSchema#string> .\n'

        # Create ExhibitionMaking if any role-related data exists
        needs_exhibition_making = (
            exposicion.fecha_inicio
            or exposicion.fecha_fin
            or exposicion.lugar_celebracion
            or exposicion.comisario
            or exposicion.organiza
            or exposicion.exposicion_patrocinada_por
            or exposicion.exposicion_exhibe_artista
        )

        if needs_exhibition_making:
            uri_id_exhibition_making = f'{sujeto}/{quote("exhibition making")}'
            POST_EXHIBITION += f"\t\t<{uri_id_exhibition_making}> <{RDF.type}> <{uri_ontologia}ExhibitionMaking> .\n"
            POST_EXHIBITION += f"\t\t<{sujeto}> <{uri_ontologia}hasExhibitionMaking> <{uri_id_exhibition_making}> .\n"
            POST_EXHIBITION += f"\t\t<{uri_id_exhibition_making}> <{uri_ontologia}isExhibitionMakingOf> <{sujeto}> .\n"

            # Handle Curators
            if exposicion.comisario:
                for idx, curator_data in enumerate(exposicion.comisario):
                    curator_uri = curator_data.get('uri') if isinstance(curator_data, dict) else curator_data
                    if curator_uri:
                        role_hash = hash_sha256(f"curator-{curator_uri}-{uri_exposicion}-{idx}")
                        curator_role_uri = f"<{URI_ONTOLOGIA}curator/{role_hash}>"
                        POST_EXHIBITION += f"\t\t{curator_role_uri} <{RDF.type}> <{URI_ONTOLOGIA}Curator> .\n"
                        POST_EXHIBITION += f"\t\t<{uri_id_exhibition_making}> <{URI_ONTOLOGIA}hasCurator> {curator_role_uri} .\n"
                        POST_EXHIBITION += f"\t\t{curator_role_uri} <{URI_ONTOLOGIA}isRoleOf> <{curator_uri}> .\n"
                        POST_EXHIBITION += f"\t\t<{curator_uri}> <{URI_ONTOLOGIA}hasRole> {curator_role_uri} .\n"

            # Handle Organizers
            if exposicion.organiza:
                for idx, org_data in enumerate(exposicion.organiza):
                    org_uri = org_data.get('uri') if isinstance(org_data, dict) else org_data
                    if org_uri:
                        role_hash = hash_sha256(f"organizer-{org_uri}-{uri_exposicion}-{idx}")
                        org_role_uri = f"<{URI_ONTOLOGIA}organizer/{role_hash}>"
                        POST_EXHIBITION += f"\t\t{org_role_uri} <{RDF.type}> <{URI_ONTOLOGIA}Organizer> .\n"
                        POST_EXHIBITION += f"\t\t<{uri_id_exhibition_making}> <{URI_ONTOLOGIA}hasOrganizer> {org_role_uri} .\n"
                        POST_EXHIBITION += f"\t\t{org_role_uri} <{URI_ONTOLOGIA}isRoleOf> <{org_uri}> .\n"
                        POST_EXHIBITION += f"\t\t<{org_uri}> <{URI_ONTOLOGIA}hasRole> {org_role_uri} .\n"

            # Handle Funders/Sponsors
            if exposicion.exposicion_patrocinada_por:
                for idx, funder_data in enumerate(exposicion.exposicion_patrocinada_por):
                    funder_uri = funder_data.get('uri') if isinstance(funder_data, dict) else funder_data
                    if funder_uri:
                        role_hash = hash_sha256(f"funder-{funder_uri}-{uri_exposicion}-{idx}")
                        funder_role_uri = f"<{URI_ONTOLOGIA}funder/{role_hash}>"
                        POST_EXHIBITION += f"\t\t{funder_role_uri} <{RDF.type}> <{URI_ONTOLOGIA}Funder> .\n"
                        POST_EXHIBITION += f"\t\t<{uri_id_exhibition_making}> <{URI_ONTOLOGIA}hasFunder> {funder_role_uri} .\n"
                        POST_EXHIBITION += f"\t\t{funder_role_uri} <{URI_ONTOLOGIA}isRoleOf> <{funder_uri}> .\n"
                        POST_EXHIBITION += f"\t\t<{funder_uri}> <{URI_ONTOLOGIA}hasRole> {funder_role_uri} .\n"

            # Handle Exhibiting Artists
            if exposicion.exposicion_exhibe_artista:
                for idx, exhibitor_data in enumerate(exposicion.exposicion_exhibe_artista):
                    exhibitor_uri = exhibitor_data.get('uri') if isinstance(exhibitor_data, dict) else exhibitor_data
                    if exhibitor_uri:
                        role_hash = hash_sha256(f"exhibiting-actant-{exhibitor_uri}-{uri_exposicion}-{idx}")
                        exhibitor_role_uri = f"<{URI_ONTOLOGIA}exhibitingactant/{role_hash}>"
                        POST_EXHIBITION += f"\t\t{exhibitor_role_uri} <{RDF.type}> <{URI_ONTOLOGIA}ExhibitingActant> .\n"
                        POST_EXHIBITION += f"\t\t<{uri_id_exhibition_making}> <{URI_ONTOLOGIA}hasExhibitingActant> {exhibitor_role_uri} .\n"
                        POST_EXHIBITION += f"\t\t{exhibitor_role_uri} <{URI_ONTOLOGIA}isRoleOf> <{exhibitor_uri}> .\n"
                        POST_EXHIBITION += f"\t\t<{exhibitor_uri}> <{URI_ONTOLOGIA}hasRole> {exhibitor_role_uri} .\n"

            # Handle Location/Place
            if exposicion.lugar_celebracion:
                place_hash = hash_sha256(f"place-{exposicion.lugar_celebracion}")
                place_uri = f"<{URI_ONTOLOGIA}place/{place_hash}>"
                POST_EXHIBITION += f"\t\t{place_uri} <{RDF.type}> <{URI_ONTOLOGIA}Place> .\n"
                POST_EXHIBITION += f'\t\t{place_uri} <{RDFS.label}> "{escape_sparql_string(exposicion.lugar_celebracion)}"^^<http://www.w3.org/2001/XMLSchema#string> .\n'
                POST_EXHIBITION += f"\t\t<{sujeto}> <{URI_ONTOLOGIA}takesPlaceAt> {place_uri} .\n"

            # Handle Opening Date
            if exposicion.fecha_inicio:
                fecha = validar_fecha(exposicion.fecha_inicio)
                if fecha:
                    fecha_str = fecha.strftime("%Y-%m-%d")
                    tipo_indiv = "ExactDate"
                    uri_fecha = f"<{URI_ONTOLOGIA}{tipo_indiv.lower()}/{hash_sha256(fecha_str)}>"
                    POST_EXHIBITION += f"\t\t{uri_fecha} <{RDF.type}> <{URI_ONTOLOGIA}{tipo_indiv}> .\n"
                    POST_EXHIBITION += f'\t\t{uri_fecha} <{RDFS.label}> "{fecha_str}"^^<http://www.w3.org/2001/XMLSchema#date> .\n'

                    uri_opening = f"<{sujeto}/opening>"
                    POST_EXHIBITION += f"\t\t{uri_opening} <{RDF.type}> <{URI_ONTOLOGIA}Opening> .\n"
                    POST_EXHIBITION += f"\t\t{uri_opening} <{URI_ONTOLOGIA}hasTimeSpan> {uri_fecha} .\n"
                    POST_EXHIBITION += f"\t\t<{sujeto}> <{URI_ONTOLOGIA}hasOpening> {uri_opening} .\n"

            # Handle Closing Date
            if exposicion.fecha_fin:
                fecha = validar_fecha(exposicion.fecha_fin)
                if fecha:
                    fecha_str = fecha.strftime("%Y-%m-%d")
                    tipo_indiv = "ExactDate"
                    uri_fecha_fin = f"<{URI_ONTOLOGIA}{tipo_indiv.lower()}/{hash_sha256(fecha_str)}>"
                    POST_EXHIBITION += f"\t\t{uri_fecha_fin} <{RDF.type}> <{URI_ONTOLOGIA}{tipo_indiv}> .\n"
                    POST_EXHIBITION += f'\t\t{uri_fecha_fin} <{RDFS.label}> "{fecha_str}"^^<http://www.w3.org/2001/XMLSchema#date> .\n'

                    uri_closing = f"<{sujeto}/closing>"
                    POST_EXHIBITION += f"\t\t{uri_closing} <{RDF.type}> <{URI_ONTOLOGIA}Closing> .\n"
                    POST_EXHIBITION += f"\t\t{uri_closing} <{URI_ONTOLOGIA}hasTimeSpan> {uri_fecha_fin} .\n"
                    POST_EXHIBITION += f"\t\t<{sujeto}> <{URI_ONTOLOGIA}hasClosing> {uri_closing} .\n"

            # Handle Venue (Sede)
            if exposicion.sede:
                venue_hash = hash_sha256(f"venue-{exposicion.sede}")
                venue_uri = f"<{URI_ONTOLOGIA}institution/{venue_hash}>"
                # We treat the text venue as a rudimentary Institution if it doesn't exist, 
                # strictly speaking we are just asserting it exists here with a label and type.
                POST_EXHIBITION += f"\t\t{venue_uri} <{RDF.type}> <{URI_ONTOLOGIA}Institution> .\n"
                POST_EXHIBITION += f'\t\t{venue_uri} <{RDFS.label}> "{escape_sparql_string(exposicion.sede)}"^^<http://www.w3.org/2001/XMLSchema#string> .\n'
                POST_EXHIBITION += f"\t\t<{sujeto}> <{URI_ONTOLOGIA}hasVenue> {venue_uri} .\n"

        # Handle displayed artworks (direct relationship, not through ExhibitionMaking)
        if exposicion.exposicion_exhibe_obra_de_arte:
            for artwork_data in exposicion.exposicion_exhibe_obra_de_arte:
                artwork_uri = artwork_data.get('uri') if isinstance(artwork_data, dict) else artwork_data
                if artwork_uri:
                    POST_EXHIBITION += f"\t\t<{sujeto}> <{URI_ONTOLOGIA}displays> <{artwork_uri}> .\n"
                    POST_EXHIBITION += f"\t\t<{artwork_uri}> <{URI_ONTOLOGIA}isDisplayedAt> <{sujeto}> .\n"

        POST_EXHIBITION += "\t}\n}"
        return POST_EXHIBITION, uri_exposicion

    @staticmethod
    def delete_exposicion(uri: str) -> list:
        """Generate SPARQL DELETE queries to remove all triples for an exhibition."""
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
        queries.append(f"""
            WITH <{graph_url}>
            DELETE {{
                <{clean_uri}/exhibition%20making> ?p ?o .
            }}
            WHERE {{
                <{clean_uri}/exhibition%20making> ?p ?o .
            }}
        """)
        return queries

    GET_EXHIBITION_BY_ID = f"""
        {PREFIXES}
        SELECT ?uri (SAMPLE(?label) as ?label) (SAMPLE(?label_place) as ?label_place) (SAMPLE(?place) as ?place_uri) 
               (SAMPLE(?label_starting_date) as ?label_starting_date) (SAMPLE(?label_ending_date) as ?label_ending_date) 
               (GROUP_CONCAT(DISTINCT CONCAT(?curator_name, ":::", STR(?curator_person)); separator="|") as ?curators) 
               (GROUP_CONCAT(DISTINCT CONCAT(?organizer, ":::", STR(?actor_org)); separator="|") as ?organizers) 
               (GROUP_CONCAT(DISTINCT CONCAT(?funder, ":::", STR(?funder_person)); separator="|") as ?funders)
               (GROUP_CONCAT(DISTINCT CONCAT(?lender, ":::", STR(?actor_lender)); separator="|") as ?lenders)
               (GROUP_CONCAT(DISTINCT CONCAT(?exhibitor_name, ":::", STR(?exhibitor_actor)); separator="|") as ?exhibitors)

               (SAMPLE(?lat) as ?lat) (SAMPLE(?long) as ?long) (SAMPLE(?access) as ?access) 
               (SAMPLE(?venue_label) as ?venue_label) (SAMPLE(?venue) as ?venue_uri)
               (GROUP_CONCAT(DISTINCT ?theme_label; separator="|") as ?theme_label) 
               (GROUP_CONCAT(DISTINCT ?type_label; separator="|") as ?type_label)
        WHERE 
        {{
            BIND(<https://w3id.org/OntoExhibit#exhibition/%s> AS ?uri)
            ?uri rdf:type <https://w3id.org/OntoExhibit#Exhibition> .
            
            OPTIONAL {{ ?uri <http://www.w3.org/2000/01/rdf-schema#label> ?direct_label }}
            OPTIONAL {{ 
                ?uri <https://w3id.org/OntoExhibit#hasTitle> ?title_node . 
                ?title_node <http://www.w3.org/2000/01/rdf-schema#label> ?title_label 
            }}
            BIND(COALESCE(?title_label, ?direct_label, "Untitled Exhibition") AS ?label)

            OPTIONAL {{ 
                ?uri <https://w3id.org/OntoExhibit#takesPlaceAt> ?place .
                ?place rdfs:label ?label_place
            }}
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasOpening> ?opening .
                ?opening <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_opening .
                ?time_opening rdfs:label ?label_starting_date
            }}
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasClosing> ?closing .
                ?closing <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_closing .
                ?time_closing rdfs:label ?label_ending_date
            }}

            OPTIONAL {{
                 ?uri <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat .
                 ?uri <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?long .
            }}

            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#access> ?access .
            }}

            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasVenue> ?venue .
                ?venue <http://www.w3.org/2000/01/rdf-schema#label> ?venue_label .
            }}
            
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasTheme> ?theme_node .
                OPTIONAL {{ ?theme_node rdfs:label ?theme_label . }}
            }}

            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#type> ?type_label .
            }}

            # Link to ExhibitionMaking
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasExhibitionMaking> ?making .
                
                # Curator logic
                OPTIONAL {{
                    ?making <https://w3id.org/OntoExhibit#hasCurator> ?curator .
                    ?curator_person <https://w3id.org/OntoExhibit#hasRole> ?curator .
                    ?curator_person rdfs:label ?curator_name
                }}

                # Organizer logic
                OPTIONAL {{
                    ?making <https://w3id.org/OntoExhibit#hasOrganizer> ?org_uri .
                    ?actor_org <https://w3id.org/OntoExhibit#hasRole> ?org_uri .
                    ?actor_org rdfs:label ?organizer
                }}

                # Lender logic
                OPTIONAL {{
                    ?making <https://w3id.org/OntoExhibit#hasLender> ?lender_role .
                    ?actor_lender <https://w3id.org/OntoExhibit#hasRole> ?lender_role .
                    ?actor_lender rdfs:label ?lender
                }}

                # Funder logic (was Sponsor)
                OPTIONAL {{
                    ?making <https://w3id.org/OntoExhibit#hasFunder> ?funder_role .
                    ?funder_person <https://w3id.org/OntoExhibit#hasRole> ?funder_role .
                    ?funder_person rdfs:label ?funder
                }}

                # Exhibiting Actants (artists exhibiting at the exhibition)
                OPTIONAL {{
                    ?making <https://w3id.org/OntoExhibit#hasExhibitingActant> ?exhibitor_role .
                    ?exhibitor_actor <https://w3id.org/OntoExhibit#hasRole> ?exhibitor_role .
                    ?exhibitor_actor rdfs:label ?exhibitor_name
                }}
            }}
        }}  GROUP BY ?uri 
    """

    GET_EXHIBITION_ARTWORKS = f"""
        {PREFIXES}
        SELECT ?uri (GROUP_CONCAT(DISTINCT CONCAT(?artwork_label, ":::", STR(?artwork)); separator="|") as ?artworks)
        WHERE {{
            BIND(<https://w3id.org/OntoExhibit#exhibition/%s> AS ?uri)
            ?uri <https://w3id.org/OntoExhibit#displays> ?artwork .
            OPTIONAL {{ ?artwork rdfs:label ?artwork_label }}
        }} GROUP BY ?uri
    """

    @staticmethod
    def get_exhibition_museographers(exhibition_id: str) -> str:
        """Get companies that were museographers for this exhibition."""
        return f"""
            {PREFIXES}
            SELECT DISTINCT ?company_uri ?company_label
            WHERE {{
                BIND(<https://w3id.org/OntoExhibit#exhibition/{exhibition_id}> AS ?exhibition)
                
                ?exhibition <https://w3id.org/OntoExhibit#hasExhibitionMaking> ?making .
                ?making <https://w3id.org/OntoExhibit#hasMuseographer> ?museographer_role .
                ?museographer_role <https://w3id.org/OntoExhibit#isRoleOf> ?company_uri .
                
                ?company_uri rdf:type <https://w3id.org/OntoExhibit#Company> .
                ?company_uri rdfs:label ?company_label .
            }}
            ORDER BY ?company_label
        """

