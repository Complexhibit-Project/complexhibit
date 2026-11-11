import sqlite3
import datetime as datetime
from sqlite3 import Cursor
from googletrans import Translator

from rdflib import Graph, Namespace, URIRef, Literal, RDF, XSD, RDFS
from urllib.parse import urlparse
import pandas as pd

from commons import URI_ONTOLOGIA, hash_sha256, normalize_name

connection = sqlite3.connect('pathwise.db')
cursor = connection.cursor()
URI_GEONAMES = "https://www.geonames.org"

translator = Translator()

BANNED_LIST = [
    "CASI",
    "COMPLETADA",
    "GaleríaInforme",
    "Cofradía",
    "Contemporánea",
    "REL",
    "NR",

    # "Exposición de homenaje",
    # "Exposición documental",
    # "Exposición interactiva",
    # "Exposición monográfica",
    # "Exposición online",
    # "Exposición temática",
    # "Obra invitada"
]

count_fail = 0
count_success = 0
total_dates = 0

# Generate new graph
rdf_graph = Graph()

# Set up namespaces used
ontoexhibit = Namespace(URI_ONTOLOGIA)

# Bind namespaces to prefix
rdf_graph.bind('ontoExhibit', ontoexhibit)

classes = [
    # ('Individuo', 'Person', 'string'),
    # ('Persona', 'Person', 'string'),
    # ('Grupo de personas', 'ArtistsGroup', 'string'),

    ('Institución', 'Institution', 'string'),
    ('Academia', 'F11_Corporate_Body', 'string'),
    ('Ayuntamiento', 'Institution', 'string'),
    ('Organización sin ánimo de lucro', 'F11_Corporate_Body', 'string'),
    ('Universidad', 'University', 'string'),
    ('Museo', 'Museum', 'string'),
    ('Empresa', 'Company', 'string'),
    ('Editorial', 'F11_Corporate_Body', 'string'),
    ('Otros tipos de organismos', 'F11_Corporate_Body', 'string'),
    ('Otras instituciones públicas', 'Government_Organization', 'string'),
    ('Galería de arte', 'Gallery', 'string'),
    ('Fundación', 'Foundation_(Institution)', 'string'),
    ('Centro de arte', 'Art_Center', 'string'),
    ('Escuela de arte', 'Art_School', 'string'),
    ('Sala de exposiciones', 'F11_Corporate_Body', 'string'),
    ('Entidad gubernamental de ámbito regional', 'Government_Organization', 'string'),
    ('Institución gubernamental de ámbito regional', 'Government_Organization', 'string'),
    ('institución gubernamental de ámbito regional', 'Government_Organization', 'string'),
    ('Centro cultural', 'Cultural_Center', 'string'),
    ('Asociación', 'Professional_Association', 'string'),
    ('Medio de comunicación digital', 'F11_Corporate_Body', 'string'),
    ('Colegio oficial', 'Educational_Institution', 'string'),
    ('Centro cívico', 'F11_Corporate_Body', 'string'),
    ('Casa de la cultura', 'Cultural_Center', 'string'),
    ('Organismo Religioso', 'F11_Corporate_Body', 'string'),
    ('Hermandad', 'F11_Corporate_Body', 'string'),
    ('Librería', 'Library', 'string'),
    ('Club', 'F11_Corporate_Body', 'string'),
    ('Periódico', 'F11_Corporate_Body', 'string'),
    ('Biblioteca', 'Library', 'string'),
    ('Instituto', 'Educational_Institution', 'string'),
    ('Administración', 'Government_Organization', 'string'),
    ('Real Academia', 'Government_Organization', 'string'),
    ('Ministerio', 'Government_Organization', 'string'),
    ('Alianza', 'F11_Corporate_Body', 'string'),
    ('Colegio', 'Educational_Institution', 'string'),
    ('Agencia', 'F11_Corporate_Body', 'string'),
    ('Prensa', 'F11_Corporate_Body', 'string'),
    ('Abogados', 'F11_Corporate_Body', 'string'),
    ('Federación', 'F11_Corporate_Body', 'string'),
    ('Cadena radiofónica', 'F11_Corporate_Body', 'string'),
    ('Consorcio', 'F11_Corporate_Body', 'string'),
    ('Casa museo', 'Museographic_Collection', 'string'),
    ('Centro de Estudios', 'Educational_Institution', 'string'),
    ('Centro de interpretación', 'Interpretation_Center', 'string'),
    ('Colección museográfica', 'Museographic_Collection', 'string'),
    ('Conjunto Arqueológico', 'F11_Corporate_Body', 'string'),
    ('Diputación provincial', 'Government_Organization', 'string'),
    ('Real Academia de Bellas Artes', 'Academy_Of_Fine_Arts', 'string'),
    ('Archivo', 'Archive', 'string'),
    ('Escuela de fotografía', 'Educational_Institution', 'string'),
    ('Página web privada o blog privado', 'F11_Corporate_Body', 'string'),
    ('Colectivos de artistas', 'Artists_Group', 'string'),
    ('Sociedad Económica de Amigos del País', 'Professional_Association', 'string'),
    ('Espacio artístico multidisciplinar', 'Cultural_Institution', 'string'),
    ('Espacio cultural', 'Cultural_Institution', 'string'),
    ('Medio de comunicación', 'Institution', 'string'),
    ('Otros tipos de organismos públicos', 'Institution', 'string'),
    ('Casa de subastas', 'Auction_House', 'string'),
    ('Colección privada', 'F11_Corporate_Body', 'string'),
    ('Embajada', 'Government_Organization', 'string'),
    ('Palacio', 'F11_Corporate_Body', 'string'),
    ('Banco', 'F11_Corporate_Body', 'string'),
    ('Restaurante', 'F11_Corporate_Body', 'string'),
    ('Festival', 'F11_Corporate_Body', 'string'),
    ('Consejo', 'F11_Corporate_Body', 'string'),
    ('Agrupación', 'F11_Corporate_Body', 'string'),
    ('Museo-Fundación', 'Museum', 'string'),
    ('Hospital', 'F11_Corporate_Body', 'string'),
    ('Tienda de antigüedades', 'F11_Corporate_Body', 'string'),
    ('Instituto de arte', 'Educational_Institution', 'string'),
    ('Espacio expositivo', 'F11_Corporate_Body', 'string'),
    ('Catálogo de colecciones', 'F11_Corporate_Body', 'string'),
    ('Tienda', 'F11_Corporate_Body', 'string'),
    ('Teatro', 'Cultural_Institution', 'string'),
    ('Subasta', 'Auction_House', 'string'),
    ('Cofradía', 'F11_Corporate_Body', 'string'),
    ('GaleríaInforme', 'F11_Corporate_Body', 'string'),

    ('Exposición', 'Exhibition', 'string'),
    ('Exposición colectiva', 'Exhibition', 'string'),
    ('Exposición monográfica', 'Exhibition', 'string'),
    ('Exposición itinerante', 'Exhibition', 'string'),
    ('Exposición retrospectiva', 'Exhibition', 'string'),
    ('Exposición antológica', 'Exhibition', 'string'),
    ('Exposición conmemorativa', 'Exhibition', 'string'),
    ('Exposición de certamen artístico', 'Exhibition', 'string'),
    ('Exposición de ferias de muestras', 'Exhibition', 'string'),
    ('Feria de arte', 'Exhibition', 'string'),
    ('Exposición menor', 'Exhibition', 'string'),
    ('Obra individual', 'Exhibition', 'string'),
    ('Exposición multisede', 'Exhibition', 'string'),
    ('Recreación histórica', 'Exhibition', 'string'),
    ('Exposición histórica', 'Exhibition', 'string'),
    ('Exposición etnográfica', 'Exhibition', 'string'),
    # ('Exposición taller', 'Workshop', 'string'),
    ('Exposición taller', 'Exhibition', 'string'),
    ('Exposición urbana', 'Exhibition', 'string'),
    ('Exposición arqueológica', 'Exhibition', 'string'),
    ('Exposición inmersiva', 'Exhibition', 'string'),
    ('Exposición virtual', 'Exhibition', 'string'),
    ('Exposición retrospectiva concentrada', 'Exhibition', 'string'),
    ('Exposición sonora', 'Exhibition', 'string'),
    ('Exposición temática', 'Exhibition', 'string'),
    ('Exposición de homenaje', 'Exhibition', 'string'),
    # ('Exposición de homenaje', 'Commemorative', 'string'),
    ('Exposición interactiva', 'Exhibition', 'string'),
    ('Exposición individual', 'Exhibition', 'string'),
    # ('Exposición individual', 'IndividualWork', 'string'),
    ('Exposición documental', 'Exhibition', 'string'),
    ('Obra invitada', 'Exhibition', 'string'),
    ('Exposición inaugural', 'Exhibition', 'string'),
    ('Exposición online', 'Exhibition', 'string'),
    ('Edición', 'Exhibition', 'string'),

    ('Obra de arte', 'WorkManifestation', 'string'),
    ('Esculturas', 'WorkManifestation', 'string'),
    ('Artes visuales', 'VisualWork', 'string'),
    ('Pinturas', 'VisualWork', 'string'),
    ('Obras en papel', 'WorkManifestation', 'string'),
    ('Dibujos', 'WorkManifestation', 'string'),
    ('Grabados', 'WorkManifestation', 'string'),
    ('Bordado', 'WorkManifestation', 'string'),
    ('Acuarelas', 'WorkManifestation', 'string'),
    ('Tabla', 'WorkManifestation', 'string'),
    ('Bocetos', 'WorkManifestation', 'string'),
    ('Mobiliario', 'WorkManifestation', 'string'),
    ('Obras textiles', 'WorkManifestation', 'string'),
    ('Artes decorativas/funcionales', 'WorkManifestation', 'string'),
    ('Joyas', 'WorkManifestation', 'string'),
    ('Espada', 'WorkManifestation', 'string'),
    ('Fotografías', 'WorkManifestation', 'string'),

    ('Dispositivo de inscripción', 'Catalogue', 'string'),
    ('Catálogo de exposiciones', 'Catalogue', 'string'),
    ('Catálogo', 'Catalogue', 'string'),
    ('Propietario', 'Owner', 'string'),
]


def dataframe_from_sql_query(results: Cursor):
    df = pd.DataFrame(results.fetchall())
    field_names = [i[0] for i in cursor.description]
    df.columns = field_names
    return df


def obtener_primer_texto(cadena):
    partes = cadena.split(';')
    for parte in partes:
        if parte.strip() != "":
            return parte.strip()
    return None


def validar_fecha(value: str):
    date1 = None
    if value != '0001-01-01':
        format_date = '%Y-%m-%d'
        global total_dates
        total_dates = total_dates + 1
        try:
            if value:
                date1 = datetime.datetime.strptime(value, format_date).date()
                global count_success
                count_success = count_success + 1
        except ValueError:
            # print('error al transformar la fecha ', value)
            global count_fail
            count_fail = count_fail + 1

    return date1


def procesar_coordenadas(coordenadas):
    # Eliminar el tercer valor (si existe) separando las coordenadas por comas y tomando solo las dos primeras partes
    latitud_longitud = coordenadas.split(',')[:2]

    # Unir nuevamente las dos partes para obtener la latitud y longitud como una sola cadena
    latitud_longitud = ','.join(latitud_longitud)

    # Dividir las coordenadas ahora que solo hay dos partes (latitud y longitud)
    latitud, longitud = latitud_longitud.split(',')

    return latitud, longitud


