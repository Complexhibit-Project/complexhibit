"""
OntoExhibit ontology constants.

Centralizes all ontology URIs and class names to avoid hardcoding 
throughout the codebase. Based on actual usage in query files.
"""

from app.core.config import settings

# Base URI
BASE_URI = "https://w3id.org/OntoExhibit#"

# Helper to create full URI
def uri(name: str) -> str:
    """Create full ontology URI from local name."""
    return f"<{BASE_URI}{name}>"


class Classes:
    """OntoExhibit class URIs."""
    
    # Exhibitions
    EXHIBITION = uri("Exhibition")
    PERMANENT_EXHIBITION = uri("Permanent_Exhibition")
    TEMPORARY_EXHIBITION = uri("Temporary_Exhibition")
    TRAVELLING_EXHIBITION = uri("Travelling_Exhibition")
    EXHIBITION_MAKING = uri("Exhibition_Making")
    
    # Actors
    HUMAN_ACTANT = uri("Human_Actant")
    ACTOR = uri("Actor")
    GROUP = uri("Group")
    
    # Artworks
    WORK_MANIFESTATION = uri("Work_Manifestation")
    ARTWORK = uri("Artwork")
    
    # Institutions
    INSTITUTION = uri("Institution")
    CULTURAL_INSTITUTION = uri("Cultural_Institution")
    ART_CENTER = uri("Art_Center")
    CULTURAL_CENTER = uri("Cultural_Center")
    EXHIBITION_SPACE = uri("ExhibitionSpace")
    INTERPRETATION_CENTER = uri("Interpretation_Center")
    LIBRARY = uri("Library")
    MUSEUM = uri("Museum")
    EDUCATIONAL_INSTITUTION = uri("Educational_Institution")
    UNIVERSITY = uri("University")
    FOUNDATION = uri("Foundation_(Institution)")
    
    # All institution types for UNION queries
    ALL_INSTITUTION_TYPES = [
        INSTITUTION,
        CULTURAL_INSTITUTION,
        ART_CENTER,
        CULTURAL_CENTER,
        EXHIBITION_SPACE,
        INTERPRETATION_CENTER,
        LIBRARY,
        MUSEUM,
        EDUCATIONAL_INSTITUTION,
        UNIVERSITY,
        FOUNDATION,
    ]
    
    # Places
    SITE = uri("Site")
    GEOGRAPHIC_PLACE = uri("Geographic_Place")
    
    # Time
    TIME_SPAN = uri("TimeSpan")


class Properties:
    """OntoExhibit property URIs."""
    
    # ================
    # Core Actor Properties
    # ================
    HAS_BIRTH = uri("hasBirth")
    HAS_DEATH = uri("hasDeath")
    DIED = uri("died")
    HAS_PLACE_OF_BIRTH = uri("hasPlaceOfBirth")
    HAS_TIME_SPAN = uri("hasTimeSpan")
    GENDER = uri("gender")
    ACTIVITY_TYPE = uri("activity_type")
    PERSON_NAME = uri("person_name")
    
    # ================
    # Role Properties
    # ================
    HAS_ROLE = uri("hasRole")
    IS_ROLE_OF = uri("isRoleOf")
    
    # ================
    # Exhibition Making Properties
    # ================
    MADE_EXHIBITION = uri("madeExhibition")
    HAS_EXHIBITING_ACTANT = uri("hasExhibitingActant")
    IS_EXHIBITING_ACTANT_IN = uri("isExhibitingActantIn")
    HAS_CURATOR = uri("hasCurator")
    IS_CURATOR_OF = uri("isCuratorOf")
    HAS_ORGANIZER = uri("hasOrganizer")
    IS_ORGANIZER_OF = uri("isOrganizerOf")
    HAS_FUNDER = uri("hasFunder")
    IS_FUNDER_OF = uri("isFunderOf")
    HAS_LENDER = uri("hasLender")
    IS_LENDER_OF = uri("isLenderOf")
    HAS_SPONSOR = uri("hasSponsor")
    
    # ================
    # Exhibition Properties
    # ================
    TAKES_PLACE_AT = uri("takesPlaceAt")
    HAS_VENUE = uri("hasVenue")
    HAS_OPENING = uri("hasOpening")
    HAS_CLOSING = uri("hasClosing")
    BEGIN_OF_BEGIN = uri("BeginOfBegin")
    END_OF_END = uri("EndOfEnd")
    HAS_THEME = uri("hasTheme")
    HAS_EXHIBITION_TYPE = uri("hasExhibitionType")
    SHOWS = uri("shows")
    
    # ================
    # Artwork Properties
    # ================
    HAS_PRODUCTION = uri("hasProduction")
    HAS_PRODUCTION_AUTHOR = uri("hasProductionAuthor")
    IS_PRODUCTION_AUTHOR_OF = uri("isProductionAuthorOf")
    HAS_OWNER = uri("hasOwner")
    IS_OWNER_OF = uri("isOwnerOf")
    HAS_TOPIC = uri("hasTopic")
    PRODUCTION_START_DATE = uri("productionStartDate")
    PRODUCTION_END_DATE = uri("productionEndDate")
    PRODUCTION_PLACE = uri("productionPlace")
    IS_SHOWN_AT = uri("isShownAt")
    
    # ================
    # Institution/Location Properties
    # ================
    HAS_LOCATION = uri("hasLocation")
    IS_LOCATED_AT = uri("isLocatedAt")
    APELATION = uri("apelation")
    
    # ================
    # Geographic Properties
    # ================
    HAS_LAT = uri("hasLat")
    HAS_LONG = uri("hasLong")


def build_institution_union_pattern(label_var: str = "label") -> str:
    """
    Build UNION pattern for all institution types.
    
    Returns:
        SPARQL WHERE clause matching all institution types
    """
    patterns = []
    for cls in Classes.ALL_INSTITUTION_TYPES:
        patterns.append(f"{{ ?uri rdf:type {cls} . ?uri rdfs:label ?{label_var} }}")
    
    return "\n                UNION ".join(patterns)
