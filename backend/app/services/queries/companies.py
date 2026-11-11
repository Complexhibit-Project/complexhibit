"""
Company SPARQL queries.

Provides SPARQL queries for company entity operations including
listing, detail retrieval, and museographer role relationships.
"""

from app.services.queries.base import PREFIXES
from app.services.queries.utils import escape_sparql_string


class CompanyQueries:
    COUNT_COMPANIES = f"""
        {PREFIXES}
        SELECT (count(distinct ?uri) as ?count) WHERE 
        {{   
            ?uri rdf:type <https://w3id.org/OntoExhibit#Company> .
        }}
    """

    @staticmethod
    def get_companies_ids(
        limit: int,
        last_label: str = None,
        last_uri: str = None,
        text_search: str = None,
        isic4_category: str = None,
        size: str = None,
        location: str = None,
    ) -> str:
        filters = []
        joins = ["?uri rdfs:label ?label ."]

        if text_search:
            escaped = escape_sparql_string(text_search)
            filters.append(f'regex(?label, "{escaped}", "i")')

        if isic4_category:
            escaped = escape_sparql_string(isic4_category)
            joins.append('OPTIONAL { ?uri <https://w3id.org/OntoExhibit#ISIC4Category> ?inner_isic }')
            filters.append(f'regex(?inner_isic, "{escaped}", "i")')

        if size:
            escaped = escape_sparql_string(size)
            joins.append('OPTIONAL { ?uri <https://w3id.org/OntoExhibit#size> ?inner_size }')
            filters.append(f'regex(?inner_size, "{escaped}", "i")')

        if location:
            escaped = escape_sparql_string(location)
            joins.append("""
                OPTIONAL {
                    ?uri <https://w3id.org/OntoExhibit#hasLocation> ?inner_location .
                    ?inner_location <https://w3id.org/OntoExhibit#hasPlaceOfLocation> ?inner_location_uri .
                    ?inner_location_uri rdfs:label ?inner_location_label .
                }
            """)
            filters.append(f'regex(?inner_location_label, "{escaped}", "i")')

        filter_clause = f"FILTER ({' && '.join(filters)})" if filters else ""
        joins_str = "\n".join(joins)
        
        pagination_filter = ""
        if last_label and last_uri:
            pagination_filter = f"""
                FILTER (?uri > <{last_uri}>)
            """

        return f"""
            {PREFIXES}
            SELECT DISTINCT ?label ?uri
            WHERE 
            {{
                ?uri rdf:type <https://w3id.org/OntoExhibit#Company> .
                {joins_str}
                
                {filter_clause}
                {pagination_filter}
            }} 
            ORDER BY ?uri
            LIMIT {limit}
        """

    @staticmethod
    def get_companies_details(uris: list[str]) -> str:
        if not uris:
            return ""
        
        uris_str = " ".join([f"<{u}>" for u in uris])
        
        return f"""
            {PREFIXES}
            SELECT ?uri (SAMPLE(?inner_label) as ?label) 
                   (SAMPLE(?inner_isic) as ?isic4_category)
                   (SAMPLE(?inner_size) as ?size)
                   (SAMPLE(?inner_place_label) as ?location_label)
                   (SAMPLE(?inner_place_uri) as ?location_uri)
            WHERE 
            {{
                VALUES ?uri {{ {uris_str} }}
                
                ?uri rdfs:label ?inner_label .

                OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#ISIC4Category> ?inner_isic }}
                OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#size> ?inner_size }}
                OPTIONAL {{ 
                    ?uri <https://w3id.org/OntoExhibit#hasLocation> ?location .
                    ?location <https://w3id.org/OntoExhibit#hasPlaceOfLocation> ?inner_place_uri .
                    ?inner_place_uri rdfs:label ?inner_place_label
                }}
            }} 
            GROUP BY ?uri
        """

    GET_COMPANY = f"""
        {PREFIXES}
        SELECT DISTINCT ?label ?uri ?isic4_category ?size ?location_label ?location_uri
        WHERE 
        {{
            ?uri rdf:type <https://w3id.org/OntoExhibit#Company> .
            ?uri rdfs:label ?label .
            
            FILTER (regex(str(?uri), "%s", "i"))

            OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#ISIC4Category> ?isic4_category }}
            OPTIONAL {{ ?uri <https://w3id.org/OntoExhibit#size> ?size }}
            OPTIONAL {{ 
                ?uri <https://w3id.org/OntoExhibit#hasLocation> ?location .
                ?location <https://w3id.org/OntoExhibit#hasPlaceOfLocation> ?location_uri .
                ?location_uri rdfs:label ?location_label
            }}
        }}
    """

    @staticmethod
    def get_museographer_exhibitions(company_id: str) -> str:
        """Get exhibitions where this company was the museographer."""
        return f"""
            {PREFIXES}
            SELECT DISTINCT ?exhibition_uri ?exhibition_label ?start_date
            WHERE {{
                BIND(<https://w3id.org/OntoExhibit#company/{company_id}> AS ?company)
                
                # 1. Company <-> Role (Support both directions)
                {{ ?museographer_role <https://w3id.org/OntoExhibit#isRoleOf> ?company }}
                UNION
                {{ ?company <https://w3id.org/OntoExhibit#hasRole> ?museographer_role }}
                
                # 2. Role <-> Making (Support both directions)
                {{ ?museographer_role <https://w3id.org/OntoExhibit#isMuseographerOf> ?making }}
                UNION
                {{ ?making <https://w3id.org/OntoExhibit#hasMuseographer> ?museographer_role }}
                
                # 3. Making <-> Exhibition (Support both directions)
                {{ ?making <https://w3id.org/OntoExhibit#isExhibitionMakingOf> ?exhibition_uri }}
                UNION
                {{ ?exhibition_uri <https://w3id.org/OntoExhibit#hasExhibitionMaking> ?making }}
                
                ?exhibition_uri rdf:type <https://w3id.org/OntoExhibit#Exhibition> .
                ?exhibition_uri rdfs:label ?exhibition_label .
                
                OPTIONAL {{
                    ?exhibition_uri <https://w3id.org/OntoExhibit#hasOpening> ?opening .
                    ?opening <https://w3id.org/OntoExhibit#hasTimeSpan> ?time_opening .
                    ?time_opening rdfs:label ?start_date
                }}
            }}
            ORDER BY ?exhibition_label
        """