def is_valid_url(s: str) -> bool:
    """Return True if s looks like a http(s) URL with a netloc."""
    try:
        p = urlparse(s)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def obtain_data_from_personas():
    results_query = cursor.execute("SELECT * FROM PERSONA;")
    df = dataframe_from_sql_query(results_query)
    size = df.size
    cnt = 0
    for row in df.to_dict(orient="records"):
        cnt += 1
        progreso = cnt / size * 100

        # print(f"{cnt} || {size} --> Porcentaje completado: {progreso:.2f}%")

        # if (int(progreso.imag) % 2) == 0:
        #    print(f"{cnt} || {size} --> Porcentaje completado: {progreso:.2f}%")

        # print(row)

        expofinder_id = row['id']
        name = row['nombre']
        tipo = row['tipo']
        genero = row['género']
        lugar_origen = row['lugar de origen']
        fecha_nacimiento = row['fecha de nacimiento']
        fecha_defuncion = row['fecha de defunción']
        direccion_postal = row['dirección postal']
        coordenadas = row['coordenadas']

        if name and name != 'None' and 'sin determinar' not in str(name).lower():
            # toda_la_info = f"{name} - {tipo} - {genero} - {lugar_origen} - {fecha_nacimiento} - {fecha_defuncion} - {
            # coordenadas}"

            # info_hashed = hash_sha256(toda_la_info)
            if tipo:
                clase_tipo = None
                if tipo == 'Individuo':
                    # uri_id = URIRef(f"http://cidoc-crm.org/cidoc-crm/7.1.1/E21_Person")
                    tipo = 'person'
                    # uri_id = URIRef(f"{ontoexhibit}person/{quote(name)}")
                    clase_tipo = URIRef(f"https://cidoc-crm.org/cidoc-crm/7.1.1/E21_Person")

                if tipo == 'Grupo de personas':
                    tipo = 'group'
                    # uri_id = URIRef(f"{ontoexhibit}group/{quote(name)}")
                    clase_tipo = URIRef(f"https://cidoc-crm.org/cidoc-crm/7.1.1/E74_Group")

                normalized = normalize_name(name)
                toda_la_info = f"{normalized} - {tipo}"
                info_hashed = hash_sha256(toda_la_info)
                uri_id = URIRef(f"{ontoexhibit}human_actant/{info_hashed}")
                rdf_graph.add((uri_id, RDF.type, clase_tipo))
                # rdf_graph.add((uri_id, RDFS.label, Literal(f"{name}", datatype=XSD['string'])))

            else:
                tipo = 'human actant'
                normalized = normalize_name(name)
                toda_la_info = f"{normalized} - {tipo}"
                info_hashed = hash_sha256(toda_la_info)
                uri_id = URIRef(f"{ontoexhibit}human_actant/{info_hashed}")
                rdf_graph.add((uri_id, RDF.type, URIRef(f"{ontoexhibit}Human_Actant")))
                # rdf_graph.add((uri_id, RDFS.label, Literal(f"{name}", datatype=XSD['string'])))

            # add name
            if tipo == 'person':
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}person_name"), Literal(f"{name}",
                                                                                    datatype=XSD['string'])))
            elif tipo == 'group':
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}name"), Literal(f"{name}",
                                                                             datatype=XSD['string'])))

            rdf_graph.add((uri_id, RDFS.label, Literal(f"{name}", datatype=XSD['string'])))

            # add género
            if genero and genero != 'None' and genero != 'No declarado':
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}gender"), Literal(f"{genero}",
                                                                               datatype=XSD['string'])))
            # add direccion_postal
            uri_residence = None

            if direccion_postal and direccion_postal != 'None':
                uri_residence = URIRef(f"{ontoexhibit}human_actant/{info_hashed}/residence")
                rdf_graph.add((uri_residence, RDF.type, URIRef(f"{ontoexhibit}Place_Of_Residence")))
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasResidency"), uri_residence))
                rdf_graph.add((uri_residence, URIRef(f"{ontoexhibit}isResidencyOf"), uri_id))
                rdf_graph.add((uri_residence, URIRef(f"{ontoexhibit}address"), Literal(f"{direccion_postal}",
                                                                                       datatype=XSD['string'])))
            # add coordenadas
            if coordenadas and coordenadas != 'None' and direccion_postal and direccion_postal != 'None':
                coordenadas = str(coordenadas)
                
                latitud, longitud = procesar_coordenadas(coordenadas)
                rdf_graph.add((uri_residence, URIRef(f"http://www.w3.org/2003/01/geo/wgs84_pos#lat"),
                               Literal(f"{latitud}", datatype=XSD['string'])))
                rdf_graph.add((uri_residence, URIRef(f"http://www.w3.org/2003/01/geo/wgs84_pos#long"),
                               Literal(f"{longitud}", datatype=XSD['string'])))

            # uri_birth = None
            uri_fecha_nacimiento = None
            uri_lugar_origen = None
            uri_estado_origen = None
            uri_pueblo_ciudad = None
            uri_pais_origen = None
            lugar_nacimiento = None
            lugar = None

            fecha_nacimiento = validar_fecha(fecha_nacimiento)

            if fecha_nacimiento:
                format_date = '%Y-%m-%d'

                if (fecha_nacimiento.month == 1 and fecha_nacimiento.day == 1) \
                        or \
                        (fecha_nacimiento.month == 12 and fecha_nacimiento.day == 31):

                    fecha_nacimiento = str(fecha_nacimiento.year)
                    tipo_indiv = 'Approximate_Date'
                    uri_fecha_nacimiento = URIRef(f"{ontoexhibit}{tipo_indiv.lower()}/{hash_sha256(fecha_nacimiento)}")
                    rdf_graph.add((uri_fecha_nacimiento, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                    rdf_graph.add(
                        (uri_fecha_nacimiento, RDFS.label, Literal(f"{fecha_nacimiento}", datatype=XSD['date'])))
                else:
                    fecha_nacimiento = fecha_nacimiento.strftime(format_date)
                    tipo_indiv = 'Exact_Date'
                    uri_fecha_nacimiento = URIRef(f"{ontoexhibit}{tipo_indiv.lower()}/{hash_sha256(fecha_nacimiento)}")
                    rdf_graph.add((uri_fecha_nacimiento, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                    rdf_graph.add(
                        (uri_fecha_nacimiento, RDFS.label, Literal(f"{fecha_nacimiento}", datatype=XSD['date'])))

            fecha_defuncion = validar_fecha(fecha_defuncion)

            if fecha_defuncion:
                format_date = '%Y-%m-%d'

                if ((fecha_defuncion.month == 1 and fecha_defuncion.day == 1) or
                        (fecha_defuncion.month == 12 and fecha_defuncion.day == 31)):

                    fecha_defuncion = str(fecha_defuncion.year)
                    tipo_indiv = 'Approximate_Date'
                    uri_fecha = URIRef(f"{ontoexhibit}{tipo_indiv.lower()}/{hash_sha256(fecha_defuncion)}")
                    rdf_graph.add((uri_fecha, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                    rdf_graph.add((uri_fecha, RDFS.label, Literal(f"{fecha_defuncion}", datatype=XSD['date'])))

                else:
                    fecha_defuncion = fecha_defuncion.strftime(format_date)
                    tipo_indiv = 'Exact_Date'
                    uri_fecha = URIRef(f"{ontoexhibit}{tipo_indiv.lower()}/{hash_sha256(fecha_defuncion)}")
                    rdf_graph.add((uri_fecha, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                    rdf_graph.add((uri_fecha, RDFS.label, Literal(f"{fecha_defuncion}", datatype=XSD['date'])))

                if tipo == 'person':
                    tipo_indiv = 'Death'
                    uri_death = URIRef(f"{uri_id}/{tipo_indiv.lower()}")
                    rdf_graph.add((uri_death, RDF.type, URIRef(f"https://cidoc-crm.org/cidoc-crm/7.1.1/E69_Death")))
                    rdf_graph.add((uri_death, URIRef(f"{ontoexhibit}hasTimeSpan"), uri_fecha))
                    rdf_graph.add((uri_fecha, URIRef(f"{ontoexhibit}isTimeSpanOf"), uri_death))
                    rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasDeath"), uri_death))
                    rdf_graph.add((uri_death, URIRef(f"{ontoexhibit}isDeathOf"), uri_id))

                elif tipo == 'group':
                    tipo_indiv = 'Dissolution'
                    uri_dissolution = URIRef(f"{uri_id}/{tipo_indiv.lower()}")
                    rdf_graph.add((uri_dissolution, RDF.type,
                                   URIRef(f"https://cidoc-crm.org/cidoc-crm/7.1.1/E68_Dissolution")))
                    rdf_graph.add((uri_dissolution, URIRef(f"{ontoexhibit}hasTimeSpan"), uri_fecha))
                    rdf_graph.add((uri_fecha, URIRef(f"{ontoexhibit}isTimeSpanOf"), uri_dissolution))
                    rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasDissolution"), uri_dissolution))
                    rdf_graph.add((uri_dissolution, URIRef(f"{ontoexhibit}isDissolutionOf"), uri_id))

            if lugar_origen and lugar_origen != 'None':
                parte_pueblo_ciudad = None
                parte_provincia_estado = None
                parte_pais = None

                partes = lugar_origen.split(';')

                if len(partes) >= 1:
                    parte_pueblo_ciudad = partes[0].strip()
                if len(partes) >= 2:
                    parte_provincia_estado = partes[1].strip()
                if len(partes) >= 3:
                    parte_pais = partes[2].strip()

                if parte_pueblo_ciudad and 'desconocido' != parte_pueblo_ciudad.lower():
                    uri_pueblo_ciudad = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_pueblo_ciudad)}")

                    rdf_graph.add((uri_pueblo_ciudad, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_pueblo_ciudad, RDFS.label,
                                   Literal(f"{parte_pueblo_ciudad}", datatype=XSD['string'])))
                    lugar_nacimiento = parte_pueblo_ciudad

                if parte_provincia_estado and 'desconocido' != parte_provincia_estado.lower():
                    uri_estado_origen = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_provincia_estado)}")

                    rdf_graph.add((uri_estado_origen, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_estado_origen, RDFS.label,
                                   Literal(f"{parte_provincia_estado}", datatype=XSD['string'])))
                    if not lugar_nacimiento:
                        lugar_nacimiento = parte_provincia_estado
                    else:
                        lugar_nacimiento = f"{lugar_nacimiento}; {parte_provincia_estado}"

                if parte_pais and 'desconocido' != parte_pais.lower():
                    uri_pais_origen = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_pais)}")

                    rdf_graph.add((uri_pais_origen, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_pais_origen, RDFS.label,
                                   Literal(f"{parte_pais}", datatype=XSD['string'])))
                    if not lugar_nacimiento:
                        lugar_nacimiento = parte_pais
                    else:
                        lugar_nacimiento = f"{lugar_nacimiento}; {parte_pais}"

                if uri_pueblo_ciudad and uri_estado_origen:
                    # Asocio el lugar (ciudad) de origen con el estado
                    rdf_graph.add((uri_pueblo_ciudad, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_estado_origen))
                    rdf_graph.add((uri_estado_origen, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

                if uri_estado_origen and uri_pais_origen:
                    # Asocio el lugar (ciudad) de origen con el estado
                    rdf_graph.add((uri_estado_origen, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_pais_origen))
                    rdf_graph.add((uri_pais_origen, URIRef(f"{ontoexhibit}hasState"), uri_estado_origen))

                if not uri_estado_origen and uri_pueblo_ciudad and uri_pais_origen:
                    rdf_graph.add((uri_pueblo_ciudad, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_pais_origen))
                    rdf_graph.add((uri_pais_origen, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

            if uri_fecha_nacimiento or lugar_nacimiento:

                if uri_fecha_nacimiento:
                    if tipo == 'person':
                        tipo_indiv = 'Birth'

                        uri_birth = URIRef(f"{uri_id}/{tipo_indiv.lower()}")
                        rdf_graph.add((uri_birth, RDF.type, URIRef(f"https://cidoc-crm.org/cidoc-crm/7.1.1/E67_Birth")))

                        rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasBirth"), uri_birth))
                        rdf_graph.add((uri_birth, URIRef(f"{ontoexhibit}isBirthOf"), uri_id))

                        rdf_graph.add((uri_birth, URIRef(f"{ontoexhibit}hasTimeSpan"), uri_fecha_nacimiento))
                        rdf_graph.add((uri_fecha_nacimiento, URIRef(f"{ontoexhibit}isTimeSpanOf"), uri_birth))

                    elif tipo == 'group':
                        tipo_indiv = 'Foundation'

                        uri_fundation = URIRef(f"{uri_id}/{tipo_indiv.lower()}")
                        rdf_graph.add((uri_fundation, RDF.type, URIRef(f"{ontoexhibit}Foundation")))

                        rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasFoundation"), uri_fundation))
                        rdf_graph.add((uri_fundation, URIRef(f"{ontoexhibit}isFoundationOf"), uri_id))

                        rdf_graph.add((uri_fundation, URIRef(f"{ontoexhibit}hasTimeSpan"), uri_fecha_nacimiento))
                        rdf_graph.add((uri_fecha_nacimiento, URIRef(f"{ontoexhibit}isTimeSpanOf"), uri_fundation))

                if lugar_nacimiento:
                    uri_lugar_origen = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(lugar_nacimiento)}")

                    rdf_graph.add((uri_lugar_origen, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_lugar_origen, RDFS.label,
                                   Literal(f"{lugar_nacimiento}", datatype=XSD['string'])))

                    if tipo == 'person':
                        rdf_graph.add((uri_birth, URIRef(f"{ontoexhibit}hasPlaceOfBirth"), uri_lugar_origen))
                        rdf_graph.add((uri_lugar_origen, URIRef(f"{ontoexhibit}isPlaceOfBirthOf"), uri_birth))

                    elif tipo == 'group':
                        rdf_graph.add((uri_fundation, URIRef(f"{ontoexhibit}hasPlaceOfFoundation"), uri_lugar_origen))
                        rdf_graph.add((uri_lugar_origen, URIRef(f"{ontoexhibit}isPlaceOfFoundationOf"), uri_fundation))

            # TODO: EL CAMPO DIRECCION POSTAL NO SIGUE NINGUN PATRON, ES DIFICIL SABER QUE ES UN PHYSICAL SITE,
            #  QUE ES UN TERRITORIAL_ENTITY, ETC... ALGUNOS REGISTROS DE EJEMPLO:
            """
            Oslo, Noruega
            Guatemala
            Baguio, Región Administrativa de La Cordillera, 2600, Filipinas
            Long Branch, Monmouth County, Nueva Jersey, 07740, Estados Unidos de América
            Desconocido
            Río de Janeiro, Região Geográfica Imediata do Rio de Janeiro, Região Metropolitana do Rio de Janeiro, Região Geográfica Intermediária do Rio de Janeiro, Río de Janeiro, Región Sudeste, Brasil
            Elm Grove, Hanover & Queen's Park, Round Hill, Brighton, Brighton and Hove, Inglaterra, BN2 3DB, Reino Unido
            """
            """
            if direccion_postal and direccion_postal != 'None':
                pueblo_ciudad = None
                provincia_estado = None
                pais = None

                partes = direccion_postal.split(';')

                if len(partes) >= 1:
                    pueblo_ciudad = partes[0].strip()
                if len(partes) >= 2:
                    provincia_estado = partes[1].strip()
                if len(partes) >= 3:
                    pais = partes[2].strip()

                if pueblo_ciudad and 'desconocido' != pueblo_ciudad.lower():
                    uri_pueblo = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(pueblo_ciudad)}")

                    rdf_graph.add((uri_pueblo, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_pueblo, RDFS.label,
                                   Literal(f"{pueblo_ciudad}", datatype=XSD['string'])))
                    lugar = pueblo_ciudad

                if provincia_estado and 'desconocido' != provincia_estado.lower():
                    uri_estado = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(provincia_estado)}")

                    rdf_graph.add((uri_estado, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_estado, RDFS.label,
                                   Literal(f"{provincia_estado}", datatype=XSD['string'])))
                    if not lugar:
                        lugar = provincia_estado
                    else:
                        lugar = f"{lugar}; {provincia_estado}"

                if pais and 'desconocido' != pais.lower():
                    uri_pais = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(pais)}")

                    rdf_graph.add((uri_pais, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_pais, RDFS.label,
                                   Literal(f"{pais}", datatype=XSD['string'])))
                    if not lugar:
                        lugar = pais
                    else:
                        lugar = f"{lugar}; {pais}"

                if uri_pueblo and uri_estado:
                    # Asocio el lugar (ciudad) de origen con el estado
                    rdf_graph.add((uri_pueblo, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_estado))
                    rdf_graph.add((uri_estado, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo))

                if uri_estado and uri_pais:
                    # Asocio el lugar (ciudad) de origen con el estado
                    rdf_graph.add((uri_estado, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_pais))
                    rdf_graph.add((uri_pais, URIRef(f"{ontoexhibit}hasState"), uri_estado))

                if not uri_estado and uri_pueblo and uri_pais:
                    rdf_graph.add((uri_pueblo, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_pais))
                    rdf_graph.add((uri_pais, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo))

                if lugar:
                    uri_lugar = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(lugar)}")
                    rdf_graph.add((uri_lugar, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_lugar, RDFS.label,
                                   Literal(f"{lugar}", datatype=XSD['string'])))

                    if tipo == 'person':
                        tipo_indiv = 'Place_Of_Residence'

                        uri_place_of_res = URIRef(f"{uri_id}/{tipo_indiv.lower()}")
                        rdf_graph.add((uri_place_of_res, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))

                        rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasResidency"), uri_place_of_res))
                        rdf_graph.add((uri_place_of_res, URIRef(f"{ontoexhibit}isResidencyOf"), uri_id))

                        rdf_graph.add((uri_lugar, URIRef(f"{ontoexhibit}hasPlaceOfResidency"),
                                       uri_place_of_res))

                        rdf_graph.add((uri_place_of_res, URIRef(f"{ontoexhibit}isPlaceOfResidencyOf"),
                                       uri_lugar))

                    elif tipo == 'group':
                        tipo_indiv = 'Place_Of_Activity'

                        uri_place_of_activity = URIRef(f"{uri_id}/{tipo_indiv.lower()}")
                        rdf_graph.add((uri_place_of_activity, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))

                        rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasPlaceOfActivity"), uri_place_of_activity))
                        rdf_graph.add((uri_place_of_activity, URIRef(f"{ontoexhibit}isPlaceOfActivityOf"), uri_id))

                        rdf_graph.add((uri_lugar, URIRef(f"{ontoexhibit}hasPlaceForActivity"),
                                       uri_place_of_activity))

                        rdf_graph.add((uri_place_of_activity, URIRef(f"{ontoexhibit}isPlaceForActivityOf"),
                                       uri_lugar))

                    if coordenadas and coordenadas != 'None':
                        coordenadas = str(coordenadas)
                        latitud, longitud = procesar_coordenadas(coordenadas)
                        rdf_graph.add((uri_lugar, URIRef(f"http://www.w3.org/2003/01/geo/wgs84_pos#lat"),
                                       Literal(f"{latitud}", datatype=XSD['string'])))
                        rdf_graph.add((uri_lugar, URIRef(f"http://www.w3.org/2003/01/geo/wgs84_pos#long"),
                                       Literal(f"{longitud}", datatype=XSD['string'])))
            """
            if expofinder_id and expofinder_id != 'None':
                rdf_graph.add(
                    (uri_id, URIRef(f"{ontoexhibit}expofinderId"), Literal(f"{expofinder_id}", datatype=XSD['string'])))

    results_query_actividad = cursor.execute(
        """
        SELECT p.nombre AS nombre_persona, p.tipo AS tipo, a.nombre AS actividad
        FROM PERSONA p 
        INNER JOIN ACTIVIDAD_PERSONA ap ON ap.id_persona=p.id
        INNER JOIN ACTIVIDAD a ON a.id=ap.id_actividad
        WHERE actividad not like 'Listo';
        """
    )
    df = dataframe_from_sql_query(results_query_actividad)

    for row in df.to_dict(orient="records"):
        nombre_persona = row['nombre_persona']
        tipo_persona = row['tipo']
        actividad = row['actividad']
        if nombre_persona and nombre_persona != 'None' and 'sin determinar' not in str(nombre_persona).lower():
            if tipo_persona != 'None' and tipo_persona == 'Individuo':
                tipo_persona = 'person'

            elif tipo_persona != 'None' and tipo_persona == 'Grupo de personas':
                tipo_persona = 'group'
            else:
                tipo_persona = 'human actant'

            toda_la_info = f"{nombre_persona} - {tipo_persona}"
            info_hashed = hash_sha256(toda_la_info)
            uri_id = URIRef(f"{ontoexhibit}human_actant/{info_hashed}")
            rdf_graph.add(
                (uri_id, URIRef(f"{ontoexhibit}activity_type"), Literal(f"{actividad}", datatype=XSD['string'])))

    results_query_lenders_personas = cursor.execute(
        """
        SELECT * FROM (
            SELECT p.nombre AS nombre_persona, p.tipo AS tipo, e.id AS id_exposicion, e.nombre AS nombre_exposicion
            FROM COLECCIONISTA_PRESTATARIO_PERSONA_EXPOSICION cpp
            INNER JOIN PERSONA p ON p.id=cpp.id_persona
            INNER JOIN EXPOSICION e ON e.id=cpp.id_exposicion)
        UNION
        SELECT * FROM(
            SELECT p.nombre as nombre_persona, p.tipo as tipo, e.id AS id_exposicion, e.nombre AS nombre_exposicion
            FROM COLECCIONISTA_PRESTATARIO_PERSONA_EXPOSICION cpp
            INNER JOIN PERSONA p ON p.id=cpp.id_persona
            INNER JOIN EXPOSICION e ON e.id=cpp.id_exposicion)
        ;
        """
    )
    df = dataframe_from_sql_query(results_query_lenders_personas)

    for row in df.to_dict(orient="records"):
        nombre_persona = row['nombre_persona']
        tipo_persona = row['tipo']
        nombre_exposicion = row['nombre_exposicion']
        id_exposicion = row['id_exposicion']

        if nombre_persona and nombre_persona != 'None' and 'sin determinar' not in str(nombre_persona).lower():
            if tipo_persona != 'None' and tipo_persona == 'Individuo':
                tipo_persona = 'person'
            elif tipo_persona != 'None' and tipo_persona == 'Grupo de personas':
                tipo_persona = 'group'
            else:
                tipo_persona = 'human actant'

            toda_la_info_persona = f"{nombre_persona} - {tipo_persona}"
            toda_la_info_persona = hash_sha256(toda_la_info_persona)

            toda_la_info_exposicion = hash_sha256(f"{id_exposicion} - {nombre_exposicion}")
            uri_id_persona = URIRef(f"{ontoexhibit}human_actant/{toda_la_info_persona}")
            uri_id_exposicion = URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}")
            uri_id_lender = \
                URIRef(f"{ontoexhibit}human_actant/{toda_la_info_persona}/lender/{toda_la_info_exposicion}")

            rdf_graph.add((uri_id_lender, RDF.type, URIRef(f"{ontoexhibit}Lender")))

            rdf_graph.add((uri_id_lender, RDFS.label,
                           Literal(f"{nombre_persona} ({uri_id_persona}) was lender at "
                                   f"{nombre_exposicion} ({uri_id_exposicion})", datatype=XSD['string'])))

            rdf_graph.add((uri_id_persona, URIRef(f"{ontoexhibit}hasRole"), uri_id_lender))
            rdf_graph.add((uri_id_lender, URIRef(f"{ontoexhibit}isRoleOf"), uri_id_persona))

            uri_id_exhibition_making = \
                URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}/exhibition_making")

            rdf_graph.add((uri_id_exhibition_making, RDF.type, URIRef(f"{ontoexhibit}Exhibition_Making")))

            rdf_graph.add((uri_id_exposicion, URIRef(f"{ontoexhibit}hasExhibitionMaking"), uri_id_exhibition_making))
            rdf_graph.add((uri_id_exhibition_making, URIRef(f"{ontoexhibit}isExhibitionMakingOf"), uri_id_exposicion))# ¿madeExhibition? ¿old?

            rdf_graph.add((uri_id_exhibition_making, URIRef(f"{ontoexhibit}hasLender"), uri_id_lender))
            rdf_graph.add((uri_id_lender, URIRef(f"{ontoexhibit}isLenderOf"), uri_id_exhibition_making))

    results_query_relacion_persona_persona = cursor.execute(
        """
        SELECT 
            p1.nombre AS nombre_persona1, p1.tipo AS tipo_persona1, 
            p2.nombre AS nombre_persona2, p2.tipo AS tipo_persona2
        FROM RELACION_PERSONA_PERSONA rpp
        INNER JOIN PERSONA p1 on p1.id=rpp.id_persona
        INNER JOIN PERSONA p2 on p2.id=rpp.id_persona_2;
        """
    )

    df = dataframe_from_sql_query(results_query_relacion_persona_persona)
    for row in df.to_dict(orient="records"):
        nombre_p1 = row['nombre_persona1']
        nombre_p2 = row['nombre_persona2']
        tipo_p1 = row['tipo_persona1']
        tipo_p2 = row['tipo_persona2']

        uri_persona1 = None
        uri_persona2 = None

        if nombre_p1 and nombre_p1 != 'None' and 'sin determinar' not in str(nombre_p1).lower():
            if tipo_p1:
                if tipo_p1 == 'Individuo':
                    tipo_p1 = 'person'
                if tipo_p1 == 'Grupo de personas':
                    tipo_p1 = 'group'
            else:
                tipo_p1 = 'human actant'

            info_p1_hashed = hash_sha256(f"{nombre_p1} - {tipo_p1}")
            uri_persona1 = URIRef(f"{ontoexhibit}human_actant/{info_p1_hashed}")

        if nombre_p2 and nombre_p2 != 'None' and 'sin determinar' not in str(nombre_p2).lower():
            if tipo_p2:
                if tipo_p2 == 'Individuo':
                    tipo_p2 = 'person'
                if tipo_p2 == 'Grupo de personas':
                    tipo_p2 = 'group'
            else:
                tipo_p2 = 'human actant'

            info_p2_hashed = hash_sha256(f"{nombre_p2} - {tipo_p2}")
            uri_persona2 = URIRef(f"{ontoexhibit}human_actant/{info_p2_hashed}")

        if uri_persona1 and uri_persona2 and tipo_p1 == 'person' and tipo_p2 == 'group':
            uri_membership = URIRef(f"{ontoexhibit}human_actant/{info_p1_hashed}/membership/{info_p2_hashed}")
            rdf_graph.add((uri_membership, RDF.type, URIRef(f"{ontoexhibit}Membership")))
            
            rdf_graph.add((uri_persona1, URIRef(f"{ontoexhibit}hasMembership"), uri_membership))
            rdf_graph.add((uri_membership, URIRef(f"{ontoexhibit}isMembershipOf"), uri_persona1))

            rdf_graph.add((uri_persona2, URIRef(f"{ontoexhibit}hasMember"), uri_membership))
            rdf_graph.add((uri_membership, URIRef(f"{ontoexhibit}isMemberOf"), uri_persona2))
        
        if uri_persona1 and uri_persona2 and tipo_p1 == 'group' and tipo_p2 == 'person':
            uri_membership = URIRef(f"{ontoexhibit}human_actant/{info_p1_hashed}/membership/{info_p2_hashed}")
            rdf_graph.add((uri_membership, RDF.type, URIRef(f"{ontoexhibit}Membership")))
            
            rdf_graph.add((uri_persona1, URIRef(f"{ontoexhibit}hasMember"), uri_membership))
            rdf_graph.add((uri_membership, URIRef(f"{ontoexhibit}isMemberOf"), uri_persona1))

            rdf_graph.add((uri_membership, URIRef(f"{ontoexhibit}isMembershipOf"), uri_persona2))
            rdf_graph.add((uri_persona2, URIRef(f"{ontoexhibit}hasMembership"), uri_membership))

    results_query_relacion_persona_institucion = cursor.execute(
        """
        SELECT DISTINCT 
            p.nombre AS nombre_persona, p.tipo AS tipo_persona, 
            i.nombre AS nombre_institucion
        FROM RELACION_PERSONA_INSTITUCION rpp
        INNER JOIN PERSONA p on p.id=rpp.id_persona
        INNER JOIN INSTITUCION i on i.id=rpp.id_institucion
        """
    )

    df = dataframe_from_sql_query(results_query_relacion_persona_institucion)

    for row in df.to_dict(orient="records"):
        nombre_persona = row['nombre_persona']
        tipo_persona = row['tipo_persona']
        nombre_institucion = row['nombre_institucion']
        uri_institucion = None
        uri_persona = None

        if (nombre_institucion and nombre_institucion != 'None'
                and 'sin determinar' not in str(nombre_institucion).lower()):
            info_institucion_hashed = hash_sha256(f"{nombre_institucion}")
            uri_institucion = URIRef(f"{ontoexhibit}institution/{info_institucion_hashed}")

        if (nombre_persona and nombre_persona != 'None'
                and 'sin determinar' not in str(nombre_persona).lower()):

            if tipo_persona:
                if tipo_persona == 'Individuo':
                    tipo_persona = 'person'
                if tipo_persona == 'Grupo de personas':
                    tipo_persona = 'group'
            else:
                tipo_persona = 'human actant'

            info_persona_hashed = hash_sha256(f"{nombre_persona} - {tipo_persona}")
            uri_persona = URIRef(f"{ontoexhibit}human_actant/{info_persona_hashed}")

        if uri_institucion and uri_persona:
            uri_affiliation = URIRef(f"{ontoexhibit}human_actant/{info_persona_hashed}/affiliation/{info_institucion_hashed}")
            rdf_graph.add((uri_affiliation, RDF.type, URIRef(f"{ontoexhibit}Affiliation")))
            
            rdf_graph.add((uri_persona, URIRef(f"{ontoexhibit}hasAffiliation"), uri_affiliation))
            rdf_graph.add((uri_affiliation, URIRef(f"{ontoexhibit}isAffiliationOf"), uri_persona))
            
            rdf_graph.add((uri_institucion, URIRef(f"{ontoexhibit}hasAffiliated"), uri_affiliation))
            rdf_graph.add((uri_affiliation, URIRef(f"{ontoexhibit}isAffiliatedWith"), uri_institucion))



def obtain_data_from_institucion():
    results_query = cursor.execute(
        "SELECT "
        "   i.id, i.nombre, `nombre alternativo`, t.nombre AS tipo, i.titularidad, `lugar de la sede`,"
        "   p.nombre AS `máximo responsable`, p.tipo AS tipo_persona, i.coordenadas AS coordenadas, `URI HTML`, "
        "   `URI RSS`, fax, `teléfono`, `correo electrónico`, `página web`, i.`dirección postal` "
        "   FROM INSTITUCION i "
        "   LEFT JOIN TIPOLOGIA_INSTITUCION ti ON i.id = ti.id_institucion "
        "   LEFT JOIN TIPOLOGIA t ON t.id=ti.id_tipologia "
        "   LEFT JOIN PERSONA p ON p.id = `máximo responsable`;")

    df = dataframe_from_sql_query(results_query)

    for row in df.to_dict(orient="records"):
        expofinder_id = row['id']
        name = row['nombre']
        nombre_alternativo = row['nombre alternativo']
        tipo = row['tipo']
        tipo_persona = row['tipo_persona']
        titularidad = row['titularidad']
        lugar_sede = row['lugar de la sede']
        direccion_sede = row['dirección postal']
        maximo_responsable = row['máximo responsable']
        coordenadas = row['coordenadas']

        uri_html = row['URI HTML']
        uri_rss = row['URI RSS']
        email = row['correo electrónico']
        fax = row['fax']
        telefono = row['teléfono']
        pagina_web = row['página web']

        # toda_la_info = f"{name} - {nombre_alternativo} - {tipo} - {titularidad} - {lugar_sede} - {
        # maximo_responsable} - {coordenadas}"
        uri_estado_origen = None
        uri_pueblo_ciudad = None
        uri_pais_origen = None

        if name and name != 'None' and 'sin determinar' not in str(name).lower():
            toda_la_info = normalize_name(f"{name}")
            info_hashed = hash_sha256(toda_la_info)

            position = None

            for i, v in enumerate(classes):
                if v[0] == tipo:
                    position = i
            if position:
                tipo = classes[position][1]
                # tipo = URIRef(ontoexhibit[mapping])
            else:
                tipo = 'Institution'

            uri_id = URIRef(f"{ontoexhibit}institution/{info_hashed}")
            rdf_graph.add((uri_id, RDF.type, URIRef(f"{ontoexhibit}{tipo}")))
            rdf_graph.add((uri_id, RDFS.label, Literal(f"{name}", datatype=XSD['string'])))
            rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}name"), Literal(f"{name}", datatype=XSD['string'])))

            # TODO: preguntar a NURIA. No puede ser hasVenue porque eso es para SITE,
            #  y lo que nos viene de las bbdd es un territorial entity. OCURRE LO MISMO EN LA TABLA EMPRESA.
            #  PROPUESTA: ¿quizas se debe usar para esto lugar de actividad de la ontología? CORRECTO...

            if lugar_sede and lugar_sede != 'None' and 'sin determinar' not in str(lugar_sede).lower():
                # lugar_sede = str(lugar_sede).replace('Desconocido', '')
                parte_pueblo_ciudad = None
                parte_provincia_estado = None
                parte_pais = None

                partes = lugar_sede.split(';')

                # Asignar las partes a las variables correspondientes si existen
                if len(partes) >= 1:
                    parte_pueblo_ciudad = partes[0].strip()
                if len(partes) >= 2:
                    parte_provincia_estado = partes[1].strip()
                if len(partes) >= 3:
                    parte_pais = partes[2].strip()

                lugar = None

                if parte_pueblo_ciudad and 'desconocido' != parte_pueblo_ciudad.lower():
                    uri_pueblo_ciudad = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_pueblo_ciudad)}")

                    rdf_graph.add((uri_pueblo_ciudad, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_pueblo_ciudad, RDFS.label,
                                   Literal(f"{parte_pueblo_ciudad}", datatype=XSD['string'])))

                    lugar = parte_pueblo_ciudad

                if parte_provincia_estado and 'desconocido' != parte_provincia_estado.lower():
                    uri_estado_origen = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_provincia_estado)}")

                    rdf_graph.add((uri_estado_origen, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_estado_origen, RDFS.label,
                                   Literal(f"{parte_provincia_estado}", datatype=XSD['string'])))

                    if not lugar:
                        lugar = parte_provincia_estado
                    else:
                        lugar = f"{lugar}; {parte_provincia_estado}"

                if parte_pais and 'desconocido' != parte_pais.lower():
                    uri_pais_origen = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_pais)}")

                    rdf_graph.add((uri_pais_origen, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_pais_origen, RDFS.label,
                                   Literal(f"{parte_pais}", datatype=XSD['string'])))
                    if not lugar:
                        lugar = parte_pais
                    else:
                        lugar = f"{lugar}; {parte_pais}"

                if lugar:
                    # lugar_sede = re.sub(r'\s*;\s*', '; ', lugar_sede)
                    uri_lugar_sede = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(lugar)}")
                    rdf_graph.add((uri_lugar_sede, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_lugar_sede, RDFS.label, Literal(f"{lugar}", datatype=XSD['string'])))

                    # TODO: Revisar en fastapi
                    uri_location = URIRef(f"{uri_id}/location")
                    rdf_graph.add((uri_location, RDF.type, URIRef(f"{ontoexhibit}Location")))

                    rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasLocation"), uri_location))
                    rdf_graph.add((uri_location, URIRef(f"{ontoexhibit}isLocationOf"), uri_id))

                    rdf_graph.add((uri_location, URIRef(f"{ontoexhibit}hasPlaceOfLocation"), uri_lugar_sede))
                    rdf_graph.add((uri_lugar_sede, URIRef(f"{ontoexhibit}isPlaceOfLocationOf"), uri_location))

                    if uri_pueblo_ciudad:
                        rdf_graph.add((uri_lugar_sede, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

                    if uri_estado_origen:
                        rdf_graph.add((uri_lugar_sede, URIRef(f"{ontoexhibit}hasState"), uri_estado_origen))

                    if uri_pais_origen:
                        rdf_graph.add((uri_lugar_sede, URIRef(f"{ontoexhibit}hasCountry"), uri_pais_origen))

                if uri_pueblo_ciudad and uri_estado_origen:
                    # Asocio el lugar (ciudad) de origen con el estado
                    rdf_graph.add((uri_pueblo_ciudad, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_estado_origen))
                    rdf_graph.add((uri_estado_origen, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

                if uri_estado_origen and uri_pais_origen:
                    # Asocio el lugar (ciudad) de origen con el estado
                    rdf_graph.add((uri_estado_origen, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_pais_origen))
                    rdf_graph.add((uri_pais_origen, URIRef(f"{ontoexhibit}hasState"), uri_estado_origen))

                if not uri_estado_origen and uri_pueblo_ciudad and uri_pais_origen:
                    rdf_graph.add((uri_pueblo_ciudad, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_pais_origen))
                    rdf_graph.add((uri_pais_origen, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

                # TODO: EL CAMPO DIRECCION POSTAL NO SIGUE NINGUN PATRON, ES DIFICIL SABER QUE ES UN PHYSICAL SITE,
                #  QUE ES UN TERRITORIAL_ENTITY, ETC...:
                
                if direccion_sede:
                    uri_dir_sede = URIRef(f"{ontoexhibit}physical_site/{hash_sha256(direccion_sede)}")
                    rdf_graph.add((uri_dir_sede, RDF.type, URIRef(f"{ontoexhibit}Physical_Site")))
                    rdf_graph.add((uri_dir_sede, RDFS.label, Literal(f"{direccion_sede}",
                                                                     datatype=XSD['string'])))

                    uri_headquarter = URIRef(f"{uri_id}/headquarter")
                    rdf_graph.add((uri_headquarter, RDF.type, URIRef(f"{ontoexhibit}Headquarter")))

                    rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasHeadquarters"), uri_headquarter))
                    rdf_graph.add((uri_headquarter, URIRef(f"{ontoexhibit}isHeadquartersOf"), uri_id))

                    rdf_graph.add((uri_headquarter, URIRef(f"{ontoexhibit}isHeadquarteredAt"), uri_dir_sede))
                    rdf_graph.add((uri_dir_sede, URIRef(f"{ontoexhibit}isSiteOfHeadquartersOf"), uri_headquarter))

                    if coordenadas and coordenadas != 'None':
                        coordenadas = str(coordenadas)

                        latitud, longitud = procesar_coordenadas(coordenadas)
                        rdf_graph.add((uri_headquarter, URIRef(f"http://www.w3.org/2003/01/geo/wgs84_pos#lat"),
                                       Literal(f"{latitud}", datatype=XSD['string'])))
                        rdf_graph.add((uri_headquarter, URIRef(f"http://www.w3.org/2003/01/geo/wgs84_pos#long"),
                                       Literal(f"{longitud}", datatype=XSD['string'])))
                

            # DATA PROPERTIES
            if titularidad and titularidad != 'None':
                if 'Titularidad pública' == titularidad:
                    titularidad = 'public'
                elif 'Titularidad privada' == titularidad:
                    titularidad = 'private'
                else:
                    titularidad = 'mixed'
                rdf_graph.add(
                    (uri_id, URIRef(f"{ontoexhibit}ownershipType"), Literal(f"{titularidad}", datatype=XSD['string'])))
            """
            if uri_html and uri_html != 'None':
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}webPage"), Literal(uri_html, datatype=XSD['string'])))
            """
            """
            if uri_rss and uri_rss != 'None':
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}uriRss"), Literal(f"{uri_rss}", datatype=XSD['string'])))
            """
            if email and email != 'None':
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}email"), Literal(f"{email}", datatype=XSD['string'])))

            """
            if fax and fax != 'None':
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}fax"), Literal(f"{fax}", datatype=XSD['string'])))
            """

            if telefono and telefono != 'None':
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}phone"),
                               Literal(f"{telefono}", datatype=XSD['string'])))

            if maximo_responsable and maximo_responsable != 'None':
                if tipo_persona:
                    if tipo_persona == 'Individuo':
                        tipo_persona = 'person'
                    if tipo_persona == 'Grupo de personas':
                        tipo_persona = 'group'
                else:
                    tipo_persona = 'human actant'

                maximo_responsable_hashed = hash_sha256(f"{maximo_responsable} - {tipo_persona}")
                uri_persona_responsable = URIRef(f"{ontoexhibit}human_actant/{maximo_responsable_hashed}")
                uri_maximo_responsable = URIRef(f"{uri_id}/executive_position/{maximo_responsable_hashed}")

                rdf_graph.add((uri_maximo_responsable, RDF.type, URIRef(f"{ontoexhibit}Executive_Position")))
                rdf_graph.add((uri_maximo_responsable, RDFS.label,
                               Literal(f"{maximo_responsable} ({uri_persona_responsable}) was "
                                       f"representative of {name} ({uri_id})", datatype=XSD['string'])))

                rdf_graph.add((URIRef(f"{ontoexhibit}human_actant/{maximo_responsable_hashed}"),
                               URIRef(f"{ontoexhibit}holdsExecutivePosition"), uri_maximo_responsable))

                rdf_graph.add((uri_maximo_responsable, URIRef(f"{ontoexhibit}isExecutivePositionOf"),
                               URIRef(f"{ontoexhibit}human_actant/{maximo_responsable_hashed}")))

                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}executivePositionHeldsBy"), uri_maximo_responsable))
                rdf_graph.add((uri_maximo_responsable, URIRef(f"{ontoexhibit}executivePositionHeldsIn"), uri_id))

            if (nombre_alternativo and nombre_alternativo != 'None'
                    and 'desconocido' not in str(nombre_alternativo).lower()
                    and 'sin determinar' not in str(nombre_alternativo).lower()):
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}apelation"),
                               Literal(f"{nombre_alternativo}", datatype=XSD['string'])))

            if expofinder_id and expofinder_id != 'None':
                rdf_graph.add(
                    (uri_id, URIRef(f"{ontoexhibit}expofinderId"), Literal(f"{expofinder_id}", datatype=XSD['string'])))

            if pagina_web and pagina_web != 'None':
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}webPage"), Literal(pagina_web, datatype=XSD['string'])))

    results_query_lenders_institucion = cursor.execute(
        """
       SELECT * FROM (
            SELECT p.nombre AS nombre_institucion, e.id AS id_exposicion, e.nombre AS nombre_exposicion
            FROM COLECCIONISTA_PRESTATARIO_INSTITUCION_EXPOSICION cpp
            INNER JOIN INSTITUCION p ON p.id=cpp.id_institucion
            INNER JOIN EXPOSICION e ON e.id=cpp.id_exposicion)
        UNION
        SELECT * FROM(
            SELECT p.nombre as nombre_institucion, e.id AS id_exposicion, e.nombre AS nombre_exposicion
            FROM COLECCIONISTA_PRESTATARIO_INSTITUCION_EXPOSICION cpp
            INNER JOIN INSTITUCION p ON p.id=cpp.id_institucion
            INNER JOIN EXPOSICION e ON e.id=cpp.id_exposicion)
        ;
        """
    )
    df = dataframe_from_sql_query(results_query_lenders_institucion)

    for row in df.to_dict(orient="records"):
        nombre_institucion = row['nombre_institucion']
        nombre_exposicion = row['nombre_exposicion']
        id_exposicion = row['id_exposicion']

        if (nombre_institucion and nombre_institucion != 'None'
                and 'sin determinar' not in str(nombre_institucion).lower()):
            toda_la_info_institucion = normalize_name(f"{nombre_institucion}")
            toda_la_info_institucion = hash_sha256(toda_la_info_institucion)

            toda_la_info_exposicion = hash_sha256(f"exhibition - {normalize_name(nombre_exposicion)}")
            uri_id_institution = URIRef(f"{ontoexhibit}institution/{toda_la_info_institucion}")
            uri_id_exposicion = URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}")

            uri_id_lender = \
                URIRef(f"{ontoexhibit}institution/{toda_la_info_institucion}/lender/{toda_la_info_exposicion}")

            rdf_graph.add((uri_id_lender, RDF.type, URIRef(f"{ontoexhibit}Lender")))
            rdf_graph.add((uri_id_lender, RDFS.label,
                           Literal(f"{nombre_institucion} ({uri_id_institution}) was lender at "
                                   f"{nombre_exposicion} ({uri_id_exposicion})", datatype=XSD['string'])))

            rdf_graph.add((uri_id_institution, URIRef(f"{ontoexhibit}hasRole"), uri_id_lender))
            rdf_graph.add((uri_id_lender, URIRef(f"{ontoexhibit}isRoleOf"), uri_id_institution))

            uri_id_exhibition_making = \
                URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}/exhibition_making")

            rdf_graph.add((uri_id_exhibition_making, RDF.type, URIRef(f"{ontoexhibit}Exhibition_Making")))

            rdf_graph.add((uri_id_exposicion, URIRef(f"{ontoexhibit}hasExhibitionMaking"), uri_id_exhibition_making))
            rdf_graph.add((uri_id_exhibition_making, URIRef(f"{ontoexhibit}isExhibitionMakingOf"), uri_id_exposicion))

            rdf_graph.add((uri_id_exhibition_making, URIRef(f"{ontoexhibit}hasLender"), uri_id_lender))
            rdf_graph.add((uri_id_lender, URIRef(f"{ontoexhibit}isLenderOf"), uri_id_exhibition_making))

    results_query_financier_institucion = cursor.execute(
        """
       SELECT * FROM (
            SELECT p.nombre AS nombre_institucion, e.id AS id_exposicion, e.nombre AS nombre_exposicion
            FROM PATROCINIO_EXPOSICION_INSTITUCION cpp
            INNER JOIN INSTITUCION p ON p.id=cpp.id_institucion
            INNER JOIN EXPOSICION e ON e.id=cpp.id_exposicion)
        UNION
        SELECT * FROM(
            SELECT p.nombre as nombre_institucion, e.id AS id_exposicion, e.nombre AS nombre_exposicion 
            FROM PATROCINIO_EXPOSICION_INSTITUCION cpp
            INNER JOIN INSTITUCION p ON p.id=cpp.id_institucion
            INNER JOIN EXPOSICION e ON e.id=cpp.id_exposicion)
        ;
        """
    )
    df = dataframe_from_sql_query(results_query_financier_institucion)

    for row in df.to_dict(orient="records"):
        nombre_institucion = row['nombre_institucion']
        nombre_exposicion = row['nombre_exposicion']
        id_exposicion = row['id_exposicion']

        if (nombre_institucion and nombre_institucion != 'None'
                and 'sin determinar' not in str(nombre_institucion).lower()):
            toda_la_info_institucion = normalize_name(f"{nombre_institucion}")
            toda_la_info_institucion = hash_sha256(toda_la_info_institucion)

            toda_la_info_exposicion = hash_sha256(f"exhibition - {normalize_name(nombre_exposicion)}")
            uri_id_institution = URIRef(f"{ontoexhibit}institution/{toda_la_info_institucion}")
            uri_id_exposicion = URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}")

            uri_id_financier = \
                URIRef(f"{ontoexhibit}institution/{toda_la_info_institucion}/financer/{toda_la_info_exposicion}")

            rdf_graph.add((uri_id_financier, RDF.type, URIRef(f"{ontoexhibit}Financer")))
            rdf_graph.add((uri_id_financier, RDFS.label,
                           Literal(f" {nombre_institucion} ({uri_id_institution}) was financer of "
                                   f"{nombre_exposicion} ({uri_id_exposicion})", datatype=XSD['string'])))

            rdf_graph.add((uri_id_institution, URIRef(f"{ontoexhibit}hasRole"), uri_id_financier))
            rdf_graph.add((uri_id_financier, URIRef(f"{ontoexhibit}isRoleOf"), uri_id_institution))

            uri_id_exhibition_making = \
                URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}/exhibition_making")

            rdf_graph.add((uri_id_exhibition_making, RDF.type, URIRef(f"{ontoexhibit}Exhibition_Making")))

            rdf_graph.add((uri_id_exposicion, URIRef(f"{ontoexhibit}hasExhibitionMaking"), uri_id_exhibition_making))
            rdf_graph.add((uri_id_exhibition_making, URIRef(f"{ontoexhibit}isExhibitionMakingOf"), uri_id_exposicion))

            rdf_graph.add((uri_id_exhibition_making, URIRef(f"{ontoexhibit}hasFunder"), uri_id_financier))
            rdf_graph.add(
                (uri_id_financier, URIRef(f"{ontoexhibit}isFunderOf"), uri_id_exhibition_making)
            )

    results_query_instituciones_matriz = cursor.execute(
        """
        SELECT i.nombre AS nombre_institucion_padre, i2.nombre AS nombre_institucion_hijo
        FROM INSTITUCION_MATRIZ im
        INNER JOIN INSTITUCION i ON i.id=id_institucion_padre
        INNER JOIN INSTITUCION i2 ON i2.id=id_institucion;
        """
    )

    df = dataframe_from_sql_query(results_query_instituciones_matriz)

    for row in df.to_dict(orient="records"):
        nombre_institucion_padre = row['nombre_institucion_padre']
        nombre_institucion_hijo = row['nombre_institucion_hijo']

        if (nombre_institucion_padre and nombre_institucion_padre != 'None' and
                'sin determinar' not in str(nombre_institucion_padre).lower() and
                nombre_institucion_hijo and nombre_institucion_hijo != 'None' and
                'sin determinar' not in str(nombre_institucion_hijo).lower()):

            toda_la_info_institucion_padre = hash_sha256(f"{nombre_institucion_padre}")
            toda_la_info_institucion_hijo = hash_sha256(f"{nombre_institucion_hijo}")

            uri_id_institucion_padre = URIRef(f"{ontoexhibit}institution/{toda_la_info_institucion_padre}")
            uri_id_institucion_hijo = URIRef(f"{ontoexhibit}institution/{toda_la_info_institucion_hijo}")

            # LA NUEVA ES https://w3id.org/OntoExhibit#hasParentOrganization
            if uri_id_institucion_hijo and uri_id_institucion_padre:
                rdf_graph.add(
                    (uri_id_institucion_padre, URIRef(f"{ontoexhibit}isParentOrganizationOf"), uri_id_institucion_hijo)
                )
                rdf_graph.add(
                    (uri_id_institucion_hijo, URIRef(f"{ontoexhibit}hasParentOrganization"), uri_id_institucion_padre)
                )


