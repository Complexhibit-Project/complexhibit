/**
 * Example SPARQL queries for the Complexhibit Knowledge Graph.
 * 
 * These queries work with the OntoExhibit ontology.
 * URI base: https://w3id.org/OntoExhibit#
 */

export interface ExampleQuery {
  id: string;
  name: string;
  description: string;
  query: string;
  category: 'exhibitions' | 'artworks' | 'persons' | 'institutions' | 'advanced';
}

/** Common prefixes used in SPARQL queries */
const PREFIXES = `PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ontoex: <https://w3id.org/OntoExhibit#>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>`;

export const exampleQueries: ExampleQuery[] = [
  // ===== Exhibitions =====
  {
    id: 'exhibitions-list',
    name: 'List All Exhibitions',
    description: 'Retrieves all exhibitions with their labels (limited to 100)',
    category: 'exhibitions',
    query: `${PREFIXES}

SELECT ?exhibition ?label
WHERE {
  ?exhibition rdf:type ontoex:Exhibition .
  OPTIONAL { ?exhibition rdfs:label ?label }
}
ORDER BY ?label
LIMIT 100`
  },
  {
    id: 'exhibitions-with-dates',
    name: 'Exhibitions with Dates',
    description: 'Lists exhibitions with their opening and closing dates',
    category: 'exhibitions',
    query: `${PREFIXES}

SELECT ?exhibition ?label ?opening_date ?closing_date
WHERE {
  ?exhibition rdf:type ontoex:Exhibition .
  OPTIONAL { 
    ?exhibition rdfs:label ?direct_label 
  }
  OPTIONAL { 
    ?exhibition ontoex:hasTitle ?title .
    ?title rdfs:label ?title_label 
  }
  BIND(COALESCE(?title_label, ?direct_label, "Unknown") AS ?label)
  
  OPTIONAL { 
    ?exhibition ontoex:hasOpening ?opening .
    ?opening ontoex:hasTimeSpan ?opening_ts .
    ?opening_ts rdfs:label ?opening_date 
  }
  OPTIONAL { 
    ?exhibition ontoex:hasClosing ?closing .
    ?closing ontoex:hasTimeSpan ?closing_ts .
    ?closing_ts rdfs:label ?closing_date 
  }
}
ORDER BY ?opening_date
LIMIT 100`
  },
  {
    id: 'exhibitions-by-place',
    name: 'Exhibitions by Location',
    description: 'Lists exhibitions grouped by their location',
    category: 'exhibitions',
    query: `${PREFIXES}

SELECT ?place_label (COUNT(?exhibition) AS ?count)
WHERE {
  ?exhibition rdf:type ontoex:Exhibition .
  ?exhibition ontoex:takesPlaceAt ?place .
  ?place rdfs:label ?place_label .
}
GROUP BY ?place_label
ORDER BY DESC(?count)
LIMIT 50`
  },

  // ===== Artworks =====
  {
    id: 'artworks-list',
    name: 'List All Artworks',
    description: 'Retrieves all artworks with their labels',
    category: 'artworks',
    query: `${PREFIXES}

SELECT ?artwork ?label
WHERE {
  ?artwork rdf:type ontoex:Artwork .
  OPTIONAL { ?artwork rdfs:label ?label }
}
ORDER BY ?label
LIMIT 100`
  },
  {
    id: 'artworks-exhibited',
    name: 'Artworks and Their Exhibitions',
    description: 'Shows artworks and the exhibitions where they were displayed',
    category: 'artworks',
    query: `${PREFIXES}

SELECT ?artwork ?artwork_label ?exhibition ?exhibition_label
WHERE {
  ?exhibition rdf:type ontoex:Exhibition .
  ?exhibition ontoex:displays ?artwork .
  OPTIONAL { ?artwork rdfs:label ?artwork_label }
  OPTIONAL { ?exhibition rdfs:label ?exhibition_label }
}
ORDER BY ?artwork_label
LIMIT 100`
  },

  // ===== Persons =====
  {
    id: 'persons-list',
    name: 'List All Persons',
    description: 'Retrieves all persons registered in the knowledge graph',
    category: 'persons',
    query: `${PREFIXES}

SELECT ?person ?label
WHERE {
  ?person rdf:type ontoex:HumanActant .
  OPTIONAL { ?person rdfs:label ?label }
}
ORDER BY ?label
LIMIT 100`
  },
  {
    id: 'curators',
    name: 'Exhibition Curators',
    description: 'Lists curators and the exhibitions they curated',
    category: 'persons',
    query: `${PREFIXES}

SELECT ?person ?person_label ?exhibition ?exhibition_label
WHERE {
  ?exhibition rdf:type ontoex:Exhibition .
  ?exhibition ontoex:hasExhibitionMaking ?making .
  ?making ontoex:hasCurator ?curator_role .
  ?person ontoex:hasRole ?curator_role .
  OPTIONAL { ?person rdfs:label ?person_label }
  OPTIONAL { ?exhibition rdfs:label ?exhibition_label }
}
ORDER BY ?person_label
LIMIT 100`
  },

  // ===== Institutions =====
  {
    id: 'institutions-list',
    name: 'List All Institutions',
    description: 'Retrieves all institutions (museums, galleries, etc.)',
    category: 'institutions',
    query: `${PREFIXES}

SELECT ?institution ?label
WHERE {
  ?institution rdf:type ontoex:Institution .
  OPTIONAL { ?institution rdfs:label ?label }
}
ORDER BY ?label
LIMIT 100`
  },
  {
    id: 'institution-exhibitions',
    name: 'Institutions and Their Exhibitions',
    description: 'Shows institutions as venues with their hosted exhibitions',
    category: 'institutions',
    query: `${PREFIXES}

SELECT ?institution ?institution_label (COUNT(?exhibition) AS ?exhibition_count)
WHERE {
  ?exhibition rdf:type ontoex:Exhibition .
  ?exhibition ontoex:hasVenue ?institution .
  OPTIONAL { ?institution rdfs:label ?institution_label }
}
GROUP BY ?institution ?institution_label
ORDER BY DESC(?exhibition_count)
LIMIT 50`
  },

  // ===== Advanced =====
  {
    id: 'geo-locations',
    name: 'Entities with Coordinates',
    description: 'Lists all entities that have geographic coordinates',
    category: 'advanced',
    query: `${PREFIXES}

SELECT ?entity ?label ?lat ?long
WHERE {
  ?entity geo:lat ?lat .
  ?entity geo:long ?long .
  OPTIONAL { ?entity rdfs:label ?label }
}
LIMIT 100`
  },
  {
    id: 'entity-types',
    name: 'Count Entities by Type',
    description: 'Shows a breakdown of entity counts by RDF type',
    category: 'advanced',
    query: `${PREFIXES}

SELECT ?type (COUNT(?entity) AS ?count)
WHERE {
  ?entity rdf:type ?type .
  FILTER(STRSTARTS(STR(?type), "https://w3id.org/OntoExhibit#"))
}
GROUP BY ?type
ORDER BY DESC(?count)
LIMIT 50`
  },
  {
    id: 'full-exhibition-info',
    name: 'Full Exhibition Details',
    description: 'Complete information about an exhibition including curators, organizers, and venue',
    category: 'advanced',
    query: `${PREFIXES}

SELECT ?exhibition ?label ?place ?opening_date ?closing_date 
       (GROUP_CONCAT(DISTINCT ?curator_name; separator=", ") AS ?curators)
       (GROUP_CONCAT(DISTINCT ?organizer_name; separator=", ") AS ?organizers)
WHERE {
  ?exhibition rdf:type ontoex:Exhibition .
  
  OPTIONAL { ?exhibition rdfs:label ?label }
  OPTIONAL { 
    ?exhibition ontoex:takesPlaceAt ?place_uri .
    ?place_uri rdfs:label ?place 
  }
  OPTIONAL { 
    ?exhibition ontoex:hasOpening ?opening .
    ?opening ontoex:hasTimeSpan ?opening_ts .
    ?opening_ts rdfs:label ?opening_date 
  }
  OPTIONAL { 
    ?exhibition ontoex:hasClosing ?closing .
    ?closing ontoex:hasTimeSpan ?closing_ts .
    ?closing_ts rdfs:label ?closing_date 
  }
  OPTIONAL {
    ?exhibition ontoex:hasExhibitionMaking ?making .
    OPTIONAL {
      ?making ontoex:hasCurator ?curator_role .
      ?curator ontoex:hasRole ?curator_role .
      ?curator rdfs:label ?curator_name .
    }
    OPTIONAL {
      ?making ontoex:hasOrganizer ?org_role .
      ?organizer ontoex:hasRole ?org_role .
      ?organizer rdfs:label ?organizer_name .
    }
  }
}
GROUP BY ?exhibition ?label ?place ?opening_date ?closing_date
LIMIT 50`
  }
];


export const EXAMPLE_QUERIES = exampleQueries;

export function getCategoryLabel(category: ExampleQuery['category']): string {
  switch (category) {
    case 'exhibitions': return 'Exhibitions';
    case 'artworks': return 'Artworks';
    case 'persons': return 'People';
    case 'institutions': return 'Institutions';
    case 'advanced': return 'Advanced';
    default: return category;
  }
}

export function getCategoryColor(category: ExampleQuery['category']): string {
  switch (category) {
    case 'exhibitions': return 'bg-green-100 text-green-800';
    case 'artworks': return 'bg-amber-100 text-amber-800';
    case 'persons': return 'bg-purple-100 text-purple-800';
    case 'institutions': return 'bg-blue-100 text-blue-800';
    case 'advanced': return 'bg-gray-100 text-gray-800';
    default: return 'bg-gray-100 text-gray-800';
  }
}

export default exampleQueries;
