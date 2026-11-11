"""
RDF Graph Builder and Utilities

Manages the RDF graph instance and provides helper functions for
creating triples following the OntoExhibit ontology.
"""
import os
from rdflib import Graph, Namespace, URIRef, Literal, RDF, XSD, RDFS

# Get ontology URI from environment or use default
URI_ONTOLOGIA = os.getenv('URI_ONTOLOGIA', 'https://w3id.org/OntoExhibit#')
URI_GEONAMES = "https://www.geonames.org"

# Shared RDF graph instance
rdf_graph = Graph()

# OntoExhibit namespace
ontoexhibit = Namespace(URI_ONTOLOGIA)

# Bind namespace prefix
rdf_graph.bind('ontoExhibit', ontoexhibit)


# Class mappings from Spanish to ontology classes
CLASSES = [
    # Institutions
    ('Institución', 'Institution'),
    ('Academia', 'F11_Corporate_Body'),
    ('Ayuntamiento', 'Institution'),
    ('Organización sin ánimo de lucro', 'F11_Corporate_Body'),
    ('Universidad', 'University'),
    ('Museo', 'Museum'),
    ('Empresa', 'Company'),
    ('Editorial', 'F11_Corporate_Body'),
    ('Otros tipos de organismos', 'F11_Corporate_Body'),
    ('Otras instituciones públicas', 'Government_Organization'),
    ('Galería de arte', 'Gallery'),
    ('Fundación', 'Foundation_(Institution)'),
    ('Centro de arte', 'Art_Center'),
    ('Escuela de arte', 'Art_School'),
    ('Sala de exposiciones', 'F11_Corporate_Body'),
    ('Entidad gubernamental de ámbito regional', 'Government_Organization'),
    ('Institución gubernamental de ámbito regional', 'Government_Organization'),
    ('institución gubernamental de ámbito regional', 'Government_Organization'),
    ('Centro cultural', 'Cultural_Center'),
    ('Asociación', 'Professional_Association'),
    ('Medio de comunicación digital', 'F11_Corporate_Body'),
    ('Colegio oficial', 'Educational_Institution'),
    ('Centro cívico', 'F11_Corporate_Body'),
    ('Casa de la cultura', 'Cultural_Center'),
    ('Organismo Religioso', 'F11_Corporate_Body'),
    ('Hermandad', 'F11_Corporate_Body'),
    ('Librería', 'Library'),
    ('Club', 'F11_Corporate_Body'),
    ('Periódico', 'F11_Corporate_Body'),
    ('Biblioteca', 'Library'),
    ('Instituto', 'Educational_Institution'),
    ('Administración', 'Government_Organization'),
    ('Real Academia', 'Government_Organization'),
    ('Ministerio', 'Government_Organization'),
    ('Alianza', 'F11_Corporate_Body'),
    ('Colegio', 'Educational_Institution'),
    ('Agencia', 'F11_Corporate_Body'),
    ('Prensa', 'F11_Corporate_Body'),
    ('Abogados', 'F11_Corporate_Body'),
    ('Federación', 'F11_Corporate_Body'),
    ('Cadena radiofónica', 'F11_Corporate_Body'),
    ('Consorcio', 'F11_Corporate_Body'),
    ('Casa museo', 'Museographic_Collection'),
    ('Centro de Estudios', 'Educational_Institution'),
    ('Centro de interpretación', 'Interpretation_Center'),
    ('Colección museográfica', 'Museographic_Collection'),
    ('Conjunto Arqueológico', 'F11_Corporate_Body'),
    ('Diputación provincial', 'Government_Organization'),
    ('Real Academia de Bellas Artes', 'Academy_Of_Fine_Arts'),
    ('Archivo', 'Archive'),
    ('Escuela de fotografía', 'Educational_Institution'),
    ('Página web privada o blog privado', 'F11_Corporate_Body'),
    ('Colectivos de artistas', 'Artists_Group'),
    ('Sociedad Económica de Amigos del País', 'Professional_Association'),
    ('Espacio artístico multidisciplinar', 'Cultural_Institution'),
    ('Espacio cultural', 'Cultural_Institution'),
    ('Medio de comunicación', 'Institution'),
    ('Otros tipos de organismos públicos', 'Institution'),
    ('Casa de subastas', 'Auction_House'),
    ('Colección privada', 'F11_Corporate_Body'),
    ('Embajada', 'Government_Organization'),
    ('Palacio', 'F11_Corporate_Body'),
    ('Banco', 'F11_Corporate_Body'),
    ('Restaurante', 'F11_Corporate_Body'),
    ('Festival', 'F11_Corporate_Body'),
    ('Consejo', 'F11_Corporate_Body'),
    ('Agrupación', 'F11_Corporate_Body'),
    ('Museo-Fundación', 'Museum'),
    ('Hospital', 'F11_Corporate_Body'),
    ('Tienda de antigüedades', 'F11_Corporate_Body'),
    ('Instituto de arte', 'Educational_Institution'),
    ('Espacio expositivo', 'F11_Corporate_Body'),
    ('Catálogo de colecciones', 'F11_Corporate_Body'),
    ('Tienda', 'F11_Corporate_Body'),
    ('Teatro', 'Cultural_Institution'),
    ('Subasta', 'Auction_House'),
    ('Cofradía', 'F11_Corporate_Body'),
    ('GaleríaInforme', 'F11_Corporate_Body'),
    
    # Exhibitions
    ('Exposición', 'Exhibition'),
    ('Exposición colectiva', 'Exhibition'),
    ('Exposición monográfica', 'Exhibition'),
    ('Exposición itinerante', 'Exhibition'),
    ('Exposición retrospectiva', 'Exhibition'),
    ('Exposición antológica', 'Exhibition'),
    ('Exposición conmemorativa', 'Exhibition'),
    ('Exposición de certamen artístico', 'Exhibition'),
    ('Exposición de ferias de muestras', 'Exhibition'),
    ('Feria de arte', 'Exhibition'),
    ('Exposición menor', 'Exhibition'),
    ('Obra individual', 'Exhibition'),
    ('Exposición multisede', 'Exhibition'),
    ('Recreación histórica', 'Exhibition'),
    ('Exposición histórica', 'Exhibition'),
    ('Exposición etnográfica', 'Exhibition'),
    ('Exposición taller', 'Exhibition'),
    ('Exposición urbana', 'Exhibition'),
    ('Exposición arqueológica', 'Exhibition'),
    ('Exposición inmersiva', 'Exhibition'),
    ('Exposición virtual', 'Exhibition'),
    ('Exposición retrospectiva concentrada', 'Exhibition'),
    ('Exposición sonora', 'Exhibition'),
    ('Exposición temática', 'Exhibition'),
    ('Exposición de homenaje', 'Exhibition'),
    ('Exposición interactiva', 'Exhibition'),
    ('Exposición individual', 'Exhibition'),
    ('Exposición documental', 'Exhibition'),
    ('Obra invitada', 'Exhibition'),
    ('Exposición inaugural', 'Exhibition'),
    ('Exposición online', 'Exhibition'),
    ('Edición', 'Exhibition'),
    
    # Artworks
    ('Obra de arte', 'WorkManifestation'),
    ('Esculturas', 'WorkManifestation'),
    ('Artes visuales', 'VisualWork'),
    ('Pinturas', 'VisualWork'),
    ('Obras en papel', 'WorkManifestation'),
    ('Dibujos', 'WorkManifestation'),
    ('Grabados', 'WorkManifestation'),
    ('Bordado', 'WorkManifestation'),
    ('Acuarelas', 'WorkManifestation'),
    ('Tabla', 'WorkManifestation'),
    ('Bocetos', 'WorkManifestation'),
    ('Mobiliario', 'WorkManifestation'),
    ('Obras textiles', 'WorkManifestation'),
    ('Artes decorativas/funcionales', 'WorkManifestation'),
    ('Joyas', 'WorkManifestation'),
    ('Espada', 'WorkManifestation'),
    ('Fotografías', 'WorkManifestation'),
    
    # Catalogs
    ('Dispositivo de inscripción', 'Catalogue'),
    ('Catálogo de exposiciones', 'Catalogue'),
    ('Catálogo', 'Catalogue'),
    ('Propietario', 'Owner'),
]


