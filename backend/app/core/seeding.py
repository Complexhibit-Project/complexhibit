import os
import re
import secrets

from sqlalchemy.orm import Session
from app.models.user import User, UserRole, UserStatus
from app.models.example_query import ExampleQuery
from app.core.security import hash_password
from app.core.config import settings
from app.core.database import SessionLocal

# Common prefixes for queries
PREFIXES = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ontoex: <https://w3id.org/OntoExhibit#>
PREFIX crm: <https://cidoc-crm.org/cidoc-crm/7.1.1/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>"""

GRAPH_URI = "https://w3id.org/OntoExhibit/Data"

DEFAULT_QUERIES = [
    {
        "name": "Total Triples Count",
        "description": "Returns the total number of triples currently stored in the knowledge graph",
        "category": "advanced",
        "query": f"""{PREFIXES}

SELECT (COUNT(*) AS ?totalTriples)
FROM <{GRAPH_URI}>
WHERE {{
  ?s ?p ?o .
}}"""
    },
    # --- New User Requests ---
    {
        "name": "Women < 40 in Andalusian Exhibitions (Sorted)",
        "description": "Women under 40 who participated in exhibitions in Andalucia, sorted by age and name.",
        "category": "persons",
        "query": f"""{PREFIXES}

SELECT DISTINCT ?person_label ?birth_date ?age_at_exhibition ?exhibition_year ?exhibition_label ?place_label
FROM <{GRAPH_URI}>
WHERE {{
  # 1. Person: Female
  ?person rdf:type crm:E21_Person ;
          rdfs:label ?person_label ;
          ontoex:gender ?gender .
  FILTER(regex(str(?gender), "^Femenino$", "i"))

  # 2. Birth Date
  ?person ontoex:hasBirth/ontoex:hasTimeSpan/rdfs:label ?birth_date .
  BIND(xsd:integer(SUBSTR(str(?birth_date), 1, 4)) AS ?birth_year)

  # 3. Role: Exhibitor
  ?person ontoex:hasRole ?role .
  ?role ontoex:isExhibitingActantIn ?making .
  ?making ontoex:isExhibitionMakingOf ?exhibition .
  
  ?exhibition rdfs:label ?exhibition_label .

  # 4. Exhibition Date (Example range >= 1990)
  ?exhibition ontoex:hasOpening/ontoex:hasTimeSpan/rdfs:label ?exhibition_date .
  BIND(xsd:integer(SUBSTR(str(?exhibition_date), 1, 4)) AS ?exhibition_year)
  FILTER(?exhibition_year >= 1990) 

  # 5. Place: Andalucia
  ?exhibition ontoex:takesPlaceAt ?place .
  ?place rdfs:label ?place_label .
  FILTER(regex(?place_label, "Sevilla|Málaga|Granada|Córdoba|Cádiz|Huelva|Jaén|Almería|Andaluc", "i"))

  # 6. Age Calculation (< 40)
  BIND((?exhibition_year - ?birth_year) AS ?age_at_exhibition)
  FILTER(?age_at_exhibition < 40 && ?age_at_exhibition > 0)
}}
ORDER BY ?age_at_exhibition ?person_label"""
    },
    {
        "name": "Intl. Andalusian Women Artists",
        "description": "Andalusian-born women who have participated in more than one exhibition outside Spain.",
        "category": "advanced",
        "query": f"""{PREFIXES}

SELECT ?person_label ?birth_place_label (COUNT(?exhibition) AS ?foreign_exhibition_count)
FROM <{GRAPH_URI}>
WHERE {{
  # 1. Andalusian Women
  ?person rdf:type crm:E21_Person ;
          rdfs:label ?person_label ;
          ontoex:gender ?gender .
  FILTER(regex(str(?gender), "^Femenino$", "i"))
  
  # Born in Andalucia
  ?person ontoex:hasBirth/ontoex:hasPlaceOfBirth ?birth_place .
  ?birth_place rdfs:label ?birth_place_label .
  FILTER(regex(?birth_place_label, "Andaluc", "i"))

  # 2. Exhibitions outside Spain
  {{
      # Role paths (Exhibitor or Author)
      {{ ?person ontoex:hasRole/ontoex:isExhibitingActantIn/ontoex:isExhibitionMakingOf ?exhibition }}
      UNION
      {{ ?person ontoex:hasRole/ontoex:isAuthorOf/^ontoex:displays ?exhibition }}
  }}
  
  ?exhibition ontoex:takesPlaceAt ?exh_place .
  ?exh_place rdfs:label ?exh_place_label .
  # Filter OUT Spain
  FILTER(!regex(?exh_place_label, "Espa.a|Spain", "i"))
  
}}
GROUP BY ?person_label ?birth_place_label
HAVING (COUNT(?exhibition) > 1)
ORDER BY DESC(?foreign_exhibition_count)"""
    },

    # --- Existing Default Queries ---
    {
        "name": "List All Exhibitions",
        "description": "Retrieves all exhibitions with their labels (limited to 100)",
        "category": "exhibitions",
        "query": f"""{PREFIXES}

SELECT ?exhibition ?label
FROM <{GRAPH_URI}>
WHERE {{
  ?exhibition rdf:type ontoex:Exhibition .
  OPTIONAL {{ ?exhibition rdfs:label ?label }}
}}
ORDER BY ?label
LIMIT 100"""
    },
    {
        "name": "Exhibitions with Dates",
        "description": "Lists exhibitions with their opening and closing dates",
        "category": "exhibitions",
        "query": f"""{PREFIXES}

SELECT ?exhibition ?label ?opening_date ?closing_date
FROM <{GRAPH_URI}>
WHERE {{
  ?exhibition rdf:type ontoex:Exhibition .
  OPTIONAL {{ 
    ?exhibition rdfs:label ?direct_label 
  }}
  OPTIONAL {{ 
    ?exhibition ontoex:hasTitle ?title .
    ?title rdfs:label ?title_label 
  }}
  BIND(COALESCE(?title_label, ?direct_label, "Unknown") AS ?label)
  
  OPTIONAL {{ 
    ?exhibition ontoex:hasOpening ?opening .
    ?opening ontoex:hasTimeSpan ?opening_ts .
    ?opening_ts rdfs:label ?opening_date 
  }}
  OPTIONAL {{ 
    ?exhibition ontoex:hasClosing ?closing .
    ?closing ontoex:hasTimeSpan ?closing_ts .
    ?closing_ts rdfs:label ?closing_date 
  }}
}}
ORDER BY ?opening_date
LIMIT 100"""
    },
    {
        "name": "Exhibitions by Location",
        "description": "Lists exhibitions grouped by their location",
        "category": "exhibitions",
        "query": f"""{PREFIXES}

SELECT ?place_label (COUNT(?exhibition) AS ?count)
FROM <{GRAPH_URI}>
WHERE {{
  ?exhibition rdf:type ontoex:Exhibition .
  ?exhibition ontoex:takesPlaceAt ?place .
  ?place rdfs:label ?place_label .
}}
GROUP BY ?place_label
ORDER BY DESC(?count)
LIMIT 50"""
    },
    {
        "name": "List All Artworks",
        "description": "Retrieves all artworks with their labels",
        "category": "artworks",
        "query": f"""{PREFIXES}

SELECT ?artwork ?label
FROM <{GRAPH_URI}>
WHERE {{
  ?artwork rdf:type ontoex:Artwork .
  OPTIONAL {{ ?artwork rdfs:label ?label }}
}}
ORDER BY ?label
LIMIT 100"""
    },
    {
        "name": "Artworks and Their Exhibitions",
        "description": "Shows artworks and the exhibitions where they were displayed",
        "category": "artworks",
        "query": f"""{PREFIXES}

SELECT ?artwork ?artwork_label ?exhibition ?exhibition_label
FROM <{GRAPH_URI}>
WHERE {{
  ?exhibition rdf:type ontoex:Exhibition .
  ?exhibition ontoex:displays ?artwork .
  OPTIONAL {{ ?artwork rdfs:label ?artwork_label }}
  OPTIONAL {{ ?exhibition rdfs:label ?exhibition_label }}
}}
ORDER BY ?artwork_label
LIMIT 100"""
    },
    {
        "name": "List All Persons",
        "description": "Retrieves all persons registered in the knowledge graph",
        "category": "persons",
        "query": f"""{PREFIXES}

SELECT ?person ?label
FROM <{GRAPH_URI}>
WHERE {{
  ?person rdf:type ontoex:HumanActant .
  OPTIONAL {{ ?person rdfs:label ?label }}
}}
ORDER BY ?label
LIMIT 100"""
    },
    {
        "name": "Exhibition Curators",
        "description": "Lists curators and the exhibitions they curated",
        "category": "persons",
        "query": f"""{PREFIXES}

SELECT ?person ?person_label ?exhibition ?exhibition_label
FROM <{GRAPH_URI}>
WHERE {{
  ?exhibition rdf:type ontoex:Exhibition .
  ?exhibition ontoex:hasExhibitionMaking ?making .
  ?making ontoex:hasCurator ?curator_role .
  ?person ontoex:hasRole ?curator_role .
  OPTIONAL {{ ?person rdfs:label ?person_label }}
  OPTIONAL {{ ?exhibition rdfs:label ?exhibition_label }}
}}
ORDER BY ?person_label
LIMIT 100"""
    },
    {
        "name": "List All Institutions",
        "description": "Retrieves all institutions (museums, galleries, etc.)",
        "category": "institutions",
        "query": f"""{PREFIXES}

SELECT ?institution ?label
FROM <{GRAPH_URI}>
WHERE {{
  ?institution rdf:type ontoex:Institution .
  OPTIONAL {{ ?institution rdfs:label ?label }}
}}
ORDER BY ?label
LIMIT 100"""
    },
    {
        "name": "Institutions and Their Exhibitions",
        "description": "Shows institutions as venues with their hosted exhibitions",
        "category": "institutions",
        "query": f"""{PREFIXES}

SELECT ?institution ?institution_label (COUNT(?exhibition) AS ?exhibition_count)
FROM <{GRAPH_URI}>
WHERE {{
  ?exhibition rdf:type ontoex:Exhibition .
  ?exhibition ontoex:hasVenue ?institution .
  OPTIONAL {{ ?institution rdfs:label ?institution_label }}
}}
GROUP BY ?institution ?institution_label
ORDER BY DESC(?exhibition_count)
LIMIT 50"""
    },
    {
        "name": "Entities with Coordinates",
        "description": "Lists all entities that have geographic coordinates",
        "category": "advanced",
        "query": f"""{PREFIXES}

SELECT ?entity ?label ?lat ?long
FROM <{GRAPH_URI}>
WHERE {{
  ?entity geo:lat ?lat .
  ?entity geo:long ?long .
  OPTIONAL {{ ?entity rdfs:label ?label }}
}}
LIMIT 100"""
    },
    {
        "name": "Count Entities by Type",
        "description": "Shows a breakdown of entity counts by RDF type",
        "category": "advanced",
        "query": f"""{PREFIXES}

SELECT ?type (COUNT(?entity) AS ?count)
FROM <{GRAPH_URI}>
WHERE {{
  ?entity rdf:type ?type .
  FILTER(STRSTARTS(STR(?type), "https://w3id.org/OntoExhibit#"))
}}
GROUP BY ?type
ORDER BY DESC(?count)
LIMIT 50"""
    },
    {
        "name": "Full Exhibition Details",
        "description": "Complete information about an exhibition including curators, organizers, and venue",
        "category": "advanced",
        "query": f"""{PREFIXES}

SELECT ?exhibition ?label ?place ?opening_date ?closing_date 
       (GROUP_CONCAT(DISTINCT ?curator_name; separator=", ") AS ?curators)
       (GROUP_CONCAT(DISTINCT ?organizer_name; separator=", ") AS ?organizers)
FROM <{GRAPH_URI}>
WHERE {{
  ?exhibition rdf:type ontoex:Exhibition .
  
  OPTIONAL {{ ?exhibition rdfs:label ?label }}
  OPTIONAL {{ 
    ?exhibition ontoex:takesPlaceAt ?place_uri .
    ?place_uri rdfs:label ?place 
  }}
  OPTIONAL {{ 
    ?exhibition ontoex:hasOpening ?opening .
    ?opening ontoex:hasTimeSpan ?opening_ts .
    ?opening_ts rdfs:label ?opening_date 
  }}
  OPTIONAL {{ 
    ?exhibition ontoex:hasClosing ?closing .
    ?closing ontoex:hasTimeSpan ?closing_ts .
    ?closing_ts rdfs:label ?closing_date 
  }}
  OPTIONAL {{
    ?exhibition ontoex:hasExhibitionMaking ?making .
    OPTIONAL {{
      ?making ontoex:hasCurator ?curator_role .
      ?curator ontoex:hasRole ?curator_role .
      ?curator rdfs:label ?curator_name .
    }}
    OPTIONAL {{
      ?making ontoex:hasOrganizer ?org_role .
      ?organizer ontoex:hasRole ?org_role .
      ?organizer rdfs:label ?organizer_name .
    }}
  }}
}}
GROUP BY ?exhibition ?label ?place ?opening_date ?closing_date
LIMIT 50"""
    }
]

