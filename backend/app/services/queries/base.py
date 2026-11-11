from app.core.config import settings

PREFIXES = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

URI_ONTOLOGIA = settings.URI_ONTOLOGIA
uri_ontologia = URI_ONTOLOGIA

OBJECT_PROPERTIES = [
    "isRoleOf",
    "takesPlaceAt",
    "hasParentOrganization",
    "hasOrganizer",
    "hasSponsor",
    "hasOpening",
    "hasClosing",
    "isCuratorInvolvedIn",
    "hasTitle",
    "hasMember",
    "isMemberOf",
    "isDirectorOf",
    "isFounderOf",
    "hasFounder",
    "isFunderOf",
    "hasFunder",
    "isParticipantOf",
    "hasParticipant",
    "productionPlace",
    "productionEndDate",
    "productionStartDate",
    "hasAuthor",
    "exposicionExhibeArtista",
    "exposicionExhibeInstitucion",
    "hasVenue",
]