def get_ontology_class(spanish_name: str) -> str | None:
    """Get the ontology class for a Spanish type name."""
    for spanish, ontology in CLASSES:
        if spanish == spanish_name:
            return ontology
    return None


def add_triple(subject, predicate, obj):
    """Add a triple to the shared RDF graph."""
    rdf_graph.add((subject, predicate, obj))


def add_type(subject, type_name: str):
    """Add RDF type triple using ontology namespace."""
    add_triple(subject, RDF.type, URIRef(f"{ontoexhibit}{type_name}"))


def add_cidoc_type(subject, type_name: str):
    """Add CIDOC-CRM type triple."""
    add_triple(subject, RDF.type, URIRef(f"https://cidoc-crm.org/cidoc-crm/7.1.1/{type_name}"))


def add_label(subject, label: str):
    """Add RDFS label."""
    add_triple(subject, RDFS.label, Literal(label, datatype=XSD['string']))


def add_literal(subject, predicate_name: str, value: str, datatype=None):
    """Add a literal property using ontology namespace."""
    if datatype is None:
        datatype = XSD['string']
    add_triple(subject, URIRef(f"{ontoexhibit}{predicate_name}"), Literal(value, datatype=datatype))


def add_relation(subject, predicate_name: str, obj):
    """Add an object property relation using ontology namespace."""
    add_triple(subject, URIRef(f"{ontoexhibit}{predicate_name}"), obj)


def add_bidirectional(subject, pred1: str, pred2: str, obj):
    """Add bidirectional relationship (both directions)."""
    add_relation(subject, pred1, obj)
    add_relation(obj, pred2, subject)


def serialize_graph(output_path: str = 'result.nt', format: str = 'nt') -> str:
    """Serialize the RDF graph to file and return the path."""
    with open(output_path, 'w+', encoding='utf-8') as f:
        f.write(rdf_graph.serialize(format=format))
    print(f'Results saved in file "{output_path}"')
    return output_path


def get_graph_stats() -> dict:
    """Get statistics about the current graph."""
    return {
        'num_triples': len(rdf_graph),
        'num_subjects': len(set(rdf_graph.subjects())),
    }
