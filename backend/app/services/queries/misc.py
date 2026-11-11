from typing import Optional

from app.services.queries.base import PREFIXES
from app.services.queries.utils import escape_sparql_string


class MiscQueries:
    ALL_CLASSES = f"""
        {PREFIXES}
        SELECT DISTINCT ?class ?label
        WHERE {{
            ?s a ?class .
            OPTIONAL {{ ?class rdfs:label ?label . FILTER (lang(?label) = "en") }}
        }}
    """

    @staticmethod
    def semantic_search(q: str, limit: int = 40, entity_type: Optional[str] = None) -> str:
        phrase = escape_sparql_string(q.strip().lower())
        terms = [
            escape_sparql_string(term.lower())
            for term in q.split()
            if len(term.strip()) > 1
        ][:6]

        if not terms and phrase:
            terms = [phrase]

        term_filters = " && ".join(
            f'CONTAINS(LCASE(?match_search_text), "{term}")' for term in terms
        )
        filter_clause = f"FILTER ({term_filters})" if term_filters else ""
        safe_limit = max(1, min(limit, 100))

        type_values = """
            (<https://w3id.org/OntoExhibit#Exhibition> "exhibition" "Exhibition")
            (<https://w3id.org/OntoExhibit#Work_Manifestation> "artwork" "Artwork")
            (<https://w3id.org/OntoExhibit#Institution> "institution" "Institution")
            (<https://w3id.org/OntoExhibit#Person> "actant" "Actor")
            (<https://w3id.org/OntoExhibit#Group> "actant" "Actor")
            (<https://w3id.org/OntoExhibit#Human_Actant> "actant" "Actor")
            (<https://w3id.org/OntoExhibit#Company> "company" "Company")
            (<https://w3id.org/OntoExhibit#Catalog> "catalog" "Catalog")
        """

        if entity_type:
            normalized_type = escape_sparql_string(entity_type.lower())
            entity_type_filter = f'FILTER (?ui_type = "{normalized_type}")'
            literal_branch = f"""
                UNION
                {{
                    ?uri rdf:type/rdfs:subClassOf* ?root_type .
                    ?uri ?predicate ?literal_value .
                    FILTER(isLiteral(?literal_value))
                    FILTER(?predicate != rdfs:label)
                    BIND(REPLACE(STR(?predicate), "^.*[/#]", "") AS ?predicate_name)
                    BIND(?predicate_name AS ?match_field)
                    BIND(STR(?literal_value) AS ?match_value)
                    BIND(CONCAT(STR(?literal_value), " ", ?predicate_name, " ", STR(?uri), " ", ?label_type) AS ?match_search_text)
                    BIND(55 AS ?base_score)
                    {filter_clause}
                }}
            """
            relationship_branches = f"""
                UNION
                {{
                    ?uri rdf:type/rdfs:subClassOf* ?root_type .
                    ?uri ?predicate ?related .
                    ?related rdfs:label ?related_label .
                    FILTER(?predicate != rdf:type)
                    BIND(REPLACE(STR(?predicate), "^.*[/#]", "") AS ?predicate_name)
                    BIND(CONCAT("Related ", ?predicate_name) AS ?match_field)
                    BIND(STR(?related_label) AS ?match_value)
                    BIND(CONCAT(STR(?related_label), " ", ?predicate_name, " ", STR(?uri), " ", ?label_type) AS ?match_search_text)
                    BIND(70 AS ?base_score)
                    {filter_clause}
                }}
                UNION
                {{
                    ?uri rdf:type/rdfs:subClassOf* ?root_type .
                    ?related ?predicate ?uri .
                    ?related rdfs:label ?related_label .
                    FILTER(?predicate != rdf:type)
                    BIND(REPLACE(STR(?predicate), "^.*[/#]", "") AS ?predicate_name)
                    BIND(CONCAT("Linked by ", ?predicate_name) AS ?match_field)
                    BIND(STR(?related_label) AS ?match_value)
                    BIND(CONCAT(STR(?related_label), " ", ?predicate_name, " ", STR(?uri), " ", ?label_type) AS ?match_search_text)
                    BIND(45 AS ?base_score)
                    {filter_clause}
                }}
            """
        else:
            entity_type_filter = ""
            literal_branch = ""
            relationship_branches = ""

        return f"""
            {PREFIXES}
            SELECT ?uri ?type ?label ?label_type
                   (SAMPLE(?match_field) AS ?matched_property)
                   (SAMPLE(?match_value) AS ?matched_label)
                   (MAX(?weighted_score) AS ?score)
            WHERE {{
                VALUES (?root_type ?type ?label_type) {{
                    {type_values}
                }}

                BIND(?type AS ?ui_type)
                {entity_type_filter}

                {{
                    ?uri rdf:type/rdfs:subClassOf* ?root_type .
                    ?uri rdfs:label ?match_value .
                    BIND("Name or title" AS ?match_field)
                    BIND(CONCAT(STR(?match_value), " ", STR(?uri), " ", ?label_type) AS ?match_search_text)
                    BIND(100 AS ?base_score)
                    {filter_clause}
                }}
                UNION
                {{
                    ?uri rdf:type/rdfs:subClassOf* ?root_type .
                    ?uri <https://w3id.org/OntoExhibit#hasTitle> ?title_node .
                    ?title_node rdfs:label ?match_value .
                    BIND("Name or title" AS ?match_field)
                    BIND(CONCAT(STR(?match_value), " ", STR(?uri), " ", ?label_type) AS ?match_search_text)
                    BIND(100 AS ?base_score)
                    {filter_clause}
                }}
                {literal_branch}
                {relationship_branches}

                OPTIONAL {{ ?uri rdfs:label ?direct_label . }}
                OPTIONAL {{
                    ?uri <https://w3id.org/OntoExhibit#hasTitle> ?title_node_for_label .
                    ?title_node_for_label rdfs:label ?title_label .
                }}
                BIND(COALESCE(?title_label, ?direct_label, ?match_value, REPLACE(STR(?uri), "^.*[/#]", "")) AS ?label)
                BIND(IF(CONTAINS(LCASE(?match_search_text), "{phrase}"), ?base_score + 20, ?base_score) AS ?weighted_score)
            }}
            GROUP BY ?uri ?type ?label ?label_type
            ORDER BY DESC(?score) LCASE(?label)
            LIMIT {safe_limit}
        """

    GET_OBJECT_ANY_TYPE = f"""
        {PREFIXES}
        SELECT DISTINCT ?p ?o
        WHERE {{
            {{
                # Direct properties
                <https://w3id.org/OntoExhibit#%s/%s> ?p ?o .
            }}
            UNION
            {{
                # Synthesize label from person_name if available and direct label missing (optional)
                BIND(rdfs:label AS ?p)
                <https://w3id.org/OntoExhibit#%s/%s> <https://w3id.org/OntoExhibit#person_name> ?o .
            }}
            UNION
            {{
                # Synthesize label from hasTitle -> label if available
                BIND(rdfs:label AS ?p)
                <https://w3id.org/OntoExhibit#%s/%s> <https://w3id.org/OntoExhibit#hasTitle> ?title_entity .
                ?title_entity rdfs:label ?o .
            }}
        }}
    """

    GET_DISTINCT_GENDERS = f"""
        {PREFIXES}
        SELECT DISTINCT ?value WHERE {{
            ?s <https://w3id.org/OntoExhibit#gender> ?value .
        }} ORDER BY ?value
    """

    GET_DISTINCT_ACTIVITIES = f"""
        {PREFIXES}
        SELECT DISTINCT ?value WHERE {{
            ?s <https://w3id.org/OntoExhibit#activity_type> ?value .
        }} ORDER BY ?value
    """
    
    GET_DISTINCT_ARTWORK_TYPES = f"""
        {PREFIXES}
        SELECT DISTINCT ?value WHERE {{
            ?s rdf:type <https://w3id.org/OntoExhibit#Work_Manifestation> .
            ?s <https://w3id.org/OntoExhibit#type> ?value .
        }} ORDER BY ?value
    """
    
    GET_DISTINCT_TOPICS = f"""
        {PREFIXES}
        SELECT DISTINCT ?value WHERE {{
            ?s rdf:type <https://w3id.org/OntoExhibit#Work_Manifestation> .
            ?s <https://w3id.org/OntoExhibit#hasTheme> ?t .
            ?t rdfs:label ?value .
        }} ORDER BY ?value
    """

    GET_DISTINCT_EXHIBITION_TYPES = f"""
        {PREFIXES}
        SELECT DISTINCT ?value WHERE {{
            ?s rdf:type <https://w3id.org/OntoExhibit#Exhibition> .
            ?s <https://w3id.org/OntoExhibit#type> ?value .
        }} ORDER BY ?value
    """

    GET_DISTINCT_EXHIBITION_THEMES = f"""
        {PREFIXES}
        SELECT DISTINCT ?value WHERE {{
            ?s rdf:type <https://w3id.org/OntoExhibit#Exhibition> .
            ?s <https://w3id.org/OntoExhibit#hasTheme> ?t .
            ?t rdfs:label ?value .
        }} ORDER BY ?value
    """

    # Institution types - hardcoded list with labels
    GET_INSTITUTION_TYPES = f"""
        {PREFIXES}
        SELECT DISTINCT ?value WHERE {{
            VALUES (?type_class) {{
                (<https://w3id.org/OntoExhibit#Cultural_Institution>)
                (<https://w3id.org/OntoExhibit#Academy_Of_Fine_Arts>)
                (<https://w3id.org/OntoExhibit#Archive>)
                (<https://w3id.org/OntoExhibit#Art_Center>)
                (<https://w3id.org/OntoExhibit#Cultural_Center>)
                (<https://w3id.org/OntoExhibit#ExhibitionSpace>)
                (<https://w3id.org/OntoExhibit#Foundation_(Institution)>)
                (<https://w3id.org/OntoExhibit#Interpretation_Center>)
                (<https://w3id.org/OntoExhibit#Library>)
                (<https://w3id.org/OntoExhibit#Museographic_Collection>)
                (<https://w3id.org/OntoExhibit#Museum>)
                (<https://w3id.org/OntoExhibit#Educational_Institution>)
                (<https://w3id.org/OntoExhibit#Art_School>)
                (<https://w3id.org/OntoExhibit#University>)
            }}
            ?type_class rdfs:label ?value .
        }} ORDER BY ?value
    """

    GET_COMPANY_ISIC4_CATEGORIES = f"""
        {PREFIXES}
        SELECT DISTINCT ?value WHERE {{
            ?s rdf:type <https://w3id.org/OntoExhibit#Company> .
            ?s <https://w3id.org/OntoExhibit#ISIC4Category> ?value .
            FILTER(STRLEN(STR(?value)) > 0)
        }} ORDER BY ?value
    """

    GET_COMPANY_SIZES = f"""
        {PREFIXES}
        SELECT DISTINCT ?value WHERE {{
            ?s rdf:type <https://w3id.org/OntoExhibit#Company> .
            ?s <https://w3id.org/OntoExhibit#size> ?value .
            FILTER(STRLEN(STR(?value)) > 0)
        }} ORDER BY ?value
    """