def seed_example_queries():
    """Seed the database with default example queries."""
    try:
        db = SessionLocal()
        try:
            # 1. Get or Create System Admin User to own these queries
            user = db.query(User).filter(User.username == "system_admin").first()
            if not user:
                # Create a dedicated system admin user if doesn't exist
                # This internal user only owns the seeded example queries; it is never
                # used to log in. Use an explicit env override if provided, otherwise a
                # cryptographically-random password so no default credential exists.
                system_admin_password = os.getenv("SYSTEM_ADMIN_PASSWORD") or secrets.token_urlsafe(32)
                user = User(
                    username="system_admin",
                    email="admin@complexhibit.com",
                    full_name="System Administrator",
                    hashed_password=hash_password(system_admin_password),
                    role=UserRole.ADMIN,
                    status=UserStatus.ACTIVE
                )
                db.add(user)
                db.flush() # flush to get ID
                print(f"Created System Admin user (ID: {user.id})")
            else:
                print(f"Using existing System Admin user (ID: {user.id})")

            # 2. Upsert Queries
            count = 0
            for q_data in DEFAULT_QUERIES:
                existing = db.query(ExampleQuery).filter(
                    ExampleQuery.name == q_data["name"],
                    ExampleQuery.user_id == user.id
                ).first()
                
                if not existing:
                    new_query = ExampleQuery(
                        name=q_data["name"],
                        description=q_data["description"],
                        category=q_data["category"],
                        query=q_data["query"],
                        user_id=user.id,
                        is_approved=True
                    )
                    db.add(new_query)
                    count += 1
                else:
                    # Optional: Update existing if query changed?
                    # For now, let's update content to ensure fixes propagate
                    existing.query = q_data["query"]
                    existing.description = q_data["description"]
                    existing.category = q_data["category"]
                    
            db.commit()
            print(f"Seeded {count} new example queries (and updated existing ones).")
            
        except Exception as e:
            print(f"Error seeding example queries: {e}")
            db.rollback()
        finally:
            db.close()
    except Exception as outer_e:
         print(f"CRITICAL ERROR in seed_example_queries: {outer_e}")