def obtain_data_from_empresa():
    results_query = cursor.execute(
        "SELECT DISTINCT id, nombre, categoria, `dimensión`, `lugar de la sede` FROM EMPRESA;")

    df = dataframe_from_sql_query(results_query)

    for row in df.to_dict(orient="records"):
        expofinder_id = row['id']
        name = row['nombre']
        categoria = row['categoria']
        dimension = row['dimensión']
        lugar_sede = row['lugar de la sede']

        if name and name != 'None' and 'sin determinar' not in str(name).lower():
            # toda_la_info = f"{name} - {nombre_alternativo} - {tipo} - {titularidad} - {lugar_sede} - {
            # maximo_responsable} - {coordenadas}"

            toda_la_info = f"{name}"
            info_hashed = hash_sha256(toda_la_info)

            tipo = 'Company'
            uri_id = URIRef(f"{ontoexhibit}{tipo.lower()}/{info_hashed}")
            rdf_graph.add((uri_id, RDF.type, URIRef(f"{ontoexhibit}{tipo}")))
            rdf_graph.add((uri_id, RDFS.label, Literal(f"{name}", datatype=XSD['string'])))
            uri_pueblo_ciudad = None
            uri_estado_origen = None
            uri_pais_origen = None

            # TODO: preguntar a NURIA. No puede ser hasVenue porque eso es para SITE,
            #  y lo que nos viene de las bbdd es un territorial entity
            if (lugar_sede and lugar_sede != 'None'
                    and 'sin determinar' not in str(lugar_sede).lower()
                    and 'desconocido' not in lugar_sede.lower()):

                parte_pueblo_ciudad = None
                parte_provincia_estado = None
                parte_pais = None

                partes = lugar_sede.split(';')

                # Asignar las partes a las variables correspondientes si existen
                if len(partes) >= 1:
                    parte_pueblo_ciudad = partes[0].strip()
                if len(partes) >= 2:
                    parte_provincia_estado = partes[1].strip()
                if len(partes) >= 3:
                    parte_pais = partes[2].strip()

                lugar = None

                if parte_pueblo_ciudad and 'desconocido' != parte_pueblo_ciudad.lower():
                    uri_pueblo_ciudad = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_pueblo_ciudad)}")

                    rdf_graph.add((uri_pueblo_ciudad, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_pueblo_ciudad, RDFS.label,
                                   Literal(f"{parte_pueblo_ciudad}", datatype=XSD['string'])))

                    lugar = parte_pueblo_ciudad

                if parte_provincia_estado and 'desconocido' != parte_provincia_estado.lower():

                    uri_estado_origen = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_provincia_estado)}")

                    rdf_graph.add((uri_estado_origen, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_estado_origen, RDFS.label,
                                   Literal(f"{parte_provincia_estado}", datatype=XSD['string'])))

                    if not lugar:
                        lugar = parte_provincia_estado
                    else:
                        lugar = f"{lugar}; {parte_provincia_estado}"

                if parte_pais and 'desconocido' != parte_pais.lower():
                    uri_pais_origen = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_pais)}")

                    rdf_graph.add((uri_pais_origen, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_pais_origen, RDFS.label,
                                   Literal(f"{parte_pais}", datatype=XSD['string'])))
                    if not lugar:
                        lugar = parte_pais
                    else:
                        lugar = f"{lugar}; {parte_pais}"

                if lugar:
                    uri_lugar_sede = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(lugar)}")
                    rdf_graph.add((uri_lugar_sede, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_lugar_sede, RDFS.label, Literal(f"{lugar}",
                                                                       datatype=XSD['string'])))

                    uri_location = URIRef(f"{uri_id}/location")
                    rdf_graph.add((uri_location, RDF.type, URIRef(f"{ontoexhibit}Location")))

                    rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasLocation"), uri_location))
                    rdf_graph.add((uri_location, URIRef(f"{ontoexhibit}isLocationOf"), uri_id))

                    rdf_graph.add((uri_location, URIRef(f"{ontoexhibit}hasPlaceOfLocation"), uri_lugar_sede))
                    rdf_graph.add((uri_lugar_sede, URIRef(f"{ontoexhibit}isPlaceOfLocationOf"), uri_location))
                    """
                    if uri_pueblo_ciudad:
                        rdf_graph.add((uri_lugar_sede, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

                    if uri_estado_origen:
                        rdf_graph.add((uri_lugar_sede, URIRef(f"{ontoexhibit}hasState"), uri_estado_origen))

                    if uri_pais_origen:
                        rdf_graph.add((uri_lugar_sede, URIRef(f"{ontoexhibit}hasCountry"), uri_pais_origen))
                    """
                    if uri_pueblo_ciudad and uri_estado_origen:
                        # Asocio el lugar (ciudad) de origen con el estado
                        rdf_graph.add((uri_pueblo_ciudad, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_estado_origen))
                        rdf_graph.add((uri_estado_origen, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

                    if uri_estado_origen and uri_pais_origen:
                        # Asocio el lugar (ciudad) de origen con el estado
                        rdf_graph.add((uri_estado_origen, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_pais_origen))
                        rdf_graph.add((uri_pais_origen, URIRef(f"{ontoexhibit}hasState"), uri_estado_origen))

                    if not uri_estado_origen and uri_pueblo_ciudad and uri_pais_origen:
                        rdf_graph.add((uri_pueblo_ciudad, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_pais_origen))
                        rdf_graph.add((uri_pais_origen, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

            if expofinder_id and expofinder_id != 'None':
                rdf_graph.add(
                    (uri_id, URIRef(f"{ontoexhibit}expofinderId"), Literal(f"{expofinder_id}",
                                                                           datatype=XSD['string'])))

            if categoria and categoria != 'None':
                rdf_graph.add(
                    (uri_id, URIRef(f"{ontoexhibit}ISIC4Category"), Literal(f"{categoria}",
                                                                            datatype=XSD['string'])))

            if dimension and dimension != 'None':
                rdf_graph.add(
                    (uri_id, URIRef(f"{ontoexhibit}size"), Literal(f"{dimension}", datatype=XSD['string'])))


def obtain_data_from_obras():
    results_query = cursor.execute(
        """
        SELECT DISTINCT 
            oa.id, oa.nombre AS nombre_obra, `título alternativo`, `fecha de comienzo`, `fecha de terminación`, 
            `lugar de creación de la obra`, t.nombre AS tipo_obra, autor, p.nombre AS nombre_persona, 
            p.tipo AS tipo_persona
        FROM `OBRA DE ARTE` oa 
        LEFT JOIN PERSONA p on p.id=oa.autor
        LEFT JOIN TIPOLOGIA_OBRA_DE_ARTE te ON oa.id=te.id_obra
        LEFT JOIN TIPOLOGIA t ON t.id=te.id_tipologia;
        """
    )

    df = dataframe_from_sql_query(results_query)

    for row in df.to_dict(orient="records"):
        expofinder_id = row['id']
        nombre_obra = row['nombre_obra']
        nombre_alternativo = row['título alternativo']
        fecha_comienzo = row['fecha de comienzo']
        fecha_terminacion = row['fecha de terminación']
        lugar_creacion_obra = row['lugar de creación de la obra']
        nombre_persona = row['nombre_persona']
        tipo_obra = row['tipo_obra']
        tipo_persona = row['tipo_persona']

        # uri_produccion = None
        uri_lugar = None
        uri_pueblo_ciudad = None
        uri_estado_creacion = None
        uri_pais_creacion = None
        uri_fecha_comienzo = None
        uri_fecha_terminacion = None
        uri_time_range = None

        if nombre_obra and nombre_obra != 'None' and 'sin determinar' not in str(nombre_obra).lower():

            toda_la_info_obra = hash_sha256(f'{normalize_name(nombre_obra)} - work manifestation')
            position = None

            """
            for i, v in enumerate(classes):
                if v[0] == tipo_obra:
                    position = i
            if position:
                tipo = classes[position][1]
                # tipo = URIRef(ontoexhibit[mapping])
            else:
                tipo = 'WorkManifestation'
            """
            uri_id_obra = URIRef(f"{ontoexhibit}work_manifestation/{toda_la_info_obra}")
            rdf_graph.add((uri_id_obra, RDF.type, URIRef(f"{ontoexhibit}Work_Manifestation")))

            if tipo_obra and tipo_obra != 'None':
                rdf_graph.add(
                    (uri_id_obra, URIRef(f"{ontoexhibit}type"), Literal(f"{tipo_obra}", datatype=XSD['string'])))

            rdf_graph.add((uri_id_obra, RDFS.label, Literal(f"{nombre_obra}", datatype=XSD['string'])))
            rdf_graph.add((uri_id_obra, URIRef(f"{ontoexhibit}name"), Literal(f"{nombre_obra}",
                                                                              datatype=XSD['string'])))

            # title hasTittle
            uri_title = URIRef(f"{ontoexhibit}title/{hash_sha256(nombre_obra)}")
            rdf_graph.add((uri_title, RDF.type, URIRef(f"{ontoexhibit}Title")))
            rdf_graph.add((uri_title, RDFS.label, Literal(f"{nombre_obra}", datatype=XSD['string'])))

            rdf_graph.add((uri_id_obra, URIRef(f"{ontoexhibit}hasTitle"), uri_title))
            rdf_graph.add((uri_title, URIRef(f"{ontoexhibit}isTitleOf"), uri_id_obra))

            # fecha_terminacion, fecha_comienzo, lugar_creacion_obra
            fecha_comienzo = validar_fecha(fecha_comienzo)

            if fecha_comienzo:
                format_date = '%Y-%m-%d'

                if ((fecha_comienzo.month == 1 and fecha_comienzo.day == 1) or
                        (fecha_comienzo.month == 12 and fecha_comienzo.day == 31)):

                    fecha_comienzo = str(fecha_comienzo.year)
                    tipo_indiv = 'Approximate_Date'
                    uri_fecha_comienzo = URIRef(f"{ontoexhibit}{tipo_indiv.lower()}/{hash_sha256(fecha_comienzo)}")

                    rdf_graph.add((uri_fecha_comienzo, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                    rdf_graph.add(
                        (uri_fecha_comienzo, RDFS.label, Literal(f"{fecha_comienzo}", datatype=XSD['date'])))
                else:
                    fecha_comienzo = fecha_comienzo.strftime(format_date)
                    tipo_indiv = 'Exact_Date'
                    uri_fecha_comienzo = URIRef(f"{ontoexhibit}{tipo_indiv.lower()}/{hash_sha256(fecha_comienzo)}")

                    rdf_graph.add((uri_fecha_comienzo, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                    rdf_graph.add(
                        (uri_fecha_comienzo, RDFS.label, Literal(f"{fecha_comienzo}", datatype=XSD['date'])))

            fecha_terminacion = validar_fecha(fecha_terminacion)

            if fecha_terminacion:
                format_date = '%Y-%m-%d'

                if ((fecha_terminacion.month == 1 and fecha_terminacion.day == 1) or
                        (fecha_terminacion.month == 12 and fecha_terminacion.day == 31)):
                    # fecha_nacimiento = fecha_nacimiento.strftime(format_date)
                    fecha_terminacion = str(fecha_terminacion.year)
                    tipo_indiv = 'Approximate_Date'
                    uri_fecha_terminacion = URIRef(f"{ontoexhibit}{tipo_indiv.lower()}/"
                                                   f"{hash_sha256(fecha_terminacion)}")

                    rdf_graph.add((uri_fecha_terminacion, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                    rdf_graph.add(
                        (uri_fecha_terminacion, RDFS.label, Literal(f"{fecha_terminacion}", datatype=XSD['date'])))
                else:
                    fecha_terminacion = fecha_terminacion.strftime(format_date)
                    tipo_indiv = 'Exact_Date'
                    uri_fecha_terminacion = URIRef(
                        f"{ontoexhibit}{tipo_indiv.lower()}/{hash_sha256(fecha_terminacion)}")

                    rdf_graph.add((uri_fecha_terminacion, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                    rdf_graph.add(
                        (uri_fecha_terminacion, RDFS.label, Literal(f"{fecha_terminacion}", datatype=XSD['date'])))

            if lugar_creacion_obra and lugar_creacion_obra != 'None' and 'desconocido' != lugar_creacion_obra.lower():
                partes = lugar_creacion_obra.split(';')
                parte_pueblo_ciudad = None
                parte_provincia_estado = None
                uri_pueblo_ciudad = None
                parte_pais = None
                lugar = None

                # Asignar las partes a las variables correspondientes si existen
                if len(partes) >= 1:
                    parte_pueblo_ciudad = partes[0].strip()
                if len(partes) >= 2:
                    parte_provincia_estado = partes[1].strip()
                if len(partes) >= 3:
                    parte_pais = partes[2].strip()

                uri_estado_creacion = None
                uri_pais_creacion = None

                if parte_pueblo_ciudad and 'desconocido' != parte_pueblo_ciudad.lower():
                    uri_pueblo_ciudad = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_pueblo_ciudad)}")

                    rdf_graph.add((uri_pueblo_ciudad, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_pueblo_ciudad, RDFS.label, Literal(f"{parte_pueblo_ciudad}",
                                                                          datatype=XSD['string'])))

                    # rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}takesPlaceAt"), uri_pueblo_ciudad))
                    # rdf_graph.add((uri_pueblo_ciudad, URIRef(f"{ontoexhibit}isPlaceOf"), uri_id))
                    lugar = parte_pueblo_ciudad

                if parte_provincia_estado and 'desconocido' != parte_provincia_estado.lower():
                    uri_estado_creacion = URIRef(
                        f"{ontoexhibit}territorial_entity/{hash_sha256(parte_provincia_estado)}")

                    # Lugar (Estado - ADM)
                    rdf_graph.add((uri_estado_creacion, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_estado_creacion, RDFS.label,
                                   Literal(f"{parte_provincia_estado}", datatype=XSD['string'])))
                    if not lugar:
                        lugar = parte_provincia_estado
                    else:
                        lugar = f"{lugar}; {parte_provincia_estado}"

                if parte_pais and 'desconocido' != parte_pais.lower():
                    uri_pais_creacion = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_pais)}")
                    # Lugar (Estado - ADM)
                    rdf_graph.add((uri_pais_creacion, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_pais_creacion, RDFS.label, Literal(f"{parte_pais}",
                                                                          datatype=XSD['string'])))
                    if not lugar:
                        lugar = parte_pais
                    else:
                        lugar = f"{lugar}; {parte_pais}"

                if lugar:
                    # lugar_creacion_obra = re.sub(r'\s*;\s*', '; ', lugar_creacion_obra)
                    uri_lugar = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(lugar)}")
                    rdf_graph.add((uri_lugar, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_lugar, RDFS.label, Literal(f"{lugar}", datatype=XSD['string'])))

            if uri_fecha_comienzo or uri_fecha_terminacion or uri_lugar or nombre_persona:

                uri_produccion = URIRef(f"{uri_id_obra}/production")
                rdf_graph.add(
                    (uri_produccion, RDF.type, URIRef(f"https://cidoc-crm.org/cidoc-crm/7.1.1/E12_Production")))

                rdf_graph.add((uri_id_obra, URIRef(f"{ontoexhibit}hasProduction"), uri_produccion))
                rdf_graph.add((uri_produccion, URIRef(f"{ontoexhibit}isProductionOf"), uri_id_obra))

                if nombre_persona and nombre_persona != 'None' and 'sin determinar' not in str(nombre_persona).lower():
                    if tipo_persona != 'None' and tipo_persona == 'Individuo':
                        tipo_persona = 'person'
                    elif tipo_persona != 'None' and tipo_persona == 'Grupo de personas':
                        tipo_persona = 'group'
                    else:
                        tipo_persona = 'human actant'

                    toda_la_info_persona = f"{nombre_persona} - {tipo_persona}"
                    toda_la_info_persona = hash_sha256(toda_la_info_persona)

                    uri_id_persona = URIRef(f"{ontoexhibit}human_actant/{toda_la_info_persona}")

                    uri_id_autor = \
                        URIRef(f"{ontoexhibit}human_actant/{toda_la_info_persona}/author/{toda_la_info_obra}")

                    rdf_graph.add((uri_id_autor, RDF.type, URIRef(f"{ontoexhibit}Author")))

                    rdf_graph.add((uri_id_autor, RDFS.label,
                                   Literal(f"{nombre_persona} ({uri_id_persona}) is the producer of "
                                           f"{nombre_obra} ({uri_id_obra})", datatype=XSD['string'])))

                    rdf_graph.add((uri_id_persona, URIRef(f"{ontoexhibit}hasRole"), uri_id_autor))
                    rdf_graph.add((uri_id_autor, URIRef(f"{ontoexhibit}isRoleOf"), uri_id_persona))

                    rdf_graph.add((uri_produccion, URIRef(f"{ontoexhibit}hasProductionAuthor"), uri_id_autor))
                    rdf_graph.add((uri_id_autor, URIRef(f"{ontoexhibit}isProductionAuthorOf"), uri_produccion))

                if uri_lugar:
                    rdf_graph.add((uri_produccion, URIRef(f"{ontoexhibit}takesPlaceAt"), uri_lugar))
                    rdf_graph.add((uri_lugar, URIRef(f"{ontoexhibit}isPlaceOf"), uri_produccion))
                """
                if uri_pueblo_ciudad:
                    rdf_graph.add((uri_lugar, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

                if uri_estado_creacion:
                    rdf_graph.add((uri_lugar, URIRef(f"{ontoexhibit}hasState"), uri_estado_creacion))

                if uri_pais_creacion:
                    rdf_graph.add((uri_lugar, URIRef(f"{ontoexhibit}hasCountry"), uri_pais_creacion))
                """
                if uri_pueblo_ciudad and uri_estado_creacion:
                    # Asocio el lugar (ciudad) de origen con el estado
                    rdf_graph.add((uri_pueblo_ciudad, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_estado_creacion))
                    rdf_graph.add((uri_estado_creacion, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

                if uri_estado_creacion and uri_pais_creacion:
                    # Asocio el lugar (ciudad) de origen con el estado
                    rdf_graph.add((uri_estado_creacion, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_pais_creacion))
                    rdf_graph.add((uri_pais_creacion, URIRef(f"{ontoexhibit}hasState"), uri_estado_creacion))

                if not uri_estado_creacion and uri_pueblo_ciudad and uri_pais_creacion:
                    rdf_graph.add((uri_pueblo_ciudad, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_pais_creacion))
                    rdf_graph.add((uri_pais_creacion, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

                ####################################################################################################
                if uri_produccion:
                    if uri_fecha_comienzo or uri_fecha_terminacion:
                        uri_time_range = URIRef(f"{uri_produccion}/time_range")
                        rdf_graph.add((uri_time_range, RDF.type, URIRef(f"{ontoexhibit}Time_Range")))
                        rdf_graph.add((uri_produccion, URIRef(f"{ontoexhibit}hasTimeSpan"), uri_time_range))
                        rdf_graph.add((uri_time_range, URIRef(f"{ontoexhibit}isTimeSpanOf"), uri_produccion))

                    if uri_fecha_comienzo:
                        rdf_graph.add((uri_time_range, URIRef(f"{ontoexhibit}hasStartingDate"), uri_fecha_comienzo))
                        rdf_graph.add((uri_fecha_comienzo, URIRef(f"{ontoexhibit}isStartingDateOf"), uri_time_range))

                    if uri_fecha_terminacion:
                        rdf_graph.add((uri_time_range, URIRef(f"{ontoexhibit}hasEndingDate"), uri_fecha_terminacion))
                        rdf_graph.add(
                            (uri_fecha_terminacion, URIRef(f"{ontoexhibit}isEndingDateOf"), uri_time_range)
                        )

            if (nombre_alternativo and nombre_alternativo != 'None'
                    and 'sin determinar' not in str(nombre_alternativo).lower()):
                rdf_graph.add((uri_id_obra, URIRef(f"{ontoexhibit}apelation"),
                               Literal(f"{nombre_alternativo}", datatype=XSD['string'])))

            if expofinder_id and expofinder_id != 'None':
                rdf_graph.add((uri_id_obra, URIRef(f"{ontoexhibit}expofinderId"),
                               Literal(f"{expofinder_id}", datatype=XSD['string'])))

    results_query_obras_exhibited = cursor.execute(
        """
        SELECT DISTINCT 
            e.id AS id_exposicion, e.nombre AS nombre_exposicion, 
            o.id AS id_obra, o.nombre AS nombre_obra
        FROM 
        `EXPOSICION_TIENE_DISPOSITIVO_INSCRIPCION` etdi
        INNER JOIN `DISPOSITIVO_INSCRIPCION_PRESENTA_OBRA_DE_ARTE` dipo 
            ON etdi.id_dispositivo_inscripcion=dipo.id_dispositivo_inscripcion
        INNER JOIN EXPOSICION e ON etdi.id_exposicion=e.id
        INNER JOIN `OBRA DE ARTE` o ON o.id=dipo.id_obra;
        """
    )

    df = dataframe_from_sql_query(results_query_obras_exhibited)

    for row in df.to_dict(orient="records"):
        nombre_exposicion = row['nombre_exposicion']
        nombre_obra = row['nombre_obra']
        id_exposicion = row['id_exposicion']

        if (nombre_obra and nombre_obra != 'None'
                and 'sin determinar' not in str(nombre_obra).lower()
                and nombre_exposicion and nombre_exposicion != 'None'
                and 'sin determinar' not in str(nombre_exposicion).lower()):
            toda_la_info_obra = hash_sha256(f'{normalize_name(nombre_obra)} - work manifestation')
            uri_id_obra = URIRef(f"{ontoexhibit}work_manifestation/{toda_la_info_obra}")

            toda_la_info_exposicion = hash_sha256(f"exhibition - {normalize_name(nombre_exposicion)}")
            uri_id_exposicion = URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}")
            rdf_graph.add((uri_id_obra, URIRef(f"{ontoexhibit}isDisplayedAt"), uri_id_exposicion))
            rdf_graph.add((uri_id_exposicion, URIRef(f"{ontoexhibit}displays"), uri_id_obra))

    results_query_owners = cursor.execute(
        """
        SELECT  p.nombre AS nombre_persona, p.tipo AS tipo_persona, oa.nombre AS nombre_obra
        FROM PROPIETARIO_PERSONA_OBRA ppa
        INNER JOIN PERSONA p ON p.id=ppa.id_persona
        INNER JOIN `OBRA DE ARTE` oa ON oa.id=ppa.id_obra
        ;
        """
    )

    df = dataframe_from_sql_query(results_query_owners)

    for row in df.to_dict(orient="records"):
        nombre_persona = row['nombre_persona']
        nombre_obra = row['nombre_obra']
        tipo_persona = row['tipo_persona']

        if (nombre_obra and nombre_obra != 'None'
                and 'sin determinar' not in str(nombre_obra).lower()
                and nombre_persona and nombre_persona != 'None'
                and 'sin determinar' not in str(nombre_persona).lower()):

            if tipo_persona != 'None' and tipo_persona == 'Individuo':
                tipo_persona = 'person'
            elif tipo_persona != 'None' and tipo_persona == 'Grupo de personas':
                tipo_persona = 'group'
            else:
                tipo_persona = 'human actant'

            toda_la_info_obra = hash_sha256(f'{nombre_obra} - work manifestation')
            uri_id_obra = URIRef(f"{ontoexhibit}work_manifestation/{toda_la_info_obra}")

            toda_la_info_persona = f"{nombre_persona} - {tipo_persona}"
            toda_la_info_persona = hash_sha256(toda_la_info_persona)

            uri_id_persona = URIRef(f"{ontoexhibit}human_actant/{toda_la_info_persona}")

            uri_owner = URIRef(f"{uri_id_persona}/owner/{toda_la_info_obra}")
            rdf_graph.add((uri_owner, RDF.type, URIRef(f"{ontoexhibit}Owner")))
            rdf_graph.add((uri_owner, RDFS.label,
                           Literal(f"{nombre_persona} ({uri_id_persona}) was owner of "
                                   f"{nombre_obra} ({uri_id_obra})", datatype=XSD['string'])))

            rdf_graph.add((uri_id_persona, URIRef(f"{ontoexhibit}hasRole"), uri_owner))
            rdf_graph.add((uri_owner, URIRef(f"{ontoexhibit}isRoleOf"), uri_id_persona))

            rdf_graph.add((uri_owner, URIRef(f"{ontoexhibit}isOwnerOf"), uri_id_obra))
            rdf_graph.add((uri_id_obra, URIRef(f"{ontoexhibit}hasOwner"), uri_owner))

    results_query_institutions_owners = cursor.execute(
        """
        SELECT DISTINCT i.nombre AS nombre_institucion, oa.nombre AS nombre_obra
        FROM PROPIETARIO_INSTITUCION_OBRA pio
        INNER JOIN INSTITUCION i ON i.id=pio.id_institucion
        INNER JOIN `OBRA DE ARTE` oa ON oa.id=pio.id_obra
        ;
        """
    )

    df = dataframe_from_sql_query(results_query_institutions_owners)

    for row in df.to_dict(orient="records"):
        nombre_institucion = row['nombre_institucion']
        nombre_obra = row['nombre_obra']

        if (nombre_obra and nombre_obra != 'None'
                and 'sin determinar' not in str(nombre_obra).lower()
                and nombre_institucion and nombre_institucion != 'None'
                and 'sin determinar' not in str(nombre_institucion).lower()):
            toda_la_info_institucion = f"{nombre_institucion}"
            toda_la_info_institucion = hash_sha256(toda_la_info_institucion)

            toda_la_info_obra = hash_sha256(f'{nombre_obra} - work manifestation')

            uri_id_obra = URIRef(f"{ontoexhibit}work_manifestation/{toda_la_info_obra}")
            uri_id_institucion = URIRef(f"{ontoexhibit}institution/{toda_la_info_institucion}")

            uri_owner = URIRef(f"{uri_id_institucion}/owner/{toda_la_info_obra}")
            rdf_graph.add((uri_owner, RDF.type, URIRef(f"{ontoexhibit}Owner")))
            rdf_graph.add((uri_owner, RDFS.label,
                           Literal(f"{nombre_institucion} ({uri_id_institucion}) was owner of "
                                   f"{nombre_obra} ({uri_id_obra})", datatype=XSD['string'])))

            rdf_graph.add((uri_id_institucion, URIRef(f"{ontoexhibit}hasRole"), uri_owner))
            rdf_graph.add((uri_owner, URIRef(f"{ontoexhibit}isRoleOf"), uri_id_institucion))

            rdf_graph.add((uri_owner, URIRef(f"{ontoexhibit}isOwnerOf"), uri_id_obra))
            rdf_graph.add((uri_id_obra, URIRef(f"{ontoexhibit}hasOwner"), uri_owner))

    results_query_periodo_historico_obras = cursor.execute(
        """
        SELECT o.nombre AS nombre_obra, ph.periodo AS periodo_historico
        FROM PERIODO_HISTORICO_OBRA_DE_ARTE pho
        INNER JOIN `OBRA DE ARTE` o ON o.id=pho.id_obra
        INNER JOIN `PERIODO HISTORICO` ph on ph.id=pho.id_periodo;
        """
    )

    df = dataframe_from_sql_query(results_query_periodo_historico_obras)

    for row in df.to_dict(orient="records"):
        nombre_obra = row['nombre_obra']
        periodo_historico = row['periodo_historico']

        if (nombre_obra and nombre_obra != 'None'
                and 'sin determinar' not in str(nombre_obra).lower()
                and periodo_historico and periodo_historico != 'None'
                and 'sin determinar' not in str(periodo_historico).lower()):
            toda_la_info_obra = hash_sha256(f'{nombre_obra} - work manifestation')
            uri_id_obra = URIRef(f"{ontoexhibit}work_manifestation/{toda_la_info_obra}")

            uri_id_theme_subject_topic = URIRef(
                f"{ontoexhibit}theme/{hash_sha256(periodo_historico)}"
            )

            rdf_graph.add((uri_id_theme_subject_topic, RDF.type, URIRef(f"{ontoexhibit}Theme")))

            rdf_graph.add(
                (
                    uri_id_theme_subject_topic,
                    RDFS.label,
                    Literal(f"{periodo_historico}", datatype=XSD['string'])
                )
            )

            rdf_graph.add(
                (uri_id_theme_subject_topic, URIRef(f"{ontoexhibit}isThemeOf"), uri_id_obra)
            )
            rdf_graph.add((uri_id_obra, URIRef(f"{ontoexhibit}hasTheme"), uri_id_theme_subject_topic))

    results_query_mov_artistico_obras = cursor.execute(
        """
        SELECT o.nombre AS nombre_obra, ma.movimiento AS movimiento_artistico
        FROM MOVIMIENTO_ARTISTICO_OBRA_DE_ARTE mao 
		INNER JOIN `OBRA DE ARTE` o ON o.id = mao.id_obra
        INNER JOIN `MOVIMIENTO ARTISTICO` ma ON ma.id = mao.id_movimiento;
        """
    )

    df = dataframe_from_sql_query(results_query_mov_artistico_obras)

    for row in df.to_dict(orient="records"):
        nombre_obra = row['nombre_obra']
        movimiento_artistico = row['movimiento_artistico']

        if (nombre_obra and nombre_obra != 'None'
                and 'sin determinar' not in str(nombre_obra).lower()
                and movimiento_artistico and movimiento_artistico != 'None'
                and 'sin determinar' not in str(movimiento_artistico).lower()):
            toda_la_info_obra = hash_sha256(f'{nombre_obra} - work manifestation')
            uri_id_obra = URIRef(f"{ontoexhibit}work_manifestation/{toda_la_info_obra}")

            uri_id_theme_subject_topic = URIRef(
                f"{ontoexhibit}theme/{hash_sha256(movimiento_artistico)}"
            )

            rdf_graph.add((uri_id_theme_subject_topic, RDF.type, URIRef(f"{ontoexhibit}Theme")))

            rdf_graph.add(
                (
                    uri_id_theme_subject_topic,
                    RDFS.label,
                    Literal(f"{movimiento_artistico}", datatype=XSD['string'])
                )
            )

            rdf_graph.add(
                (uri_id_theme_subject_topic, URIRef(f"{ontoexhibit}isThemeOf"), uri_id_obra)
            )
            rdf_graph.add((uri_id_obra, URIRef(f"{ontoexhibit}hasTheme"), uri_id_theme_subject_topic))


def obtain_data_from_exposicion():
    results_query = cursor.execute(
        "SELECT DISTINCT"
        "   e.id, e.nombre, e.acceso, e.coordenadas, `fecha de apertura`, `fecha de cierre`, `lugar donde se celebra`, "
        "   e.sede, t.nombre AS tipo "
        "FROM EXPOSICION e "
        "LEFT JOIN TIPOLOGIA_EXPOSICION te ON e.id=te.id_exposicion "
        "LEFT JOIN TIPOLOGIA t ON t.id=te.id_tipologia;"
    )

    df = dataframe_from_sql_query(results_query)

    for row in df.to_dict(orient="records"):
        expofinder_id = row['id']
        name = row['nombre']
        acceso = row['acceso']
        coordenadas = row['coordenadas']
        fecha_apertura = row['fecha de apertura']
        fecha_cierre = row['fecha de cierre']
        lugar_celebracion = row['lugar donde se celebra']
        sede = row['sede']
        tipo = row['tipo']

        if name and name != 'None' and 'sin determinar' not in str(name).lower():
            # toda_la_info = f"{name} - {nombre_alternativo} - {tipo} - {titularidad} - {lugar_sede} - {
            # maximo_responsable} - {coordenadas}"

            toda_la_info = f"{expofinder_id} - {name}"
            info_hashed = hash_sha256(toda_la_info)

            position = None
            """
            for i, v in enumerate(classes):
                if v[0] == tipo:
                    position = i
            if position:
                tipo = classes[position][1]
                # tipo = URIRef(ontoexhibit[mapping])

            else:
                tipo = 'Exhibition'
            """
            uri_id = URIRef(f"{ontoexhibit}exhibition/{info_hashed}")
            rdf_graph.add((uri_id, RDF.type, URIRef(f"{ontoexhibit}Exhibition")))
            rdf_graph.add((uri_id, RDFS.label, Literal(f"{name}", datatype=XSD['string'])))

            if tipo and tipo != 'None':
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}type"), Literal(f"{tipo}", datatype=XSD['string'])))

            # title hasTittle
            uri_title = URIRef(f"{ontoexhibit}title/{hash_sha256(name)}")
            rdf_graph.add((uri_title, RDF.type, URIRef(f"{ontoexhibit}Title")))
            rdf_graph.add((uri_title, RDFS.label, Literal(f"{name}", datatype=XSD['string'])))

            rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasTitle"), uri_title))
            rdf_graph.add((uri_title, URIRef(f"{ontoexhibit}isTitleOf"), uri_id))

            if lugar_celebracion and lugar_celebracion != 'None':
                partes = lugar_celebracion.split(';')

                parte_pueblo_ciudad = None
                parte_provincia_estado = None
                uri_pueblo_ciudad = None
                parte_pais = None
                lugar = None

                # Asignar las partes a las variables correspondientes si existen
                if len(partes) >= 1:
                    parte_pueblo_ciudad = partes[0].strip()
                if len(partes) >= 2:
                    parte_provincia_estado = partes[1].strip()
                if len(partes) >= 3:
                    parte_pais = partes[2].strip()

                if lugar_celebracion and 'desconocido' != lugar_celebracion.lower():

                    uri_estado = None
                    uri_pais = None

                    if parte_pueblo_ciudad and 'desconocido' != parte_pueblo_ciudad.lower():
                        uri_pueblo_ciudad = URIRef(
                            f"{ontoexhibit}territorial_entity/{hash_sha256(parte_pueblo_ciudad)}")

                        rdf_graph.add((uri_pueblo_ciudad, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                        rdf_graph.add((uri_pueblo_ciudad, RDFS.label, Literal(f"{parte_pueblo_ciudad}",
                                                                              datatype=XSD['string'])))

                        # rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}takesPlaceAt"), uri_pueblo_ciudad))
                        # rdf_graph.add((uri_pueblo_ciudad, URIRef(f"{ontoexhibit}isPlaceOf"), uri_id))
                        lugar = parte_pueblo_ciudad

                    if parte_provincia_estado and 'desconocido' != parte_provincia_estado.lower():
                        uri_estado = URIRef(
                            f"{ontoexhibit}territorial_entity/{hash_sha256(parte_provincia_estado)}")

                        # Lugar (Estado - ADM)
                        rdf_graph.add((uri_estado, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                        rdf_graph.add((uri_estado, RDFS.label,
                                       Literal(f"{parte_provincia_estado}", datatype=XSD['string'])))
                        if not lugar:
                            lugar = parte_provincia_estado
                        else:
                            lugar = f"{lugar}; {parte_provincia_estado}"

                    if parte_pais and 'desconocido' != parte_pais.lower():
                        uri_pais = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_pais)}")
                        # Lugar (Estado - ADM)
                        rdf_graph.add((uri_pais, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                        rdf_graph.add((uri_pais, RDFS.label, Literal(f"{parte_pais}",
                                                                     datatype=XSD['string'])))
                        if not lugar:
                            lugar = parte_pais
                        else:
                            lugar = f"{lugar}; {parte_pais}"

                    if lugar:
                        # lugar_celebracion = re.sub(r'\s*;\s*', '; ', lugar_celebracion)

                        uri_lugar = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(lugar)}")
                        rdf_graph.add((uri_lugar, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                        rdf_graph.add((uri_lugar, RDFS.label, Literal(f"{lugar_celebracion}", datatype=XSD['string'])))

                        rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}takesPlaceAt"), uri_lugar))
                        rdf_graph.add((uri_lugar, URIRef(f"{ontoexhibit}isPlaceOf"), uri_id))

                        """
                        if uri_pueblo_ciudad:
                            rdf_graph.add((uri_lugar, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

                        if uri_estado:
                            rdf_graph.add((uri_lugar, URIRef(f"{ontoexhibit}hasState"), uri_estado))

                        if uri_pais:
                            rdf_graph.add((uri_lugar, URIRef(f"{ontoexhibit}hasCountry"), uri_pais))
                        """

                        if uri_pueblo_ciudad and uri_estado:
                            # Asocio el lugar (ciudad) de origen con el estado
                            rdf_graph.add((uri_pueblo_ciudad, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_estado))
                            rdf_graph.add((uri_estado, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

                        if uri_estado and uri_pais:
                            # Asocio el lugar (ciudad) de origen con el estado
                            rdf_graph.add((uri_estado, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_pais))
                            rdf_graph.add((uri_pais, URIRef(f"{ontoexhibit}hasState"), uri_estado))

                        if not uri_estado and uri_pueblo_ciudad and uri_pais:
                            rdf_graph.add((uri_pueblo_ciudad, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_pais))
                            rdf_graph.add((uri_pais, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

            fecha_apertura = validar_fecha(fecha_apertura)

            if fecha_apertura:
                format_date = '%Y-%m-%d'

                if (fecha_apertura.month == 1 and fecha_apertura.day == 1) \
                        or \
                        (fecha_apertura.month == 12 and fecha_apertura.day == 31):

                    fecha_apertura = str(fecha_apertura.year)
                    tipo_indiv = 'Approximate_Date'
                    uri_fecha = URIRef(f"{ontoexhibit}{tipo_indiv.lower()}/{hash_sha256(fecha_apertura)}")

                    rdf_graph.add((uri_fecha, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                    rdf_graph.add((uri_fecha, RDFS.label, Literal(f"{fecha_apertura}", datatype=XSD['date'])))
                else:
                    fecha_apertura = fecha_apertura.strftime(format_date)
                    tipo_indiv = 'Exact_Date'
                    uri_fecha = URIRef(f"{ontoexhibit}{tipo_indiv.lower()}/{hash_sha256(fecha_apertura)}")

                    rdf_graph.add((uri_fecha, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                    rdf_graph.add((uri_fecha, RDFS.label, Literal(f"{fecha_apertura}", datatype=XSD['date'])))

                tipo_indiv = 'Opening'
                uri_opening = URIRef(f"{uri_id}/{tipo_indiv.lower()}")
                rdf_graph.add((uri_opening, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                rdf_graph.add((uri_opening, URIRef(f"{ontoexhibit}hasTimeSpan"), uri_fecha))
                rdf_graph.add((uri_fecha, URIRef(f"{ontoexhibit}isTimeSpanOf"), uri_opening))
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasOpening"), uri_opening))
                rdf_graph.add((uri_opening, URIRef(f"{ontoexhibit}isOpeningOf"), uri_id))

            fecha_cierre = validar_fecha(fecha_cierre)

            if fecha_cierre:
                format_date = '%Y-%m-%d'

                if (fecha_cierre.month == 1 and fecha_cierre.day == 1) \
                        or \
                        (fecha_cierre.month == 12 and fecha_cierre.day == 31):
                    # fecha_nacimiento = fecha_nacimiento.strftime(format_date)
                    fecha_cierre = str(fecha_cierre.year)
                    tipo_indiv = 'Approximate_Date'
                    uri_fecha = URIRef(f"{ontoexhibit}{tipo_indiv.lower()}/{hash_sha256(fecha_cierre)}")

                    rdf_graph.add((uri_fecha, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                    rdf_graph.add((uri_fecha, RDFS.label, Literal(f"{fecha_cierre}", datatype=XSD['date'])))
                else:
                    fecha_cierre = fecha_cierre.strftime(format_date)
                    tipo_indiv = 'Exact_Date'
                    uri_fecha = URIRef(f"{ontoexhibit}{tipo_indiv.lower()}/{hash_sha256(fecha_cierre)}")

                    rdf_graph.add((uri_fecha, RDF.type, URIRef(f"{ontoexhibit}Exact_Date")))
                    rdf_graph.add((uri_fecha, RDFS.label, Literal(f"{fecha_cierre}", datatype=XSD['date'])))

                tipo_indiv = 'Closing'
                uri_closing = URIRef(f"{uri_id}/{tipo_indiv.lower()}")
                rdf_graph.add((uri_closing, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                rdf_graph.add((uri_closing, URIRef(f"{ontoexhibit}hasTimeSpan"), uri_fecha))
                rdf_graph.add((uri_fecha, URIRef(f"{ontoexhibit}isTimeSpanOf"), uri_closing))
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasClosing"), uri_closing))
                rdf_graph.add((uri_closing, URIRef(f"{ontoexhibit}isClosingOf"), uri_id))

            if (sede and sede != 'None'
                    and 'desconocido' != str(sede).lower() and 'sin determinar' not in str(sede).lower()):
                tipo_indiv = 'Site'
                uri_sede = URIRef(f"{ontoexhibit}{tipo_indiv.lower()}/{hash_sha256(sede)}")
                rdf_graph.add((uri_sede, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                rdf_graph.add((uri_sede, RDFS.label, Literal(f"{sede}", datatype=XSD['string'])))
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasVenue"), uri_sede))
                rdf_graph.add((uri_sede, URIRef(f"{ontoexhibit}isVenueOf"), uri_id))

            if coordenadas and coordenadas != 'None':
                coordenadas = str(coordenadas)

                latitud, longitud = procesar_coordenadas(coordenadas)
                rdf_graph.add((uri_id, URIRef(f"http://www.w3.org/2003/01/geo/wgs84_pos#lat"),
                               Literal(f"{latitud}", datatype=XSD['string'])))
                rdf_graph.add((uri_id, URIRef(f"http://www.w3.org/2003/01/geo/wgs84_pos#long"),
                               Literal(f"{longitud}", datatype=XSD['string'])))

            if expofinder_id and expofinder_id != 'None':
                rdf_graph.add(
                    (uri_id, URIRef(f"{ontoexhibit}expofinderId"), Literal(f"{expofinder_id}", datatype=XSD['string'])))

            if acceso and acceso != 'None' and acceso != 'No disponible':
                rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}access"), Literal(f"{acceso}", datatype=XSD['string'])))

    # Object properties relacionadas con personas
    results_query_exhibitors_person = cursor.execute(
        "SELECT DISTINCT persona_nombre, exposicion_nombre, id_exposicion "
        "FROM "
        "   ("
        "   SELECT p.nombre as persona_nombre, "
        "       e.nombre as exposicion_nombre, e.id as id_exposicion "
        "   FROM EXPOSICION_PRESENTA_PERSONA epp "
        "   INNER JOIN PERSONA p ON p.id = epp.id_persona "
        "   INNER JOIN EXPOSICION e ON e.id = epp.id_exposicion) AS tabla1 "
        "UNION "
        "SELECT DISTINCT persona_nombre, exposicion_nombre, id_exposicion "
        "FROM "
        "   ( "
        "   SELECT p.nombre as persona_nombre, "
        "       e.nombre as exposicion_nombre, e.id as id_exposicion "
        "   FROM EXPOSICION_PRESENTA_PERSONA epp "
        "   INNER JOIN PERSONA p ON p.id = epp.id_persona "
        "   INNER JOIN EXPOSICION e ON e.id = epp.id_exposicion) AS tabla1; "
    )

    df = dataframe_from_sql_query(results_query_exhibitors_person)
    for row in df.to_dict(orient="records"):
        name_persona = row['persona_nombre']
        name_exposicion = row['exposicion_nombre']
        id_exposicion = row['id_exposicion']

        toda_la_info_persona = hash_sha256(f"{name_persona} - person")
        toda_la_info_exposicion = hash_sha256(f"{id_exposicion} - {name_exposicion}")

        if (name_persona and name_persona != 'None'
                and 'sin determinar' not in str(name_persona).lower()
                and name_exposicion and name_exposicion != 'None'
                and 'sin determinar' not in str(name_exposicion).lower()):
            uri_id_persona = URIRef(f"{ontoexhibit}human_actant/{toda_la_info_persona}")

            uri_id_exposicion = URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}")

            uri_id_exhibitor = \
                URIRef(f"{ontoexhibit}human_actant/{toda_la_info_persona}/exhibitor/{toda_la_info_exposicion}")

            rdf_graph.add((uri_id_exhibitor, RDF.type, URIRef(f"{ontoexhibit}Exhibitor")))
            rdf_graph.add((uri_id_exhibitor, RDFS.label, Literal(f"{name_persona} ({uri_id_persona}) "
                                                                 f"is exhibiting actant in {name_exposicion} "
                                                                 f"({uri_id_exposicion})", datatype=XSD['string'])))
            rdf_graph.add((uri_id_persona, URIRef(f"{ontoexhibit}hasRole"), uri_id_exhibitor))
            rdf_graph.add((uri_id_exhibitor, URIRef(f"{ontoexhibit}isRoleOf"), uri_id_persona))

            uri_id_exhibition_making = \
                URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}/exhibition_making")

            rdf_graph.add((uri_id_exhibition_making, RDF.type, URIRef(f"{ontoexhibit}Exhibition_Making")))

            rdf_graph.add((uri_id_exposicion, URIRef(f"{ontoexhibit}hasExhibitionMaking"), uri_id_exhibition_making))
            rdf_graph.add((uri_id_exhibition_making, URIRef(f"{ontoexhibit}isExhibitionMakingOf"), uri_id_exposicion))

            rdf_graph.add(
                (uri_id_exhibition_making, URIRef(f"{ontoexhibit}hasExhibitingActant"), uri_id_exhibitor)
            )
            rdf_graph.add(
                (uri_id_exhibitor, URIRef(f"{ontoexhibit}isExhibitingActantIn"), uri_id_exhibition_making)
            )

    results_query_organize_institution = cursor.execute(
        """
        SELECT * 
        FROM (
            SELECT i.id AS id_institucion, i.nombre AS nombre_institucion, e.id AS id_exposicion, 
                e.nombre AS nombre_exposicion 
            FROM ORGANIZACION_EXPOSICION_INSTITUCION oei 
            INNER JOIN INSTITUCION i ON i.id=oei.id_institucion 
            INNER JOIN EXPOSICION e on e.id=oei.id_exposicion)
        UNION
        SELECT * 
        FROM (
            SELECT i.id AS id_institucion, i.nombre AS nombre_institucion, e.id AS id_exposicion, 
                e.nombre AS nombre_exposicion 
            FROM ORGANIZACION_EXPOSICION_INSTITUCION oei 
            INNER JOIN INSTITUCION i ON i.id=oei.id_institucion 
            INNER JOIN EXPOSICION e on e.id=oei.id_exposicion);
    """
    )
    df = dataframe_from_sql_query(results_query_organize_institution)
    for row in df.to_dict(orient="records"):
        nombre_institucion = row['nombre_institucion']
        nombre_exposicion = row['nombre_exposicion']
        id_exposicion = row['id_exposicion']

        if (nombre_exposicion and nombre_exposicion != 'None'
                and 'sin determinar' not in str(nombre_exposicion).lower()
                and nombre_institucion and nombre_institucion != 'None'
                and 'sin determinar' not in str(nombre_institucion).lower()):
            toda_la_info_institucion = hash_sha256(f"{nombre_institucion}")
            toda_la_info_exposicion = hash_sha256(f"{id_exposicion} - {nombre_exposicion}")

            uri_id_institucion = URIRef(f"{ontoexhibit}institution/{toda_la_info_institucion}")
            uri_id_exposicion = URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}")

            uri_id_organizer = \
                URIRef(f"{ontoexhibit}institution/{toda_la_info_institucion}/organizer/{toda_la_info_exposicion}")

            rdf_graph.add((uri_id_organizer, RDF.type, URIRef(f"{ontoexhibit}Organizer")))
            rdf_graph.add((uri_id_organizer, RDFS.label, Literal(f"{nombre_institucion} "
                                                                 f"({uri_id_institucion}) was organizer of "
                                                                 f"{nombre_exposicion} ({uri_id_exposicion})",
                                                                 datatype=XSD['string'])))

            rdf_graph.add((uri_id_institucion, URIRef(f"{ontoexhibit}hasRole"), uri_id_organizer))
            rdf_graph.add((uri_id_organizer, URIRef(f"{ontoexhibit}isRoleOf"), uri_id_institucion))

            uri_id_exhibition_making = \
                URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}/exhibition_making")

            rdf_graph.add((uri_id_exhibition_making, RDF.type, URIRef(f"{ontoexhibit}Exhibition_Making")))

            rdf_graph.add((uri_id_exposicion, URIRef(f"{ontoexhibit}hasExhibitionMaking"), uri_id_exhibition_making))
            rdf_graph.add((uri_id_exhibition_making, URIRef(f"{ontoexhibit}isExhibitionMakingOf"), uri_id_exposicion))

            rdf_graph.add(
                (uri_id_exhibition_making, URIRef(f"{ontoexhibit}hasOrganizer"), uri_id_organizer)
            )
            rdf_graph.add(
                (uri_id_organizer, URIRef(f"{ontoexhibit}isOrganizerOf"), uri_id_exhibition_making)
            )

    results_query_commissioners_personas = cursor.execute(
        """
        SELECT * FROM (
            SELECT p.nombre AS nombre_persona, p.tipo AS tipo, e.id AS id_exposicion, e.nombre AS nombre_exposicion
            FROM COMISARIO_EXPOSICION_PERSONA cpp
            INNER JOIN PERSONA p ON p.id=cpp.id_persona
            INNER JOIN EXPOSICION e ON e.id=cpp.id_exposicion)
        UNION
        SELECT * FROM(
            SELECT p.nombre as nombre_persona, p.tipo as tipo, e.id AS id_exposicion, e.nombre AS nombre_exposicion
            FROM COMISARIO_EXPOSICION_PERSONA cpp
            INNER JOIN PERSONA p ON p.id=cpp.id_persona
            INNER JOIN EXPOSICION e ON e.id=cpp.id_exposicion)
        ;
        """
    )
    df = dataframe_from_sql_query(results_query_commissioners_personas)

    for row in df.to_dict(orient="records"):
        nombre_persona = row['nombre_persona']
        tipo_persona = row['tipo']
        nombre_exposicion = row['nombre_exposicion']
        id_exposicion = row['id_exposicion']

        if nombre_persona and nombre_persona != 'None' and 'sin determinar' not in str(nombre_persona).lower():
            if tipo_persona != 'None' and tipo_persona == 'Individuo':
                tipo_persona = 'person'
            elif tipo_persona != 'None' and tipo_persona == 'Grupo de personas':
                tipo_persona = 'group'
            else:
                tipo_persona = 'human actant'

            toda_la_info_persona = f"{nombre_persona} - {tipo_persona}"
            toda_la_info_persona = hash_sha256(toda_la_info_persona)
            toda_la_info_exposicion = hash_sha256(f"{id_exposicion} - {nombre_exposicion}")
            uri_id_persona = URIRef(f"{ontoexhibit}human_actant/{toda_la_info_persona}")
            uri_id_exposicion = URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}")

            uri_id_curator = \
                URIRef(f"{ontoexhibit}human_actant/{toda_la_info_persona}/curator/{toda_la_info_exposicion}")

            rdf_graph.add((uri_id_curator, RDF.type, URIRef(f"{ontoexhibit}Curator")))

            rdf_graph.add((uri_id_curator, RDFS.label,
                           Literal(f"{nombre_persona} ({uri_id_persona}) was curator at "
                                   f"{nombre_exposicion} ({uri_id_exposicion})", datatype=XSD['string'])))

            rdf_graph.add((uri_id_persona, URIRef(f"{ontoexhibit}hasRole"), uri_id_curator))
            rdf_graph.add((uri_id_curator, URIRef(f"{ontoexhibit}isRoleOf"), uri_id_persona))

            uri_id_exhibition_making = \
                URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}/exhibition_making")

            rdf_graph.add((uri_id_exhibition_making, RDF.type, URIRef(f"{ontoexhibit}Exhibition_Making")))

            rdf_graph.add((uri_id_exposicion, URIRef(f"{ontoexhibit}hasExhibitionMaking"), uri_id_exhibition_making))
            rdf_graph.add((uri_id_exhibition_making, URIRef(f"{ontoexhibit}isExhibitionMakingOf"), uri_id_exposicion))

            rdf_graph.add((uri_id_exhibition_making, URIRef(f"{ontoexhibit}hasCurator"), uri_id_curator))
            rdf_graph.add((uri_id_curator, URIRef(f"{ontoexhibit}isCuratorOf"), uri_id_exhibition_making))

    results_query_museographer_empresas = cursor.execute(
        """
        SELECT * FROM (
            SELECT emp.nombre AS nombre_empresa, e.id AS id_exposicion, e.nombre AS nombre_exposicion
            FROM MUSEOGRAFIA_EMPRESA_EXPOSICION mee
            INNER JOIN EMPRESA emp ON emp.id=mee.id_empresa
            INNER JOIN EXPOSICION e ON e.id=mee.id_exposicion)
        UNION
        SELECT * FROM(
            SELECT emp.nombre as nombre_empresa, e.id AS id_exposicion, e.nombre AS nombre_exposicion
            FROM MUSEOGRAFIA_EMPRESA_EXPOSICION mee
            INNER JOIN EMPRESA emp ON emp.id=mee.id_empresa
            INNER JOIN EXPOSICION e ON e.id=mee.id_exposicion)
        ;
        """
    )
    df = dataframe_from_sql_query(results_query_museographer_empresas)

    for row in df.to_dict(orient="records"):
        nombre_empresa = row['nombre_empresa']
        nombre_exposicion = row['nombre_exposicion']
        id_exposicion = row['id_exposicion']

        if nombre_empresa and nombre_empresa != 'None' and 'sin determinar' not in str(nombre_empresa).lower():
            toda_la_info = f"{nombre_empresa}"
            info_hashed = hash_sha256(toda_la_info)

            tipo = 'Company'
            uri_id = URIRef(f"{ontoexhibit}{tipo.lower()}/{info_hashed}")

            toda_la_info_exposicion = hash_sha256(f"{id_exposicion} - {nombre_exposicion}")
            uri_id_exposicion = URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}")
            uri_id_museographer = \
                URIRef(f"{ontoexhibit}{tipo.lower()}/{info_hashed}/museographer/{toda_la_info_exposicion}")

            rdf_graph.add((uri_id_museographer, RDF.type, URIRef(f"{ontoexhibit}Museographer")))

            rdf_graph.add((uri_id_museographer, RDFS.label,
                           Literal(f"{nombre_empresa} ({uri_id}) was museographer at "
                                   f"{nombre_exposicion} ({uri_id_exposicion})", datatype=XSD['string'])))

            rdf_graph.add((uri_id, URIRef(f"{ontoexhibit}hasRole"), uri_id_museographer))
            rdf_graph.add((uri_id_museographer, URIRef(f"{ontoexhibit}isRoleOf"), uri_id))

            uri_id_exhibition_making = \
                URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}/exhibition_making")

            rdf_graph.add((uri_id_exhibition_making, RDF.type, URIRef(f"{ontoexhibit}Exhibition_Making")))

            rdf_graph.add((uri_id_exposicion, URIRef(f"{ontoexhibit}hasExhibitionMaking"), uri_id_exhibition_making))
            rdf_graph.add((uri_id_exhibition_making, URIRef(f"{ontoexhibit}isExhibitionMakingOf"), uri_id_exposicion))

            rdf_graph.add((uri_id_exhibition_making, URIRef(f"{ontoexhibit}hasMuseographer"), uri_id_museographer))
            rdf_graph.add((uri_id_museographer, URIRef(f"{ontoexhibit}isMuseographerOf"), uri_id_exhibition_making))

    results_query_periodo_historico_exposicion = cursor.execute(
        """
        SELECT e.id AS id_exposicion, e.nombre AS nombre_exposicion, ph.periodo AS periodo_historico
        FROM PERIODO_HISTORICO_EXPOSICION phe INNER JOIN EXPOSICION e ON e.id = phe.id_exposicion
        INNER JOIN `PERIODO HISTORICO` ph ON ph.id = phe.id_periodo;
        """
    )

    df = dataframe_from_sql_query(results_query_periodo_historico_exposicion)

    for row in df.to_dict(orient="records"):
        nombre_exposicion = row['nombre_exposicion']
        periodo_historico = row['periodo_historico']
        id_exposicion = row['id_exposicion']

        if (nombre_exposicion and nombre_exposicion != 'None'
                and 'sin determinar' not in str(nombre_exposicion).lower()
                and periodo_historico and periodo_historico != 'None'
                and 'sin determinar' not in str(periodo_historico).lower()):
            toda_la_info_exposicion = hash_sha256(f"{id_exposicion} - {nombre_exposicion}")
            uri_id_exposicion = URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}")

            uri_id_theme_subject_topic = URIRef(
                f"{ontoexhibit}theme/{hash_sha256(periodo_historico)}"
            )

            rdf_graph.add((uri_id_theme_subject_topic, RDF.type, URIRef(f"{ontoexhibit}Theme")))

            rdf_graph.add(
                (
                    uri_id_theme_subject_topic,
                    RDFS.label,
                    Literal(f"{periodo_historico}", datatype=XSD['string'])
                )
            )

            rdf_graph.add(
                (uri_id_theme_subject_topic, URIRef(f"{ontoexhibit}isThemeOf"), uri_id_exposicion)
            )
            rdf_graph.add((uri_id_exposicion, URIRef(f"{ontoexhibit}hasTheme"), uri_id_theme_subject_topic))

    results_query_mov_artistico_exposicion = cursor.execute(
        """
        SELECT e.id AS id_exposicion, e.nombre AS nombre_exposicion, ma.movimiento AS movimiento_artistico
        FROM MOVIMIENTO_ARTISTICO_EXPOSICION mae 
        INNER JOIN EXPOSICION e ON e.id = mae.id_exposicion
        INNER JOIN `MOVIMIENTO ARTISTICO` ma ON ma.id = mae.id_movimiento;
        """
    )

    df = dataframe_from_sql_query(results_query_mov_artistico_exposicion)

    for row in df.to_dict(orient="records"):
        nombre_exposicion = row['nombre_exposicion']
        movimiento_artistico = row['movimiento_artistico']
        id_exposicion = row['id_exposicion']

        if (nombre_exposicion and nombre_exposicion != 'None'
                and 'sin determinar' not in str(nombre_exposicion).lower()
                and movimiento_artistico and movimiento_artistico != 'None'
                and 'sin determinar' not in str(movimiento_artistico).lower()):
            toda_la_info_exposicion = hash_sha256(f"{id_exposicion} - {nombre_exposicion}")
            uri_id_exposicion = URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}")

            uri_id_theme_subject_topic = URIRef(
                f"{ontoexhibit}theme/{hash_sha256(movimiento_artistico)}"
            )

            rdf_graph.add((uri_id_theme_subject_topic, RDF.type, URIRef(f"{ontoexhibit}Theme")))

            rdf_graph.add(
                (
                    uri_id_theme_subject_topic,
                    RDFS.label,
                    Literal(f"{movimiento_artistico}", datatype=XSD['string'])
                )
            )

            rdf_graph.add(
                (uri_id_theme_subject_topic, URIRef(f"{ontoexhibit}isThemeOf"), uri_id_exposicion)
            )
            rdf_graph.add((uri_id_exposicion, URIRef(f"{ontoexhibit}hasTheme"), uri_id_theme_subject_topic))

    results_query_publishers = cursor.execute(
        """
        SELECT DISTINCT
            e.id AS id_exposicion, e.nombre AS nombre_exposicion,
            di.id AS id_catalogo, di.nombre AS nombre_catalogo, di.`fecha de publicación` AS fecha_publicacion, 
            di.`lugar de publicación` AS lugar_publicacion, di.`tipo de catálogo` AS tipo_catalogo,
            edi.id AS id_editorial, edi.nombre AS nombre_editorial
        FROM 
            EXPOSICION e
        INNER JOIN
            EXPOSICION_TIENE_DISPOSITIVO_INSCRIPCION etdi on etdi.id_exposicion=e.id
        INNER JOIN
            DISPOSITIVO_INSCRIPCION di on etdi.id_dispositivo_inscripcion = di.id 
        INNER JOIN 
            EDITORIAL_DISPOSITIVO_INSCRIPCION edidi on edidi.id_dispositivo_inscripcion=di.id
        INNER JOIN 
            EDITORIAL edi on edi.id=edidi.id_editorial;
        """
    )

    df = dataframe_from_sql_query(results_query_publishers)

    for row in df.to_dict(orient="records"):
        nombre_exposicion = row['nombre_exposicion']
        nombre_catalogo = row['nombre_catalogo']
        id_exposicion = row['id_exposicion']
        id_catalogo = row['id_catalogo']
        fecha_publicacion = row['fecha_publicacion']
        lugar_publicacion = row['lugar_publicacion']
        tipo_catalogo = row['tipo_catalogo']
        id_editorial = row['id_editorial']
        nombre_editorial = row['nombre_editorial']

        if (nombre_catalogo and nombre_catalogo != 'None'
                and 'sin determinar' not in str(nombre_catalogo).lower()
                and nombre_exposicion and nombre_exposicion != 'None'
                and 'sin determinar' not in str(nombre_exposicion).lower()):

            toda_la_info_catalogo = hash_sha256(f'{nombre_catalogo} - catalog')

            uri_id_catalogo = URIRef(f"{ontoexhibit}catalog/{toda_la_info_catalogo}")
            rdf_graph.add((uri_id_catalogo, RDF.type, URIRef(f"{ontoexhibit}Catalog")))
            rdf_graph.add((uri_id_catalogo, RDFS.label, Literal(f"{nombre_catalogo}",
                                                                datatype=XSD['string'])))

            uri_id_publication = URIRef(f"{ontoexhibit}catalog/{toda_la_info_catalogo}/publication")
            rdf_graph.add((uri_id_catalogo, RDF.type, URIRef(f"{ontoexhibit}Publication")))

            toda_la_info_exposicion = hash_sha256(f"{id_exposicion} - {nombre_exposicion}")
            uri_id_exposicion = URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}")

            rdf_graph.add((uri_id_catalogo, URIRef(f"{ontoexhibit}hasPublication"), uri_id_publication))
            rdf_graph.add((uri_id_publication, URIRef(f"{ontoexhibit}isPublicationOf"), uri_id_catalogo))

            uri_id_documentation_disp = URIRef(f"{ontoexhibit}exhibition/{toda_la_info_exposicion}"
                                               f"/documentation_dispositif")
            rdf_graph.add((uri_id_documentation_disp, RDF.type,
                           URIRef(f"{ontoexhibit}Institutional_Documentation_Dispositif")))

            rdf_graph.add((uri_id_exposicion, URIRef(f"{ontoexhibit}hasDocumentationDispositif"),
                           uri_id_documentation_disp))

            rdf_graph.add((uri_id_documentation_disp, URIRef(f"{ontoexhibit}isDocumentationDispositifOf"),
                           uri_id_exposicion))

            rdf_graph.add((uri_id_catalogo, URIRef(f"{ontoexhibit}servesAsDocumentationResourceOf"),
                           uri_id_documentation_disp))

            rdf_graph.add((uri_id_documentation_disp, URIRef(f"{ontoexhibit}hasDocumentationResource"),
                           uri_id_catalogo))

            if (nombre_editorial and nombre_editorial != 'None' and
                    'sin determinar' not in str(nombre_editorial).lower()):
                toda_la_info = f"{nombre_editorial}"
                info_hashed = hash_sha256(toda_la_info)

                uri_id_editorial = URIRef(f"{ontoexhibit}institution/{info_hashed}")

                uri_id_publisher = URIRef(f"{ontoexhibit}institution/{info_hashed}/publisher/{toda_la_info_catalogo}")

                rdf_graph.add((uri_id_publisher, RDF.type, URIRef(f"{ontoexhibit}Publisher")))

                rdf_graph.add((uri_id_publisher, RDFS.label,
                               Literal(f"{nombre_editorial} ({uri_id_editorial}) is the publisher of "
                                       f"{nombre_catalogo} ({uri_id_catalogo})", datatype=XSD['string'])))

                rdf_graph.add((uri_id_editorial, URIRef(f"{ontoexhibit}hasRole"), uri_id_publisher))
                rdf_graph.add((uri_id_publisher, URIRef(f"{ontoexhibit}isRoleOf"), uri_id_editorial))

                rdf_graph.add((uri_id_publication, URIRef(f"{ontoexhibit}hasPublisher"), uri_id_publisher))
                rdf_graph.add((uri_id_publisher, URIRef(f"{ontoexhibit}isPublisherOf"), uri_id_publication))

            if lugar_publicacion and lugar_publicacion != 'None':
                # lugar_origen = str(lugar_origen).replace('desconocido', '').replace('Desconocido', '')
                parte_pueblo_ciudad = None
                parte_provincia_estado = None
                parte_pais = None
                uri_pueblo_ciudad = None
                uri_estado = None
                uri_pais = None

                partes = lugar_publicacion.split(';')

                if len(partes) >= 1:
                    parte_pueblo_ciudad = partes[0].strip()
                if len(partes) >= 2:
                    parte_provincia_estado = partes[1].strip()
                if len(partes) >= 3:
                    parte_pais = partes[2].strip()

                if parte_pueblo_ciudad and 'desconocido' != parte_pueblo_ciudad.lower():
                    uri_pueblo_ciudad = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_pueblo_ciudad)}")

                    rdf_graph.add((uri_pueblo_ciudad, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_pueblo_ciudad, RDFS.label,
                                   Literal(f"{parte_pueblo_ciudad}", datatype=XSD['string'])))
                    lugar_publicacion = parte_pueblo_ciudad

                if parte_provincia_estado and 'desconocido' != parte_provincia_estado.lower():

                    uri_estado = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_provincia_estado)}")

                    rdf_graph.add((uri_estado, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_estado, RDFS.label,
                                   Literal(f"{parte_provincia_estado}", datatype=XSD['string'])))
                    if not lugar_publicacion:
                        lugar_publicacion = parte_provincia_estado
                    else:
                        lugar_publicacion = f"{lugar_publicacion}; {parte_provincia_estado}"

                if parte_pais and 'desconocido' != parte_pais.lower():
                    uri_pais = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(parte_pais)}")

                    rdf_graph.add((uri_pais, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_pais, RDFS.label,
                                   Literal(f"{parte_pais}", datatype=XSD['string'])))
                    if not lugar_publicacion:
                        lugar_publicacion = parte_pais
                    else:
                        lugar_publicacion = f"{lugar_publicacion}; {parte_pais}"

                if uri_pueblo_ciudad and uri_estado:
                    rdf_graph.add((uri_pueblo_ciudad, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_estado))
                    rdf_graph.add((uri_estado, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

                if uri_estado and uri_pais:
                    rdf_graph.add((uri_estado, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_pais))
                    rdf_graph.add((uri_pais, URIRef(f"{ontoexhibit}hasState"), uri_estado))

                if not uri_estado and uri_pueblo_ciudad and uri_pais:
                    rdf_graph.add((uri_pueblo_ciudad, URIRef(f"{ontoexhibit}hasParentTerritory"), uri_pais))
                    rdf_graph.add((uri_pais, URIRef(f"{ontoexhibit}hasCity"), uri_pueblo_ciudad))

                if lugar_publicacion:
                    uri_lugar = URIRef(f"{ontoexhibit}territorial_entity/{hash_sha256(lugar_publicacion)}")

                    rdf_graph.add((uri_lugar, RDF.type, URIRef(f"{ontoexhibit}Territorial_Entity")))
                    rdf_graph.add((uri_lugar, RDFS.label,
                                   Literal(f"{lugar_publicacion}", datatype=XSD['string'])))

                    rdf_graph.add((uri_id_publication, URIRef(f"{ontoexhibit}hasPlaceOfPublication"), uri_lugar))
                    rdf_graph.add((uri_lugar, URIRef(f"{ontoexhibit}isPlaceOf"), uri_id_publication))

            fecha_publicacion = validar_fecha(fecha_publicacion)

            if fecha_publicacion:
                format_date = '%Y-%m-%d'

                if ((fecha_publicacion.month == 1 and fecha_publicacion.day == 1) or
                        (fecha_publicacion.month == 12 and fecha_publicacion.day == 31)):

                    fecha_publicacion = str(fecha_publicacion.year)
                    tipo_indiv = 'Approximate_Date'
                    uri_fecha = URIRef(f"{ontoexhibit}{tipo_indiv.lower()}/{hash_sha256(fecha_publicacion)}")
                    rdf_graph.add((uri_fecha, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                    rdf_graph.add((uri_fecha, RDFS.label, Literal(f"{fecha_publicacion}", datatype=XSD['date'])))

                else:
                    fecha_publicacion = fecha_publicacion.strftime(format_date)
                    tipo_indiv = 'Exact_Date'
                    uri_fecha = URIRef(f"{ontoexhibit}{tipo_indiv.lower()}/{hash_sha256(fecha_publicacion)}")
                    rdf_graph.add((uri_fecha, RDF.type, URIRef(f"{ontoexhibit}{tipo_indiv}")))
                    rdf_graph.add((uri_fecha, RDFS.label, Literal(f"{fecha_publicacion}", datatype=XSD['date'])))

                rdf_graph.add((uri_id_publication, URIRef(f"{ontoexhibit}hasTimeSpan"), uri_fecha))
                rdf_graph.add((uri_fecha, URIRef(f"{ontoexhibit}isTimeSpanOf"), uri_id_publication))


def obtain_data_from_catalog():
    results_query_authors_persons = cursor.execute(
        """
        SELECT DISTINCT
            d.id AS id_catalogo, d.nombre AS nombre_catalogo, 
            p.id AS id_persona, p.nombre AS nombre_persona, p.tipo AS tipo_persona 
        FROM 
            AUTORIA_PERSONA_DISPOSITIVO_INSCRIPCION apdi
        INNER JOIN
            PERSONA p ON p.id=apdi.id_persona
        INNER JOIN
            DISPOSITIVO_INSCRIPCION d ON d.id=apdi.id_dispositivo_inscripcion;
        """
    )

    df = dataframe_from_sql_query(results_query_authors_persons)

    for row in df.to_dict(orient="records"):
        id_catalogo = row['id_catalogo']
        nombre_catalogo = row['nombre_catalogo']
        id_persona = row['id_persona']
        nombre_persona = row['nombre_persona']
        tipo_persona = row['tipo_persona']

        if (nombre_catalogo and nombre_catalogo != 'None' and 'sin determinar' not in str(nombre_catalogo).lower()
                and nombre_persona and nombre_persona != 'None'
                and 'sin determinar' not in str(nombre_persona).lower()):

            toda_la_info_catalogo = hash_sha256(f'{nombre_catalogo} - catalog')

            uri_id_catalogo = URIRef(f"{ontoexhibit}catalog/{toda_la_info_catalogo}")
            rdf_graph.add((uri_id_catalogo, RDF.type, URIRef(f"{ontoexhibit}Catalog")))
            rdf_graph.add((uri_id_catalogo, RDFS.label, Literal(f"{nombre_catalogo}",
                                                                datatype=XSD['string'])))

            if nombre_persona and nombre_persona != 'None' and 'sin determinar' not in str(nombre_persona).lower():
                if tipo_persona != 'None' and tipo_persona == 'Individuo':
                    tipo_persona = 'person'

                elif tipo_persona != 'None' and tipo_persona == 'Grupo de personas':
                    tipo_persona = 'group'
                else:
                    tipo_persona = 'human actant'

                toda_la_info = f"{nombre_persona} - {tipo_persona}"
                info_hashed = hash_sha256(toda_la_info)
                uri_id_persona = URIRef(f"{ontoexhibit}human_actant/{info_hashed}")

                uri_production = URIRef(f"{ontoexhibit}catalog/{toda_la_info_catalogo}/production")
                rdf_graph.add(
                    (uri_production, RDF.type, URIRef(f"https://cidoc-crm.org/cidoc-crm/7.1.1/E12_Production")))

                rdf_graph.add((uri_id_catalogo, URIRef(f"{ontoexhibit}hasProduction"), uri_production))
                rdf_graph.add((uri_production, URIRef(f"{ontoexhibit}isProductionOf"), uri_id_catalogo))

                uri_producer = URIRef(f"{ontoexhibit}human_actant/{info_hashed}/producer/{toda_la_info_catalogo}")

                rdf_graph.add((uri_producer, RDF.type, URIRef(f"{ontoexhibit}Producer")))

                rdf_graph.add((uri_producer, RDFS.label,
                               Literal(f"{nombre_persona} ({uri_id_persona}) is the producer of "
                                       f"{nombre_catalogo} ({uri_id_catalogo})", datatype=XSD['string'])))

                rdf_graph.add((uri_id_persona, URIRef(f"{ontoexhibit}hasRole"), uri_producer))
                rdf_graph.add((uri_producer, URIRef(f"{ontoexhibit}isRoleOf"), uri_id_persona))

                rdf_graph.add((uri_producer, URIRef(f"{ontoexhibit}isProducerOf"), uri_production))
                rdf_graph.add((uri_production, URIRef(f"{ontoexhibit}hasProducer"), uri_producer))

    results_query_authors_institutions = cursor.execute(
        """
        SELECT d.id AS id_catalogo, d.nombre AS nombre_catalogo, i.id AS id_institucion, i.nombre AS nombre_institucion
        FROM 
            AUTORIA_INSTITUCION_DISPOSITIVO_INSCRIPCION aidi
        INNER JOIN
            INSTITUCION i ON i.id=aidi.id_institucion
        INNER JOIN
            DISPOSITIVO_INSCRIPCION d ON d.id=aidi.id_dispositivo_inscripcion;
        """
    )

    df = dataframe_from_sql_query(results_query_authors_institutions)

    for row in df.to_dict(orient="records"):
        id_catalogo = row['id_catalogo']
        nombre_catalogo = row['nombre_catalogo']
        id_institucion = row['id_institucion']
        nombre_institucion = row['nombre_institucion']

        if (nombre_catalogo and nombre_catalogo != 'None' and 'sin determinar' not in str(nombre_catalogo).lower()
                and nombre_institucion and nombre_institucion != 'None'
                and 'sin determinar' not in str(nombre_institucion).lower()):

            toda_la_info_catalogo = hash_sha256(f'{nombre_catalogo} - catalog')

            uri_id_catalogo = URIRef(f"{ontoexhibit}catalog/{toda_la_info_catalogo}")
            rdf_graph.add((uri_id_catalogo, RDF.type, URIRef(f"{ontoexhibit}Catalog")))
            rdf_graph.add((uri_id_catalogo, RDFS.label, Literal(f"{nombre_catalogo}",
                                                                datatype=XSD['string'])))

            if (nombre_institucion and nombre_institucion != 'None'
                    and 'sin determinar' not in str(nombre_institucion).lower()):
                toda_la_info_institucion = f"{nombre_institucion}"
                info_hashed = hash_sha256(toda_la_info_institucion)

                uri_id_institution = URIRef(f"{ontoexhibit}institution/{info_hashed}")

                uri_production = URIRef(f"{ontoexhibit}catalog/{toda_la_info_catalogo}/production")
                rdf_graph.add(
                    (uri_production, RDF.type, URIRef(f"https://cidoc-crm.org/cidoc-crm/7.1.1/E12_Production")))

                rdf_graph.add((uri_id_catalogo, URIRef(f"{ontoexhibit}hasProduction"), uri_production))
                rdf_graph.add((uri_production, URIRef(f"{ontoexhibit}isProductionOf"), uri_id_catalogo))

                uri_producer = URIRef(f"{ontoexhibit}institution/{info_hashed}/producer/{toda_la_info_catalogo}")

                rdf_graph.add((uri_producer, RDF.type, URIRef(f"{ontoexhibit}Producer")))

                rdf_graph.add((uri_producer, RDFS.label,
                               Literal(f"{nombre_institucion} ({uri_id_institution}) is the producer of "
                                       f"{nombre_catalogo} ({uri_id_catalogo})", datatype=XSD['string'])))

                rdf_graph.add((uri_id_institution, URIRef(f"{ontoexhibit}hasRole"), uri_producer))
                rdf_graph.add((uri_producer, URIRef(f"{ontoexhibit}isRoleOf"), uri_id_institution))

                rdf_graph.add((uri_producer, URIRef(f"{ontoexhibit}isProducerOf"), uri_production))
                rdf_graph.add((uri_production, URIRef(f"{ontoexhibit}hasProducer"), uri_producer))


obtain_data_from_personas()
print('acabadas las personas')
obtain_data_from_institucion()
print('acabadas las instituciones')
obtain_data_from_empresa()
print('acabadas las empresas')
obtain_data_from_catalog()
print('acabados los catálogos')
obtain_data_from_exposicion()
print('acabadas las exposiciones')
obtain_data_from_obras()
print('acabadas las obras')

########################################################################################################################
# CLASSES
########################################################################################################################

# fun_classes()
# print('Classes obtained')

########################################################################################################################
# OBJECT PROPERTIES
########################################################################################################################

# fun_object_properties()
# print('Object properties obtained ')

########################################################################################################################
# DATA PROPERTIES
########################################################################################################################

# fun_data_properties()
# print('Data properties obtained ')

# print(f'Total dates = {total_dates}')

percentage_fail = None
percentage_success = None

try:
    percentage_fail = round(count_fail * 100 / total_dates, 1)
    percentage_success = round(count_success * 100 / total_dates, 1)
except ZeroDivisionError:
    print('Error dividing by 0')

print(f'Incorrect dates: {count_fail}, ->  {percentage_fail} % of total dates')
print(f'Correct dates: {count_success}, -> {percentage_success} % of total dates')

########################################################################################################################
# SAVE OUTPUT FILE
########################################################################################################################

output_file_name = 'result.nt'
with open(output_file_name, 'w+', encoding='utf-8') as f:
    f.write(rdf_graph.serialize(format='nt'))

print(f'Results saved in file "{output_file_name}"\n')
