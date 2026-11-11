from urllib.parse import quote

from rdflib import RDF, RDFS

from app.core.config import settings
from app.models.domain import Persona
from app.services.queries.base import OBJECT_PROPERTIES, PREFIXES, URI_ONTOLOGIA, uri_ontologia
from app.utils.helpers import convertir_fecha, hash_sha256, pascal_case_to_camel_case, validar_fecha, normalize_name
from app.services.queries.utils import escape_sparql_string


class PersonQueries:
    ALL_PERSONAS = f"""
        {PREFIXES}
        SELECT distinct ?uri ?label
        WHERE 
        {{
            ?uri rdf:type <https://w3id.org/OntoExhibit#Human_Actant> .
            ?uri rdfs:label ?label
        }}
        ORDER BY ?label
    """

    @staticmethod
    def get_personas_ids(limit: int, last_label: str = None, last_uri: str = None, text_search: str = None,
                         birth_place: str = None, birth_date: str = None, death_date: str = None, 
                         gender: str = None, activity: str = None, entity_type: str = None) -> str:
        
        filters = []
        inner_joins = []
        
        if text_search:
            e_text = escape_sparql_string(text_search)
            filters.append(f'(regex(?label, "{e_text}", "i") || regex(?inner_birth_place_label, "{e_text}", "i") || regex(?inner_activity, "{e_text}", "i"))')
            inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasBirth> ?birth_ts .
                    OPTIONAL { ?birth_ts <https://w3id.org/OntoExhibit#hasPlaceOfBirth> ?place_ts . ?place_ts rdfs:label ?inner_birth_place_label }
                }
            """)
            inner_joins.append("OPTIONAL { ?uri <https://w3id.org/OntoExhibit#activity_type> ?inner_activity }")
        
        if birth_place and not text_search:
            # Search in both Birth Place (individuals) and Foundation Place (groups)
            e_place = escape_sparql_string(birth_place)
            filters.append(f'(regex(?inner_birth_place_label, "{e_place}", "i") || regex(?inner_foundation_place_label, "{e_place}", "i"))')
            inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasBirth> ?birth_bp .
                    OPTIONAL { ?birth_bp <https://w3id.org/OntoExhibit#hasPlaceOfBirth> ?place_bp . ?place_bp rdfs:label ?inner_birth_place_label }
                }
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasFoundation> ?foundation_bp .
                    OPTIONAL { ?foundation_bp <https://w3id.org/OntoExhibit#hasPlaceOfFoundation> ?place_fp . ?place_fp rdfs:label ?inner_foundation_place_label }
                }
            """)

        if birth_date:
            # Search in both Birth Date (individuals) and Foundation Date (groups)
            e_date = escape_sparql_string(birth_date)
            filters.append(f'(regex(str(?inner_birth_date_label), "{e_date}", "i") || regex(str(?inner_foundation_date_label), "{e_date}", "i"))')
            inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasBirth> ?birth_bd .
                    OPTIONAL { ?birth_bd <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_bd . ?time_bd rdfs:label ?inner_birth_date_label }
                }
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasFoundation> ?foundation_bd .
                    OPTIONAL { ?foundation_bd <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_fd . ?time_fd rdfs:label ?inner_foundation_date_label }
                }
            """)
            
        if death_date:
            # Search in both Death Date (individuals) and Dissolution Date (groups)
            e_date = escape_sparql_string(death_date)
            filters.append(f'(regex(str(?inner_death_date_label), "{e_date}", "i") || regex(str(?inner_dissolution_date_label), "{e_date}", "i"))')
            inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasDeath> ?death_dd .
                    ?death_dd <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_death_dd .
                    ?time_death_dd rdfs:label ?inner_death_date_label
                }
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasDissolution> ?dissolution_dd .
                    ?dissolution_dd <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_diss_dd .
                    ?time_diss_dd rdfs:label ?inner_dissolution_date_label
                }
            """)

        if gender:
            filters.append(f'regex(?inner_gender, "^{escape_sparql_string(gender)}$", "i")')
            inner_joins.append("OPTIONAL { ?uri <https://w3id.org/OntoExhibit#gender> ?inner_gender }")

        if activity and not text_search:
            filters.append(f'regex(?inner_activity, "{escape_sparql_string(activity)}", "i")')
            inner_joins.append("OPTIONAL { ?uri <https://w3id.org/OntoExhibit#activity_type> ?inner_activity }")

        filter_clause = f"FILTER ({' && '.join(filters)})" if filters else ""
        
        pagination_filter = ""
        if last_label and last_uri:
            # Use URI-only comparison which is safe from special character issues
            pagination_filter = f"""
                FILTER (?uri > <{last_uri}>)
            """

        inner_joins_str = "\n".join(inner_joins)

        # Build type patterns based on entity_type filter
        if entity_type and entity_type.lower() == 'person':
            # Only individuals (E21_Person)
            type_patterns = """
                ?uri rdf:type <https://cidoc-crm.org/cidoc-crm/7.1.1/E21_Person> .
                ?uri rdfs:label ?label
            """
        elif entity_type and entity_type.lower() == 'group':
            # Only groups (E74_Group)
            type_patterns = """
                ?uri rdf:type <https://cidoc-crm.org/cidoc-crm/7.1.1/E74_Group> .
                ?uri rdfs:label ?label
            """
        else:
            # All types (default)
            type_patterns = """
                {
                    ?uri rdf:type <https://w3id.org/OntoExhibit#Human_Actant> .
                    ?uri rdfs:label ?label
                }
                UNION
                {
                    ?uri rdf:type <https://cidoc-crm.org/cidoc-crm/7.1.1/E21_Person> .
                    ?uri rdfs:label ?label
                }
                UNION
                {
                    ?uri rdf:type <https://cidoc-crm.org/cidoc-crm/7.1.1/E74_Group> .
                    ?uri rdfs:label ?label
                }
            """

        return f"""
            {PREFIXES}
            SELECT distinct ?uri ?label
            WHERE 
            {{
                {type_patterns}
                {inner_joins_str}
                {filter_clause}
                {pagination_filter}
            }}
            ORDER BY ?uri
            LIMIT {limit}
        """

    @staticmethod
    def get_personas_details(uris: list[str]) -> str:
        if not uris:
            return ""
        
        uris_str = " ".join([f"<{u}>" for u in uris])
        
        return f"""
            {PREFIXES}
            SELECT ?uri (SAMPLE(COALESCE(?inner_person_name, ?inner_group_name, ?inner_label, "")) as ?label) 
                   (SAMPLE(?inner_birth_place_label) as ?birth_place_label)
                   (SAMPLE(?inner_birth_date_label) as ?birth_date_label)
                   (SAMPLE(?inner_death_date_label) as ?death_date_label)
                   (SAMPLE(?inner_gender) as ?gender)
                   (GROUP_CONCAT(DISTINCT ?inner_activity; separator="|") as ?activity)
                   (SAMPLE(?inner_foundation_place_label) as ?foundation_place_label)
                   (SAMPLE(?inner_foundation_date_label) as ?foundation_date_label)
                   (SAMPLE(?inner_foundation_place_uri) as ?foundation_place_uri)
                   (SAMPLE(?inner_entity_type) as ?entity_type)
                   (SAMPLE(?inner_dissolution_date_label) as ?dissolution_date_label)
            WHERE 
            {{
                VALUES ?uri {{ {uris_str} }}
                
                OPTIONAL {{ ?uri rdfs:label ?inner_label . }}
                OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#person_name> ?inner_person_name . }}
                OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#name> ?inner_group_name . }}
                
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#hasBirth> ?birth .
                    OPTIONAL {{ 
                        ?birth <https://w3id.org/OntoExhibit#hasPlaceOfBirth> ?place .
                        ?place rdfs:label ?inner_birth_place_label 
                    }}
                    OPTIONAL {{
                        ?birth <https://w3id.org/OntoExhibit#hasTimeSpan> ?time .
                        ?time rdfs:label ?inner_birth_date_label
                    }}
                }}
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#hasDeath> ?death .
                    ?death <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_death .
                    ?time_death rdfs:label ?inner_death_date_label
                }}
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#gender> ?inner_gender
                }}
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#activity_type> ?inner_activity
                }}
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#hasFoundation> ?foundation .
                    OPTIONAL {{ 
                        ?foundation <https://w3id.org/OntoExhibit#hasPlaceOfFoundation> ?inner_foundation_place_uri .
                        ?inner_foundation_place_uri rdfs:label ?inner_foundation_place_label 
                    }}
                    OPTIONAL {{
                        ?foundation <https://w3id.org/OntoExhibit#hasTimeSpan> ?foundation_time .
                        ?foundation_time rdfs:label ?inner_foundation_date_label
                    }}
                }}
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#hasDissolution> ?dissolution .
                    ?dissolution <https://w3id.org/OntoExhibit#hasTimeSpan> ?dissolution_time .
                    ?dissolution_time rdfs:label ?inner_dissolution_date_label
                }}
                # Determine entity type
                OPTIONAL {{ ?uri rdf:type <https://cidoc-crm.org/cidoc-crm/7.1.1/E74_Group> . BIND("group" AS ?inner_entity_type) }}
            }}
            GROUP BY ?uri
        """

    GET_PERSONS_AND_GROUPS = f"""
        {PREFIXES}
        SELECT ?uri 
               (SAMPLE(COALESCE(?inner_person_name, ?inner_group_name, ?inner_label, "")) as ?label)
               (SAMPLE(?inner_label_place) as ?label_place)
               (SAMPLE(?inner_place_uri) as ?place_uri)
               (SAMPLE(?inner_label_date) as ?label_date)
               (SAMPLE(?inner_death_date) as ?death_date)
               (SAMPLE(?inner_gender) as ?gender)
               (GROUP_CONCAT(DISTINCT ?inner_activity; separator="|") as ?activity)
               (SAMPLE(?inner_residence_address) as ?residence_address)
               (SAMPLE(?inner_residence_lat) as ?residence_lat)
               (SAMPLE(?inner_residence_long) as ?residence_long)
               (SAMPLE(?inner_foundation_place_label) as ?foundation_place_label)
               (SAMPLE(?inner_foundation_date_label) as ?foundation_date_label)
               (SAMPLE(?inner_foundation_place_uri) as ?foundation_place_uri)
               (SAMPLE(?inner_entity_type) as ?entity_type)
               (SAMPLE(?inner_dissolution_date) as ?dissolution_date_label)
        WHERE 
        {{
            {{
                ?uri rdf:type <https://w3id.org/OntoExhibit#Human_Actant> .
            }}
            UNION
            {{
                ?uri rdf:type <https://cidoc-crm.org/cidoc-crm/7.1.1/E21_Person> .
            }}
            UNION
            {{
                ?uri rdf:type <https://cidoc-crm.org/cidoc-crm/7.1.1/E74_Group> .
            }}
            
            OPTIONAL {{ ?uri rdfs:label ?inner_label }}
            OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#person_name> ?inner_person_name }}
            OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#name> ?inner_group_name }}

            OPTIONAL 
            {{
                ?uri <https://w3id.org/OntoExhibit#hasBirth> ?birth .
                OPTIONAL {{
                    ?birth <https://w3id.org/OntoExhibit#hasPlaceOfBirth> ?inner_place_uri .
                    ?inner_place_uri rdfs:label ?inner_label_place
                }}
                OPTIONAL {{
                    ?birth <https://w3id.org/OntoExhibit#hasTimeSpan> ?birth_date .
                    ?birth_date rdfs:label ?inner_label_date
                }}
            }}
            OPTIONAL
            {{
                ?uri <https://w3id.org/OntoExhibit#hasDeath> ?death .
                ?death <https://w3id.org/OntoExhibit#hasTimeSpan> ?death_date_uri .
                ?death_date_uri rdfs:label ?inner_death_date
            }}
            OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#gender> ?inner_gender }}
            OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#activity_type> ?inner_activity }}
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasResidency> ?residence .
                ?residence rdf:type <https://w3id.org/OntoExhibit#Place_Of_Residence> .
                OPTIONAL {{ ?residence <https://w3id.org/OntoExhibit#address> ?inner_residence_address }}
                OPTIONAL {{ ?residence <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?inner_residence_lat }}
                OPTIONAL {{ ?residence <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?inner_residence_long }}
            }}
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasFoundation> ?foundation .
                OPTIONAL {{ 
                    ?foundation <https://w3id.org/OntoExhibit#hasPlaceOfFoundation> ?inner_foundation_place_uri .
                    ?inner_foundation_place_uri rdfs:label ?inner_foundation_place_label 
                }}
                OPTIONAL {{
                    ?foundation <https://w3id.org/OntoExhibit#hasTimeSpan> ?foundation_time .
                    ?foundation_time rdfs:label ?inner_foundation_date_label
                }}
            }}
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasDissolution> ?dissolution .
                ?dissolution <https://w3id.org/OntoExhibit#hasTimeSpan> ?dissolution_time .
                ?dissolution_time rdfs:label ?inner_dissolution_date
            }}
            # Determine entity type
            OPTIONAL {{ ?uri rdf:type <https://cidoc-crm.org/cidoc-crm/7.1.1/E74_Group> . BIND("group" AS ?inner_entity_type) }}
            FILTER (regex(str(?uri), "%s", "i"))
        }} 
        GROUP BY ?uri
        ORDER BY ?label
    """

    @staticmethod
    def get_person_collaborators(person_id: str) -> str:
        """Get all collaborators (persons and institutions) for a person, including memberships and affiliations."""
        return f"""
            {PREFIXES}
            SELECT DISTINCT ?collaborator_uri ?collaborator_label ?collaborator_type ?relationship_type
            WHERE {{
                BIND(<https://w3id.org/OntoExhibit#human_actant/{person_id}> AS ?person)
                
                # --- MEMBERSHIPS (Person <-> Group) ---
                {{
                    {{
                        # Case 1: The 'person' IS A GROUP (querying a group's members)
                        # Pattern: Group (person_id) -> hasMember -> Membership -> isMembershipOf -> Person (collaborator)
                        ?person <https://w3id.org/OntoExhibit#hasMember> ?membership .
                        ?membership <https://w3id.org/OntoExhibit#isMembershipOf> ?collaborator_uri .
                        BIND("membership" AS ?relationship_type)
                    }}
                    UNION
                    {{
                        # Case 2: The 'person' IS A PERSON (querying a person's groups)
                        # Pattern: Person (person_id) -> hasMembership -> Membership -> isMemberOf -> Group (collaborator)
                        ?person <https://w3id.org/OntoExhibit#hasMembership> ?membership .
                        ?membership <https://w3id.org/OntoExhibit#isMemberOf> ?collaborator_uri .
                        BIND("membership" AS ?relationship_type)
                    }}
                }}
                UNION
                # --- AFFILIATIONS (Person <-> Institution) ---
                {{
                    {{
                        # Person has affiliation (Person is affiliated with an Institution)
                        ?person <https://w3id.org/OntoExhibit#hasAffiliation> ?affiliation .
                        ?affiliation <https://w3id.org/OntoExhibit#isAffiliatedWith> ?collaborator_uri .
                        BIND("affiliation" AS ?relationship_type)
                    }}
                    UNION
                    {{
                         # Institution has affiliated (Institution has this person affiliated) - though query starts with person
                         ?collaborator_uri <https://w3id.org/OntoExhibit#hasAffiliated> ?affiliation .
                         ?affiliation <https://w3id.org/OntoExhibit#isAffiliationOf> ?person .
                         BIND("affiliation" AS ?relationship_type)
                    }}
                }}
                
                ?collaborator_uri rdfs:label ?collaborator_label .
                
                # Determine collaborator type
                OPTIONAL {{
                    {{ ?collaborator_uri rdf:type <https://w3id.org/OntoExhibit#Human_Actant> . BIND("person" AS ?type_person) }}
                    UNION
                    {{ ?collaborator_uri rdf:type <https://cidoc-crm.org/cidoc-crm/7.1.1/E21_Person> . BIND("person" AS ?type_person) }}
                    UNION
                    {{ ?collaborator_uri rdf:type <https://cidoc-crm.org/cidoc-crm/7.1.1/E74_Group> . BIND("group" AS ?type_group) }}
                    UNION
                    {{ ?collaborator_uri rdf:type <https://w3id.org/OntoExhibit#Institution> . BIND("institution" AS ?type_inst) }}
                    UNION
                    {{ ?collaborator_uri rdf:type <https://w3id.org/OntoExhibit#Museum> . BIND("institution" AS ?type_inst) }}
                    UNION
                    {{ ?collaborator_uri rdf:type <https://w3id.org/OntoExhibit#Cultural_Institution> . BIND("institution" AS ?type_inst) }}
                }}
                BIND(COALESCE(?type_inst, ?type_group, ?type_person, "unknown") AS ?collaborator_type)
            }}
            ORDER BY ?collaborator_label
        """

    @staticmethod
    def get_person_executive_positions(person_id: str) -> str:
        """Get institutions where this person holds an executive position."""
        return f"""
            {PREFIXES}
            SELECT DISTINCT ?institution_uri ?institution_label
            WHERE {{
                BIND(<https://w3id.org/OntoExhibit#human_actant/{person_id}> AS ?person)
                
                # Executive position links person to institution
                ?exec_position rdf:type <https://w3id.org/OntoExhibit#Executive_Position> .
                ?exec_position <https://w3id.org/OntoExhibit#isExecutivePositionOf> ?person .
                ?exec_position <https://w3id.org/OntoExhibit#executivePositionHeldsIn> ?institution_uri .
                
                ?institution_uri rdfs:label ?institution_label .
            }}
            ORDER BY ?institution_label
        """


    @staticmethod
    def get_actor_roles(actor_id: str) -> str:
        """Get all exhibitions and artworks where the actor participated in any role."""
        return f"""
            {PREFIXES}
            SELECT DISTINCT ?item_uri ?item_label ?role_type ?item_type
            WHERE {{
                BIND(<https://w3id.org/OntoExhibit#human_actant/{actor_id}> AS ?actor)
                
                # Link Actor to Role (check both directions)
                {{ ?actor <https://w3id.org/OntoExhibit#hasRole> ?role }}
                UNION
                {{ ?role <https://w3id.org/OntoExhibit#isRoleOf> ?actor }}
                
                # --- EXHIBITION ROLES ---
                {{
                    {{
                        # Exhibitor
                        {{ ?making <https://w3id.org/OntoExhibit#hasExhibitingActant> ?role }}
                        UNION
                        {{ ?role <https://w3id.org/OntoExhibit#isExhibitingActantIn> ?making }}
                        BIND("Exhibitor" AS ?role_type)
                    }}
                    UNION
                    {{
                        # Curator
                        {{ ?making <https://w3id.org/OntoExhibit#hasCurator> ?role }}
                        UNION
                        {{ ?role <https://w3id.org/OntoExhibit#isCuratorOf> ?making }}
                        BIND("Curator" AS ?role_type)
                    }}
                    UNION
                    {{
                        # Organizer
                        {{ ?making <https://w3id.org/OntoExhibit#hasOrganizer> ?role }}
                        UNION
                        {{ ?role <https://w3id.org/OntoExhibit#isOrganizerOf> ?making }}
                        BIND("Organizer" AS ?role_type)
                    }}
                    UNION
                    {{
                        # Funder
                        {{ ?making <https://w3id.org/OntoExhibit#hasFunder> ?role }}
                        UNION
                        {{ ?role <https://w3id.org/OntoExhibit#isFunderOf> ?making }}
                        BIND("Funder" AS ?role_type)
                    }}
                    UNION
                    {{
                        # Lender
                        {{ ?making <https://w3id.org/OntoExhibit#hasLender> ?role }}
                        UNION
                        {{ ?role <https://w3id.org/OntoExhibit#isLenderOf> ?making }}
                        BIND("Lender" AS ?role_type)
                    }}
                    
                    # Get the exhibition from making
                    ?making <https://w3id.org/OntoExhibit#isExhibitionMakingOf> ?item_uri .
                    BIND("exhibition" AS ?item_type)
                }}
                
                # --- ARTWORK ROLES ---
                UNION
                {{
                    # Author
                    {{
                        {{ ?prod <https://w3id.org/OntoExhibit#hasProductionAuthor> ?role }}
                        UNION
                        {{ ?role <https://w3id.org/OntoExhibit#isProductionAuthorOf> ?prod }}
                        
                        ?item_uri <https://w3id.org/OntoExhibit#hasProduction> ?prod .
                        BIND("Author" AS ?role_type)
                    }}
                    UNION
                    {{
                        # Owner
                        {{ ?item_uri <https://w3id.org/OntoExhibit#hasOwner> ?role }}
                        UNION
                        {{ ?role <https://w3id.org/OntoExhibit#isOwnerOf> ?item_uri }}
                        BIND("Owner" AS ?role_type)
                    }}
                    BIND("artwork" AS ?item_type)
                }}

                ?item_uri rdfs:label ?item_label .
            }}
            ORDER BY ?item_label
        """

    COUNT_ACTANTS = f"""
        {PREFIXES}
        SELECT (count(distinct ?uri) as ?count) WHERE 
        {{   
            {{ ?uri rdf:type <https://w3id.org/OntoExhibit#Human_Actant> }}
            UNION {{ ?uri rdf:type <https://cidoc-crm.org/cidoc-crm/7.1.1/E74_Group> }}
            UNION {{ ?uri rdf:type <https://cidoc-crm.org/cidoc-crm/7.1.1/E21_Person> }}
        }}
    """

    @staticmethod
    def add_persona(persona: Persona) -> tuple:
        POST_PERSONA = f"INSERT DATA\n\t{{\n\t\tGRAPH <{settings.DEFAULT_GRAPH_URL}> {{\n"

        if persona.type:
            if persona.type == "Individual":
                persona.type = "person"
            elif persona.type == "Group":
                persona.type = "group"
        else:
            persona.type = "human actant"

        normalized = normalize_name(persona.name)
        data_to_hash = f"{normalized} - {persona.type}"
        sujeto = f'{uri_ontologia}{quote("human_actant").lower()}/{hash_sha256(data_to_hash)}'

        if "group" == persona.type.lower():
            POST_PERSONA += (
                f"\t\t<{sujeto}> <{RDF.type}> <https://cidoc-crm.org/cidoc-crm/7.1.1/E74_Group> .\n"
            )
        elif "individual" == persona.type.lower() or "person" == persona.type.lower():
            POST_PERSONA += (
                f"\t\t<{sujeto}> <{RDF.type}> <https://cidoc-crm.org/cidoc-crm/7.1.1/E21_Person> .\n"
            )
        else:
            POST_PERSONA += f"\t\t<{sujeto}> <{RDF.type}> <{uri_ontologia}Human_Actant> .\n"

        if persona.name:
            escaped_name = escape_sparql_string(persona.name.title())
            POST_PERSONA += f'\t\t<{sujeto}> <{RDFS.label}> "{escaped_name}"^^<http://www.w3.org/2001/XMLSchema#string> .\n'
            POST_PERSONA += f'\t\t<{sujeto}> <{uri_ontologia}person_name> "{escaped_name}"^^<http://www.w3.org/2001/XMLSchema#string> .\n'

        if persona.country or persona.birth_date:
            POST_PERSONA += f"\t\t<{sujeto}> <{uri_ontologia}hasBirth> <{sujeto}/birth> .\n"
            POST_PERSONA += f"\t\t<{sujeto}/birth> <{uri_ontologia}isBirthOf> <{sujeto}> .\n"

            if persona.country:
                escaped_country = escape_sparql_string(persona.country.title())
                uri_lugar = (
                    f"{uri_ontologia}territorialEntity/{hash_sha256(persona.country.title())}"
                )
                POST_PERSONA += (
                    f"\t\t<{uri_lugar}> <{RDF.type}> <{uri_ontologia}TerritorialEntity> .\n"
                )
                POST_PERSONA += f'\t\t<{uri_lugar}> <{RDFS.label}> "{escaped_country}"^^<http://www.w3.org/2001/XMLSchema#string> .\n'
                POST_PERSONA += f"\t\t<{sujeto}/birth> <https://w3id.org/OntoExhibit#hasPlaceOfBirth> <{uri_lugar}> .\n"
                POST_PERSONA += f"\t\t<{uri_lugar}> <https://w3id.org/OntoExhibit#isPlaceOfBirthOf> <{sujeto}/birth> .\n"

            if persona.birth_date:
                fecha = validar_fecha(persona.birth_date)
                if fecha:
                    if (fecha.month == 1 and fecha.day == 1) or (
                        fecha.month == 12 and fecha.day == 31
                    ):
                        fecha_str = str(fecha.year)
                        tipo_indiv = "ApproximateDate"
                        uri_fecha = (
                            f"<{URI_ONTOLOGIA}{tipo_indiv.lower()}/{hash_sha256(fecha_str)}>"
                        )
                        POST_PERSONA += (
                            f"\t\t{uri_fecha} <{RDF.type}> <{URI_ONTOLOGIA}{tipo_indiv}> .\n"
                        )
                        POST_PERSONA += f'\t\t{uri_fecha} <{RDFS.label}> "{fecha_str}-01-01"^^<http://www.w3.org/2001/XMLSchema#date> .\n'
                    else:
                        fecha_str = fecha.strftime("%Y-%m-%d")
                        tipo_indiv = "ExactDate"
                        uri_fecha = (
                            f"<{URI_ONTOLOGIA}{tipo_indiv.lower()}/{hash_sha256(fecha_str)}>"
                        )
                        POST_PERSONA += (
                            f"\t\t{uri_fecha} <{RDF.type}> <{URI_ONTOLOGIA}{tipo_indiv}> .\n"
                        )
                        POST_PERSONA += f'\t\t{uri_fecha} <{RDFS.label}> "{fecha_str}"^^<http://www.w3.org/2001/XMLSchema#date> .\n'

                    POST_PERSONA += (
                        f"\t\t<{sujeto}/birth> <{uri_ontologia}hasTimeSpan> {uri_fecha} .\n"
                    )
                    POST_PERSONA += (
                        f"\t\t{uri_fecha} <{uri_ontologia}isTimeSpanOf> <{sujeto}/birth> .\n"
                    )

        if persona.death_date:
            POST_PERSONA += f"\t\t<{sujeto}> <{uri_ontologia}hasDeath> <{sujeto}/death> .\n"
            POST_PERSONA += f"\t\t<{sujeto}/death> <{uri_ontologia}isDeathOf> <{sujeto}> .\n"

            fecha = validar_fecha(persona.death_date)
            if fecha:
                if (fecha.month == 1 and fecha.day == 1) or (fecha.month == 12 and fecha.day == 31):
                    fecha_str = str(fecha.year)
                    tipo_indiv = "ApproximateDate"
                    uri_fecha = f"<{URI_ONTOLOGIA}{tipo_indiv.lower()}/{hash_sha256(fecha_str)}>"
                    POST_PERSONA += (
                        f"\t\t{uri_fecha} <{RDF.type}> <{URI_ONTOLOGIA}{tipo_indiv}> .\n"
                    )
                    POST_PERSONA += f'\t\t{uri_fecha} <{RDFS.label}> "{fecha_str}-01-01"^^<http://www.w3.org/2001/XMLSchema#date> .\n'
                else:
                    fecha_str = fecha.strftime("%Y-%m-%d")
                    tipo_indiv = "ExactDate"
                    uri_fecha = f"<{URI_ONTOLOGIA}{tipo_indiv.lower()}/{hash_sha256(fecha_str)}>"
                    POST_PERSONA += (
                        f"\t\t{uri_fecha} <{RDF.type}> <{URI_ONTOLOGIA}{tipo_indiv}> .\n"
                    )
                    POST_PERSONA += f'\t\t{uri_fecha} <{RDFS.label}> "{fecha_str}"^^<http://www.w3.org/2001/XMLSchema#date> .\n'

                POST_PERSONA += f"\t\t<{sujeto}/death> <{uri_ontologia}hasTimeSpan> {uri_fecha} .\n"
                POST_PERSONA += (
                    f"\t\t{uri_fecha} <{uri_ontologia}isTimeSpanOf> <{sujeto}/death> .\n"
                )

        if persona.activity:
            if isinstance(persona.activity, list):
                for act in persona.activity:
                    POST_PERSONA += f'\t\t<{sujeto}> <https://w3id.org/OntoExhibit#activity_type> "{escape_sparql_string(act)}"^^<http://www.w3.org/2001/XMLSchema#string> .\n'
            else:
                POST_PERSONA += f'\t\t<{sujeto}> <https://w3id.org/OntoExhibit#activity_type> "{escape_sparql_string(persona.activity)}"^^<http://www.w3.org/2001/XMLSchema#string> .\n'

        if persona.gender:
            POST_PERSONA += f'\t\t<{sujeto}> <https://w3id.org/OntoExhibit#gender> "{escape_sparql_string(persona.gender)}"^^<http://www.w3.org/2001/XMLSchema#string> .\n'

        POST_PERSONA += "\t}\n}"
        uri = f"https://w3id.org/OntoExhibit#{quote('human_actant').lower()}/{hash_sha256(data_to_hash)}"
        return POST_PERSONA, uri

    @staticmethod
    def delete_persona(uri: str) -> list:
        """Generate SPARQL DELETE queries to remove all triples for a person.
        
        Args:
            uri: The full URI of the person to delete
            
        Returns:
            List of SPARQL DELETE query strings to execute in order
        """
        # Clean up the URI - remove any surrounding brackets if present
        clean_uri = uri.strip().lstrip('<').rstrip('>')
        graph_url = settings.DEFAULT_GRAPH_URL
        
        queries = []
        
        # Delete all triples where this entity is the subject
        queries.append(f"""
            WITH <{graph_url}>
            DELETE {{
                <{clean_uri}> ?p ?o .
            }}
            WHERE {{
                <{clean_uri}> ?p ?o .
            }}
        """)
        
        # Delete all triples where this entity is the object
        queries.append(f"""
            WITH <{graph_url}>
            DELETE {{
                ?s ?p <{clean_uri}> .
            }}
            WHERE {{
                ?s ?p <{clean_uri}> .
            }}
        """)
        
        # Delete birth-related triples
        queries.append(f"""
            WITH <{graph_url}>
            DELETE {{
                <{clean_uri}/birth> ?p ?o .
            }}
            WHERE {{
                <{clean_uri}/birth> ?p ?o .
            }}
        """)
        
        # Delete death-related triples
        queries.append(f"""
            WITH <{graph_url}>
            DELETE {{
                <{clean_uri}/death> ?p ?o .
            }}
            WHERE {{
                <{clean_uri}/death> ?p ?o .
            }}
        """)
        
        return queries