def parse_admin_users(raw: str):
    """
    Parse the ADMIN_USERS env string into a list of (email, password) tuples.

    Format: "email:pass,email:pass". Each entry is split on the FIRST ':' only,
    so passwords may contain ':'. Entries are separated by ','.
    """
    admins = []
    if not raw:
        return admins
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry or ":" not in entry:
            continue
        email, password = entry.split(":", 1)
        email = email.strip()
        if email and password:
            admins.append((email, password))
    return admins


def _unique_username(db, base: str) -> str:
    """Sanitize base to ^[a-zA-Z0-9_]+$ and ensure uniqueness in the DB."""
    candidate = re.sub(r"[^a-zA-Z0-9_]", "", base) or "admin"
    username = candidate
    suffix = 1
    while db.query(User).filter(User.username == username).first():
        suffix += 1
        username = f"{candidate}{suffix}"
    return username


def seed_admins():
    """
    Create admin users listed in ADMIN_USERS if they don't already exist.

    Idempotent: an existing user (matched by email) is never modified, so an
    admin who changed their password keeps it across restarts.
    """
    admins = parse_admin_users(settings.ADMIN_USERS)
    if not admins:
        return
    try:
        db = SessionLocal()
        try:
            created = 0
            for email, password in admins:
                if db.query(User).filter(User.email == email).first():
                    continue
                username = _unique_username(db, email.split("@", 1)[0])
                user = User(
                    email=email,
                    username=username,
                    hashed_password=hash_password(password),
                    full_name="Administrator",
                    role=UserRole.ADMIN,
                    status=UserStatus.ACTIVE,
                )
                db.add(user)
                created += 1
                print(f"Created admin user: {email} (username: {username})")
            db.commit()
            print(f"Seeded {created} new admin user(s).")
        except Exception as e:
            print(f"Error seeding admins: {e}")
            db.rollback()
        finally:
            db.close()
    except Exception as outer_e:
        print(f"CRITICAL ERROR in seed_admins: {outer_e}")
