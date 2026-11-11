from urllib.parse import quote

from rdflib import RDF, RDFS
from app.core.config import settings
from app.models.domain import Institucion
from app.services.queries.base import OBJECT_PROPERTIES, PREFIXES, URI_ONTOLOGIA, uri_ontologia
from app.services.queries.utils import add_any_type, escape_sparql_string
from app.utils.helpers import generate_hashed_id, hash_sha256, normalize_name


class InstitutionQueries:
    COUNT_INSTITUCIONES = f"""
        {PREFIXES}
        SELECT (count(distinct ?uri) as ?count) WHERE 
        {{   
            {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Institution> }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Cultural_Institution> }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Art_Center> }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Cultural_Center> }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#ExhibitionSpace> }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Interpretation_Center> }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Library> }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Museum> }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Educational_Institution> }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#University> }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Foundation_(Institution)> }}
        }}
    """

    @staticmethod
    def get_instituciones_ids(
        limit: int,
        last_label: str = None,
        last_uri: str = None,
        text_search: str = None,
        place: str = None,
        apelation: str = None,
        institution_type: str = None,
    ) -> str:
        filters = []
        optional_joins = []

        if text_search:
            escaped = escape_sparql_string(text_search)
            filters.append(f'regex(?label, "{escaped}", "i")')

        if place:
            escaped = escape_sparql_string(place)
            optional_joins.append("""
                OPTIONAL { 
                    ?uri <https://w3id.org/OntoExhibit#hasLocation> ?inner_location .
                    ?inner_location (<https://w3id.org/OntoExhibit#isLocatedAt>|<https://w3id.org/OntoExhibit#hasPlaceOfLocation>) ?inner_place_uri .
                    ?inner_place_uri rdfs:label ?inner_place_label .
                }
            """)
            filters.append(f'regex(?inner_place_label, "{escaped}", "i")')

        if apelation:
            escaped = escape_sparql_string(apelation)
            optional_joins.append('OPTIONAL { ?uri <https://w3id.org/OntoExhibit#apelation> ?inner_apelation }')
            filters.append(f'regex(?inner_apelation, "{escaped}", "i")')

        if institution_type:
            escaped = escape_sparql_string(institution_type)
            optional_joins.append("""
                OPTIONAL {
                    ?uri rdf:type ?inner_type_uri .
                    OPTIONAL { ?inner_type_uri rdfs:label ?inner_type_label }
                }
            """)
            filters.append(
                f'((BOUND(?inner_type_label) && regex(?inner_type_label, "{escaped}", "i")) || '
                f'(BOUND(?inner_type_uri) && regex(str(?inner_type_uri), "{escaped}", "i")))'
            )

        filter_clause = f"FILTER ({' && '.join(filters)})" if filters else ""
        optional_joins_str = "\n".join(optional_joins)
        
        pagination_filter = ""
        if last_label and last_uri:
            # Use URI-only comparison which is safe from special character issues
            pagination_filter = f"""
                FILTER (?uri > <{last_uri}>)
            """

        return f"""
            {PREFIXES}
            SELECT DISTINCT ?label ?uri ?institution_type
            WHERE
            {{
                {{
                    ?uri rdf:type <https://w3id.org/OntoExhibit#Institution> .
                    ?uri rdfs:label ?label
                    BIND("Institution" AS ?institution_type)
                }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Cultural_Institution> . ?uri rdfs:label ?label . BIND("Cultural Institution" AS ?institution_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Art_Center> . ?uri rdfs:label ?label . BIND("Art Center" AS ?institution_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Cultural_Center> . ?uri rdfs:label ?label . BIND("Cultural Center" AS ?institution_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#ExhibitionSpace> . ?uri rdfs:label ?label . BIND("Exhibition Space" AS ?institution_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Interpretation_Center> . ?uri rdfs:label ?label . BIND("Interpretation Center" AS ?institution_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Library> . ?uri rdfs:label ?label . BIND("Library" AS ?institution_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Museum> . ?uri rdfs:label ?label . BIND("Museum" AS ?institution_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Educational_Institution> . ?uri rdfs:label ?label . BIND("Educational Institution" AS ?institution_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#University> . ?uri rdfs:label ?label . BIND("University" AS ?institution_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Foundation_(Institution)> . ?uri rdfs:label ?label . BIND("Foundation (Institution)" AS ?institution_type) }}

                {optional_joins_str}
                {filter_clause}
                {pagination_filter}
            }}
            ORDER BY ?uri
            LIMIT {limit}
        """

    @staticmethod
    def get_instituciones_details(uris: list[str]) -> str:
        if not uris:
            return ""

        uris_str = " ".join([f"<{u}>" for u in uris])

        return f"""
            {PREFIXES}
            SELECT ?uri (SAMPLE(?inner_label) as ?label)
                   (SAMPLE(?inner_apelation) as ?apelation)
                   (GROUP_CONCAT(DISTINCT ?inner_label_place; separator="|") as ?label_place)
                   (SAMPLE(?inner_type) as ?institution_type)
                   (SAMPLE(?inner_ownership) as ?ownershipType)
                   (SAMPLE(?inner_address) as ?headquarters_address)
            WHERE
            {{
                VALUES ?uri {{ {uris_str} }}

                ?uri rdfs:label ?inner_label .

                {{
                    ?uri rdf:type <https://w3id.org/OntoExhibit#Institution> .
                    BIND("Institution" AS ?inner_type)
                }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Cultural_Institution> . BIND("Cultural Institution" AS ?inner_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Art_Center> . BIND("Art Center" AS ?inner_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Cultural_Center> . BIND("Cultural Center" AS ?inner_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#ExhibitionSpace> . BIND("Exhibition Space" AS ?inner_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Interpretation_Center> . BIND("Interpretation Center" AS ?inner_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Library> . BIND("Library" AS ?inner_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Museum> . BIND("Museum" AS ?inner_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Educational_Institution> . BIND("Educational Institution" AS ?inner_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#University> . BIND("University" AS ?inner_type) }}
                UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Foundation_(Institution)> . BIND("Foundation (Institution)" AS ?inner_type) }}

                OPTIONAL
                {{
                    ?uri <https://w3id.org/OntoExhibit#hasLocation> ?location.
                    ?location <https://w3id.org/OntoExhibit#isLocatedAt> ?place .
                    ?place rdfs:label ?inner_label_place
                }}
                OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#apelation> ?inner_apelation }}
                OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#ownershipType> ?inner_ownership }}
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#hasHeadquarters> ?headquarters .
                    ?headquarters rdf:type <https://w3id.org/OntoExhibit#Headquarter> .
                    OPTIONAL {{
                        ?headquarters <https://w3id.org/OntoExhibit#isHeadquarteredAt> ?hq_site .
                        ?hq_site rdfs:label ?inner_address
                    }}
                }}
            }}
            GROUP BY ?uri
        """

    GET_INSTITUTION = f"""
        {PREFIXES}
        SELECT DISTINCT ?label ?uri ?apelation ?label_place ?place_uri 
                        ?ownershipType ?email ?telephone ?uriHtml
                        ?headquarters_address ?headquarters_lat ?headquarters_long
        WHERE 
        {{
            {{
                ?uri rdf:type <https://w3id.org/OntoExhibit#Institution> .
                ?uri rdfs:label ?label
            }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Cultural_Institution> . ?uri rdfs:label ?label }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Academy_Of_Fine_Arts> . ?uri rdfs:label ?label }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Archive> . ?uri rdfs:label ?label }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Art_Center> . ?uri rdfs:label ?label }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Cultural_Center> . ?uri rdfs:label ?label }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#ExhibitionSpace> . ?uri rdfs:label ?label }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Interpretation_Center> . ?uri rdfs:label ?label }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Library> . ?uri rdfs:label ?label }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Museographic_Collection> . ?uri rdfs:label ?label }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Museum> . ?uri rdfs:label ?label }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Educational_Institution> . ?uri rdfs:label ?label }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Art_School> . ?uri rdfs:label ?label }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#University> . ?uri rdfs:label ?label }}
            UNION {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Foundation_(Institution)> . ?uri rdfs:label ?label }}
            
            FILTER (regex(str(?uri), "%s", "i"))

            OPTIONAL 
            {{ 
                ?uri <https://w3id.org/OntoExhibit#hasLocation> ?location.
                ?location <https://w3id.org/OntoExhibit#isLocatedAt> ?place_uri .
                ?place_uri rdfs:label ?label_place
            }}
            OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#apelation> ?apelation }}
            OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#ownershipType> ?ownershipType }}
            OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#email> ?email }}
            OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#phone> ?telephone }}
            OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#webPage> ?uriHtml }}
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasHeadquarters> ?headquarters .
                ?headquarters rdf:type <https://w3id.org/OntoExhibit#Headquarter> .
                OPTIONAL {{
                    ?headquarters <https://w3id.org/OntoExhibit#isHeadquarteredAt> ?hq_site .
                    ?hq_site rdfs:label ?headquarters_address
                }}
                OPTIONAL {{ ?headquarters <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?headquarters_lat }}
                OPTIONAL {{ ?headquarters <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?headquarters_long }}
            }}
        }}
    """

    @staticmethod
    def get_institution_executives(inst_id: str) -> str:
        """Get executive positions held at this institution."""
        return f"""
            {PREFIXES}
            SELECT DISTINCT ?person_uri ?person_label
            WHERE {{
                BIND(<https://w3id.org/OntoExhibit#institution/{inst_id}> AS ?institution)
                
                # Institution has executive position
                ?institution <https://w3id.org/OntoExhibit#executivePositionHeldsBy> ?exec_position .
                ?exec_position rdf:type <https://w3id.org/OntoExhibit#Executive_Position> .
                ?exec_position <https://w3id.org/OntoExhibit#isExecutivePositionOf> ?person_uri .
                
                ?person_uri rdfs:label ?person_label .
            }}
            ORDER BY ?person_label
        """


    GET_HOSTED_EXHIBITIONS = f"""
        {PREFIXES}
        SELECT DISTINCT ?uri (SAMPLE(?label) as ?label) (SAMPLE(?start_date) as ?start_date) (SAMPLE(?role) as ?role)
        WHERE 
        {{
            ?inst_uri rdfs:label ?inst_label .
            FILTER (regex(str(?inst_uri), "%s", "i"))
            
            {{
                ?uri <https://w3id.org/OntoExhibit#hasVenue> ?inst_uri .
                BIND("Venue" AS ?role)
            }}
            UNION
            {{
                ?uri <https://w3id.org/OntoExhibit#hasExhibitionMaking> ?making .
                ?making <https://w3id.org/OntoExhibit#hasOrganizer> ?role_node .
                ?role_node <https://w3id.org/OntoExhibit#isRoleOf> ?inst_uri .
                BIND("Organizer" AS ?role)
            }}
            UNION
            {{
                # Funder/Sponsor role - institution has a financer role
                ?inst_uri <https://w3id.org/OntoExhibit#hasRole> ?funder_role .
                ?funder_role <https://w3id.org/OntoExhibit#isFunderOf> ?making .
                ?making <https://w3id.org/OntoExhibit#isExhibitionMakingOf> ?uri .
                BIND("Funder" AS ?role)
            }}
            
            ?uri rdf:type <https://w3id.org/OntoExhibit#Exhibition> .
            
            OPTIONAL {{ ?uri rdfs:label ?label }}
            
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasOpening> ?opening .
                ?opening <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_opening .
                ?time_opening rdfs:label ?start_date
            }}
        }} GROUP BY ?uri
    """

    # Query to find exhibitions where institution was a lender
    GET_LENDER_EXHIBITIONS = f"""
        {PREFIXES}
        SELECT DISTINCT ?uri (SAMPLE(?label) as ?label) (SAMPLE(?start_date) as ?start_date)
        WHERE 
        {{
            ?inst_uri rdfs:label ?inst_label .
            FILTER (regex(str(?inst_uri), "%s", "i"))
            
            # Institution has a lender role
            ?inst_uri <https://w3id.org/OntoExhibit#hasRole> ?lender_role .
            ?lender_role <https://w3id.org/OntoExhibit#isLenderOf> ?making .
            ?making <https://w3id.org/OntoExhibit#isExhibitionMakingOf> ?uri .
            
            ?uri rdf:type <https://w3id.org/OntoExhibit#Exhibition> .
            
            OPTIONAL {{ ?uri rdfs:label ?label }}
            
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasOpening> ?opening .
                ?opening <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_opening .
                ?time_opening rdfs:label ?start_date
            }}
        }} GROUP BY ?uri
    """

    # Query to find artworks owned by the institution
    GET_OWNED_ARTWORKS = f"""
        {PREFIXES}
        SELECT DISTINCT ?uri (SAMPLE(?label) as ?label) (SAMPLE(?type) as ?type)
        WHERE 
        {{
            ?inst_uri rdfs:label ?inst_label .
            FILTER (regex(str(?inst_uri), "%s", "i"))
            
            # Institution has an owner role for the artwork
            ?inst_uri <https://w3id.org/OntoExhibit#hasRole> ?owner_role .
            ?uri <https://w3id.org/OntoExhibit#hasOwner> ?owner_role .
            
            ?uri rdf:type <https://w3id.org/OntoExhibit#Work_Manifestation> .
            
            OPTIONAL {{ ?uri rdfs:label ?label }}
            OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#type> ?type }}
        }} GROUP BY ?uri
    """

    @staticmethod
    def get_institution_collaborators(inst_id: str) -> str:
        """Get all persons who collaborate with this institution."""
        return f"""
            {PREFIXES}
            SELECT DISTINCT ?collaborator_uri ?collaborator_label
            WHERE {{
                BIND(<https://w3id.org/OntoExhibit#institution/{inst_id}> AS ?institution)
                
                # --- AFFILIATIONS (Person <-> Institution) ---
                {{
                     # Institution has affiliated (Institution has a person affiliated)
                     ?institution <https://w3id.org/OntoExhibit#hasAffiliated> ?affiliation .
                     ?affiliation <https://w3id.org/OntoExhibit#isAffiliationOf> ?collaborator_uri .
                }}
                UNION
                {{
                     # Person is affiliated with (Person points to Institution) - bidirectional check
                     ?collaborator_uri <https://w3id.org/OntoExhibit#hasAffiliation> ?affiliation .
                     ?affiliation <https://w3id.org/OntoExhibit#isAffiliatedWith> ?institution .
                }}
                
                ?collaborator_uri rdfs:label ?collaborator_label .
                
                # Ensure it's a person/human_actant
                {{
                    ?collaborator_uri rdf:type <https://w3id.org/OntoExhibit#Human_Actant> .
                }}
                UNION
                {{
                    ?collaborator_uri rdf:type <https://cidoc-crm.org/cidoc-crm/7.1.1/E21_Person> .
                }}
                UNION
                {{
                    ?collaborator_uri rdf:type <https://cidoc-crm.org/cidoc-crm/7.1.1/E74_Group> .
                }}
            }}
            ORDER BY ?collaborator_label
        """

    @staticmethod
    def get_parent_organization(inst_id: str) -> str:
        """Get the parent organization of this institution (hasParentOrganization)."""
        return f"""
            {PREFIXES}
            SELECT DISTINCT ?parent_uri ?parent_label
            WHERE {{
                BIND(<https://w3id.org/OntoExhibit#institution/{inst_id}> AS ?institution)
                
                # Institution has a parent organization
                ?institution <https://w3id.org/OntoExhibit#hasParentOrganization> ?parent_uri .
                ?parent_uri rdfs:label ?parent_label .
            }}
            ORDER BY ?parent_label
        """

    @staticmethod
    def get_child_organizations(inst_id: str) -> str:
        """Get child organizations of this institution (isParentOrganizationOf)."""
        return f"""
            {PREFIXES}
            SELECT DISTINCT ?child_uri ?child_label
            WHERE {{
                BIND(<https://w3id.org/OntoExhibit#institution/{inst_id}> AS ?institution)
                
                # Institution is the parent of child organizations
                ?institution <https://w3id.org/OntoExhibit#isParentOrganizationOf> ?child_uri .
                ?child_uri rdfs:label ?child_label .
            }}
            ORDER BY ?child_label
        """

    @staticmethod
    def add_institucion(entidad: Institucion) -> str:
        # Generate ID
        if not entidad.id:
            normalized = normalize_name(entidad.nombre)
            data_to_hash = f"{normalized}"
            entidad.id = hash_sha256(data_to_hash)
            
        # Base URI
        sujeto = f"<{URI_ONTOLOGIA}institution/{entidad.id}>"
        
        triples = []
        
        # 1. Type
        # If specific type provided, use it, otherwise default to Institution
        has_specific_type = False
        if entidad.tipo_institucion:
            types = entidad.tipo_institucion if isinstance(entidad.tipo_institucion, list) else [entidad.tipo_institucion]
            for t in types:
                if t:
                    # Map common frontend types to ontology classes if needed, or use as is if they match
                    # Assuming basic mapping or direct usage
                    clean_type = t.strip()
                    if clean_type == "Museum":
                        triples.append(f"{sujeto} <{RDF.type}> <https://w3id.org/OntoExhibit#Museum> .")
                        has_specific_type = True
                    elif clean_type == "Foundation (Institution)": # Handle special case from select
                        triples.append(f"{sujeto} <{RDF.type}> <https://w3id.org/OntoExhibit#Foundation_(Institution)> .")
                        has_specific_type = True
                    else:
                        # Try to use as class if valid, otherwise generic + property
                        # For now, let's assume valid subclasses or just add as explicit type
                        # Use quote to be safe for URI construction
                        triples.append(f"{sujeto} <{RDF.type}> <{URI_ONTOLOGIA}{quote(clean_type.replace(' ', '_'))}> .")
                        has_specific_type = True

        if not has_specific_type:
            triples.append(f"{sujeto} <{RDF.type}> <https://w3id.org/OntoExhibit#Institution> .")
            
        # 2. Label / Name
        triples.append(f'{sujeto} <{RDFS.label}> "{escape_sparql_string(entidad.nombre.title())}"^^<http://www.w3.org/2001/XMLSchema#string> .')
        
        # 3. Alternative Name (Apelation)
        if entidad.nombre_alternativo:
             triples.append(f'{sujeto} <https://w3id.org/OntoExhibit#apelation> "{escape_sparql_string(entidad.nombre_alternativo)}"^^<http://www.w3.org/2001/XMLSchema#string> .')

        # 4. Website
        if entidad.pagina_web:
             triples.append(f'{sujeto} <https://w3id.org/OntoExhibit#webPage> "{escape_sparql_string(entidad.pagina_web)}"^^<http://www.w3.org/2001/XMLSchema#anyURI> .')
             
        # 5. Location (City/Place)
        # Pattern: Institution -> hasLocation -> Place (TerritorialEntity) -> isLocatedAt -> Institution
        if entidad.lugar_sede:
            place_hash = hash_sha256(entidad.lugar_sede)
            uri_place = f"<{URI_ONTOLOGIA}territorialEntity/{place_hash}>"
            
            triples.append(f"{uri_place} <{RDF.type}> <{URI_ONTOLOGIA}TerritorialEntity> .")
            triples.append(f'{uri_place} <{RDFS.label}> "{escape_sparql_string(entidad.lugar_sede.title())}"^^<http://www.w3.org/2001/XMLSchema#string> .')
            
            # Create Location node to link them? 
            # Ontology typically uses: Institution -> hasLocation -> Location -> isLocatedAt -> Place
            # Or simplified: Institution -> hasLocation -> Place (if range is place)
            # Based on GET query: ?uri <...#hasLocation> ?location . ?location <...#isLocatedAt> ?place
            
            loc_hash = hash_sha256(f"location-{entidad.id}")
            uri_location = f"<{URI_ONTOLOGIA}location/{loc_hash}>"
            
            triples.append(f"{uri_location} <{RDF.type}> <{URI_ONTOLOGIA}Location> .")
            triples.append(f"{sujeto} <{URI_ONTOLOGIA}hasLocation> {uri_location} .")
            triples.append(f"{uri_location} <{URI_ONTOLOGIA}isLocationOf> {sujeto} .")
            
            triples.append(f"{uri_location} <{URI_ONTOLOGIA}isLocatedAt> {uri_place} .")
            
        # 6. Address / Headquarters
        if entidad.direccion_postal:
            # Based on GET query: ?uri hasHeadquarters ?hq . ?hq isHeadquarteredAt ?site . ?site label "Address"
            hq_hash = hash_sha256(f"hq-{entidad.id}")
            uri_hq = f"<{URI_ONTOLOGIA}headquarter/{hq_hash}>"
            
            triples.append(f"{uri_hq} <{RDF.type}> <{URI_ONTOLOGIA}Headquarter> .")
            triples.append(f"{sujeto} <{URI_ONTOLOGIA}hasHeadquarters> {uri_hq} .")
            
            # The literal address
            site_hash = hash_sha256(entidad.direccion_postal)
            uri_site = f"<{URI_ONTOLOGIA}site/{site_hash}>"
            
            triples.append(f"{uri_site} <{RDF.type}> <{URI_ONTOLOGIA}Site> .")
            triples.append(f'{uri_site} <{RDFS.label}> "{escape_sparql_string(entidad.direccion_postal)}"^^<http://www.w3.org/2001/XMLSchema#string> .')
            
            triples.append(f"{uri_hq} <{URI_ONTOLOGIA}isHeadquarteredAt> {uri_site} .")

        # Build final query
        query = f"INSERT DATA\n{{\n\tGRAPH <{settings.DEFAULT_GRAPH_URL}> {{\n"
        for triple in triples:
            query += f"\t\t{triple}\n"
        query += "\t}\n}"

        return query

    @staticmethod
    def delete_institucion(uri: str) -> list:
        """Generate SPARQL DELETE queries to remove all triples for an institution."""
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
