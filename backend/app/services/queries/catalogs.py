"""
Catalog queries for SPARQL operations.

Provides queries for fetching catalog (inscription devices/documentation resources) data.
"""

from app.services.queries.base import PREFIXES
from app.services.queries.utils import escape_sparql_string


class CatalogQueries:
    """SPARQL queries for catalog entities."""

    COUNT_CATALOGS = f"""
        {PREFIXES}
        SELECT (count(distinct ?uri) as ?count) WHERE 
        {{   
            ?uri rdf:type <https://w3id.org/OntoExhibit#Catalog> .
        }}
    """

    @staticmethod
    def get_catalogs_ids(
        limit: int,
        last_label: str = None,
        last_uri: str = None,
        text_search: str = None,
        publication_date: str = None,
        publication_place: str = None,
        producer: str = None,
        exhibition: str = None,
    ) -> str:
        filters = []
        inner_joins = []
        
        inner_joins.append("?uri rdfs:label ?inner_label .")
        
        if text_search:
            escaped = escape_sparql_string(text_search)
            filters.append(f'regex(?inner_label, "{escaped}", "i")')

        if publication_date:
            escaped = escape_sparql_string(publication_date)
            inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasPublication> ?inner_publication .
                    ?inner_publication <https://w3id.org/OntoExhibit#hasTimeSpan> ?inner_timespan .
                    ?inner_timespan rdfs:label ?inner_publication_date .
                }
            """)
            filters.append(f'regex(str(?inner_publication_date), "{escaped}", "i")')

        if publication_place:
            escaped = escape_sparql_string(publication_place)
            inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasPublication> ?inner_publication_place_node .
                    ?inner_publication_place_node <https://w3id.org/OntoExhibit#hasPlaceOfPublication> ?inner_publication_place_uri .
                    ?inner_publication_place_uri rdfs:label ?inner_publication_place .
                }
            """)
            filters.append(f'regex(?inner_publication_place, "{escaped}", "i")')

        if producer:
            escaped = escape_sparql_string(producer)
            inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasProduction> ?inner_production .
                    ?inner_production <https://w3id.org/OntoExhibit#hasProducer> ?inner_producer_role .
                    ?inner_producer_uri <https://w3id.org/OntoExhibit#hasRole> ?inner_producer_role .
                    ?inner_producer_uri rdfs:label ?inner_producer_label .
                }
            """)
            filters.append(f'regex(?inner_producer_label, "{escaped}", "i")')

        if exhibition:
            escaped = escape_sparql_string(exhibition)
            inner_joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#servesAsDocumentationResourceOf> ?inner_doc_dispositif .
                    ?inner_doc_dispositif <https://w3id.org/OntoExhibit#isDocumentationDispositifOf> ?inner_exhibition_uri .
                    ?inner_exhibition_uri rdfs:label ?inner_exhibition_label .
                }
            """)
            filters.append(f'regex(?inner_exhibition_label, "{escaped}", "i")')
        
        filter_clause = f"FILTER ({' && '.join(filters)})" if filters else ""
        
        pagination_filter = ""
        if last_label and last_uri:
            pagination_filter = f"""
                FILTER (?uri > <{last_uri}>)
            """

        inner_joins_str = "\n".join(inner_joins)

        return f"""
            {PREFIXES}
            SELECT DISTINCT ?uri ?inner_label
            WHERE 
            {{
                ?uri rdf:type <https://w3id.org/OntoExhibit#Catalog> .
                {inner_joins_str}
                {filter_clause}
                {pagination_filter}
            }} 
            ORDER BY ?uri
            LIMIT {limit}
        """

    @staticmethod
    def get_catalogs_details(uris: list[str]) -> str:
        if not uris:
            return ""
        
        uris_str = " ".join([f"<{u}>" for u in uris])
        
        return f"""
            {PREFIXES}
            SELECT ?uri (SAMPLE(?inner_label) as ?label) 
                   (SAMPLE(?inner_publication_date) as ?publication_date)
                   (SAMPLE(?inner_publication_place) as ?publication_place)
                   (GROUP_CONCAT(DISTINCT CONCAT(?inner_producer, ":::", STR(?producer_uri)); separator="|") as ?producers)
                   (GROUP_CONCAT(DISTINCT CONCAT(?inner_exhibition, ":::", STR(?exhibition_uri)); separator="|") as ?exhibitions)
            WHERE 
            {{
                VALUES ?uri {{ {uris_str} }}
                
                OPTIONAL {{ ?uri rdfs:label ?inner_label . }}
                
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#hasPublication> ?publication .
                    OPTIONAL {{ 
                        ?publication <https://w3id.org/OntoExhibit#hasTimeSpan> ?timespan .
                        ?timespan rdfs:label ?inner_publication_date .
                    }}
                    OPTIONAL {{ 
                        ?publication <https://w3id.org/OntoExhibit#hasPlaceOfPublication> ?place_uri .
                        ?place_uri rdfs:label ?inner_publication_place .
                    }}
                }}
                
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#hasProduction> ?production .
                    ?production <https://w3id.org/OntoExhibit#hasProducer> ?producer_role .
                    ?producer_uri <https://w3id.org/OntoExhibit#hasRole> ?producer_role .
                    ?producer_uri rdfs:label ?inner_producer .
                }}
                
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#servesAsDocumentationResourceOf> ?doc_dispositif .
                    ?doc_dispositif <https://w3id.org/OntoExhibit#isDocumentationDispositifOf> ?exhibition_uri .
                    ?exhibition_uri rdfs:label ?inner_exhibition .
                }}
            }} 
            GROUP BY ?uri
        """

    GET_CATALOG_BY_ID = f"""
        {PREFIXES}
        SELECT DISTINCT ?uri ?label ?publication_date ?publication_place_label ?publication_place_uri
        WHERE {{
            BIND(<https://w3id.org/OntoExhibit#catalog/%s> AS ?uri)
            
            ?uri rdfs:label ?label .
            
            # Publication info via hasPublication
            OPTIONAL {{
                ?uri <https://w3id.org/OntoExhibit#hasPublication> ?publication .
                # Publication date via hasTimeSpan -> approximate_date -> label
                OPTIONAL {{ 
                    ?publication <https://w3id.org/OntoExhibit#hasTimeSpan> ?timespan .
                    ?timespan rdfs:label ?publication_date .
                }}
                OPTIONAL {{ 
                    ?publication <https://w3id.org/OntoExhibit#hasPlaceOfPublication> ?publication_place_uri .
                    ?publication_place_uri rdfs:label ?publication_place_label .
                }}
            }}
        }}
    """

    GET_CATALOG_EXHIBITIONS = f"""
        {PREFIXES}
        SELECT DISTINCT ?exhibition_uri ?exhibition_label
        WHERE {{
            BIND(<https://w3id.org/OntoExhibit#catalog/%s> AS ?catalog_uri)
            
            # Catalog serves as documentation resource of a dispositif
            ?catalog_uri <https://w3id.org/OntoExhibit#servesAsDocumentationResourceOf> ?doc_dispositif .
            # The dispositif is of an exhibition
            ?doc_dispositif <https://w3id.org/OntoExhibit#isDocumentationDispositifOf> ?exhibition_uri .
            ?exhibition_uri rdfs:label ?exhibition_label .
        }}
    """

    GET_CATALOG_PRODUCERS = f"""
        {PREFIXES}
        SELECT DISTINCT ?producer_uri ?producer_label ?producer_type
        WHERE {{
            BIND(<https://w3id.org/OntoExhibit#catalog/%s> AS ?catalog_uri)
            
            ?catalog_uri <https://w3id.org/OntoExhibit#hasProduction> ?production .
            ?production <https://w3id.org/OntoExhibit#hasProducer> ?producer_role .
            
            # Get the actant that has this producer role
            ?actant_uri <https://w3id.org/OntoExhibit#hasRole> ?producer_role .
            ?actant_uri rdfs:label ?producer_label .
            BIND(?actant_uri AS ?producer_uri)
            
            # Determine type
            OPTIONAL {{
                ?actant_uri rdf:type ?type_uri .
                FILTER(?type_uri IN (
                    <https://w3id.org/OntoExhibit#Human_Actant>,
                    <https://cidoc-crm.org/cidoc-crm/7.1.1/E21_Person>,
                    <https://w3id.org/OntoExhibit#Institution>,
                    <https://cidoc-crm.org/cidoc-crm/7.1.1/E74_Group>
                ))
                BIND(IF(?type_uri = <https://w3id.org/OntoExhibit#Institution> || 
                        ?type_uri = <https://cidoc-crm.org/cidoc-crm/7.1.1/E74_Group>, 
                        "institution", "actant") AS ?producer_type)
            }}
        }}
    """

    GET_EXHIBITION_CATALOGS = f"""
        {PREFIXES}
        SELECT DISTINCT ?catalog_uri ?catalog_label
        WHERE {{
            BIND(<https://w3id.org/OntoExhibit#exhibition/%s> AS ?exhibition_uri)
            
            # Exhibition -> DocumentationDispositif -> Catalog
            ?exhibition_uri <https://w3id.org/OntoExhibit#hasDocumentationDispositif> ?doc_dispositif .
            ?doc_dispositif <https://w3id.org/OntoExhibit#hasDocumentationResource> ?catalog_uri .
            ?catalog_uri rdfs:label ?catalog_label .
        }}
    """

    GET_PRODUCER_CATALOGS = f"""
        {PREFIXES}
        SELECT DISTINCT ?catalog_uri ?catalog_label ?exhibition_uri ?exhibition_label
        WHERE {{
            # Find any entity (human_actant or institution) whose URI ends with the given ID
            ?actant_uri <https://w3id.org/OntoExhibit#hasRole> ?producer_role .
            FILTER(STRENDS(STR(?actant_uri), "/%s"))
            
            # The producer role is linked to a production
            ?producer_role <https://w3id.org/OntoExhibit#isProducerOf> ?production .
            
            # The production is for a catalog
            ?production <https://w3id.org/OntoExhibit#isProductionOf> ?catalog_uri .
            ?catalog_uri rdfs:label ?catalog_label .
            
            # Optionally get the related exhibition
            OPTIONAL {{
                ?catalog_uri <https://w3id.org/OntoExhibit#servesAsDocumentationResourceOf> ?doc_dispositif .
                ?doc_dispositif <https://w3id.org/OntoExhibit#isDocumentationDispositifOf> ?exhibition_uri .
                ?exhibition_uri rdfs:label ?exhibition_label .
            }}
        }}
    """
