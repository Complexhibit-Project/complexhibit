import sqlite3
import hashlib
from sqlite3 import OperationalError


def hash_sha256(data: str) -> str:
    """Generate deterministic hash for ID generation."""
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def execute_scripts_from_sql_file(filename):
    cursor = conexion.cursor()
    # Open and read the file as a single buffer
    fd = open(filename, 'r', encoding="utf-8")
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    sqlCommands = sqlFile.split(';')

    # Execute every command from the input file
    for command in sqlCommands:
        # This will skip and report errors
        # For example, if the tables do not yet exist, this will skip over
        # the DROP TABLE commands
        try:
            cursor.execute(command)
        except OperationalError as msg:
            print("Command skipped: ", msg)


def convertir(field: str):
    if '"' in field:
        field = field.replace('"', "'")
    elif '`' in field:
        field = field.replace('`', "'")
    elif '‘' in field:
        field = field.replace("‘", "'")

    return field


def transformar_tuplas_string(tuplas: list) -> str:
    """Convert list of tuples to SQL VALUES string, properly quoting all fields."""
    string = ''
    cont2 = 0

    for tupla in tuplas:
        cont2 += 1
        string += '('
        cont1 = 0
        for field in tupla:
            cont1 += 1
            field_str = convertir(str(field)) if field is not None else ''
            
            if cont1 < len(tupla):
                # Quote all fields including the first (now a hash string)
                string += f'"{field_str}", '
            else:
                # Last field, no trailing comma
                string += f'"{field_str}"'
        
        if cont2 < len(tuplas):
            string += '), '
        else:
            string += ')'
    return string


def insert_ediciones():
    cursor = conexion.cursor()
    cursor.execute(f'SELECT * from temp_edicion order by nombre, `fecha de apertura`;')

    filas = cursor.fetchall()

    if len(filas) > 0:
        i = 0
        nombre_padre = None
        # id_padre = None
        ids_para_borrar_exposicion = []
        tuplas_filas_insertar = []

        while i < len(filas):
            fila = filas[i]
            id = fila[0]
            nombre = fila[1]

            if i == 0:
                id_padre = filas[0][0]
                nombre_padre = filas[0][1]
                # debo insertar en una lista para insertar todas despues en la tabla de exposicion
            else:
                if nombre != nombre_padre:
                    nombre_padre = nombre
                    id_padre = id
                    # creo que va a la misma tabla, exposicion
                else:
                    # tuplas_filas_insertar.append()
                    # inserto en una lista que va a ir a la tabla edicion
                    # borro esa fila de la tabla exposicion
                    ids_para_borrar_exposicion.append(id)
                    if id_padre:
                        fila = list(fila)
                        fila.append(id_padre)
                        fila = tuple(fila)
                        # print(fila)
                    tuplas_filas_insertar.append(fila)

            i += 1

        string_borrar = ''
        cont = 0
        for id in ids_para_borrar_exposicion:
            cont += 1
            if cont < len(ids_para_borrar_exposicion):
                string_borrar += str(id) + ", "
            else:
                string_borrar += str(id)

        string_insertar = transformar_tuplas_string(tuplas_filas_insertar)
        # print(string_insertar)
        # print(string_borrar)
        # print(f'INSERT INTO EDICION VALUES {string_insertar};')
        # print(f'DELETE FROM EXPOSICION WHERE id IN ( {string_borrar} );')
        # print(tuple(tuplas_filas_insertar))

        try:
            cursor.execute(f'DELETE FROM EXPOSICION WHERE id IN ({string_borrar});')
            conexion.commit()
        except sqlite3.Error as error:
            raise Exception("Error al intentar borrar de la tabla EXPOSICION: " + str(error))
        
        try:  # INSERT EDICIONES
            cursor.execute(f'INSERT INTO EDICION VALUES {string_insertar};')
            conexion.commit()
        except sqlite3.Error as error:
            raise Exception("Error al intentar insertar de la tabla EDICION: " + str(error))

    cursor.close()


def insert_propietarios_personas_obras():
    # INSERT PROPIETARIOS PERSONAS OBRAS
    cursor = conexion.cursor()
    cursor.execute(f"SELECT DISTINCT rid AS id_persona, id AS id_obra "
                   f"FROM rel "
                   f"WHERE rkey LIKE 'propietario/a de la obra' AND ridtype LIKE 'actor' ORDER BY id;")

    filas = cursor.fetchall()

    if len(filas) > 0:
        tuplas_filas_insertar = []
        for fila in filas:
            # print(fila)
            id_persona = fila[0]
            id_obra = fila[1]
            id_generated = hash_sha256(f'{id_persona}-{id_obra}')
            new_tuple = [str(id_generated), id_persona, id_obra]
            tuplas_filas_insertar.append(tuple(new_tuple))

        string_propietarios_personas_obras = transformar_tuplas_string(tuplas_filas_insertar)

        try:
            cursor.execute(f'INSERT INTO PROPIETARIO_PERSONA_OBRA (id, id_persona, id_obra) '
                           f'VALUES {string_propietarios_personas_obras}')
            conexion.commit()
        except sqlite3.Error as error:
            raise Exception("Error al intentar insertar de la tabla PROPIETARIO_PERSONA_OBRA: " + str(error))

    cursor.close()


def insert_propietarios_instituciones_obras():
    # INSERT PROPIETARIOS INSTITUCIONES OBRAS
    cursor = conexion.cursor()
    cursor.execute(f"SELECT DISTINCT rid AS id_institucion, id AS id_obra "
                   f"FROM rel WHERE rkey LIKE 'propietario/a de la obra' AND ridtype LIKE 'institución' "
                   f"ORDER BY id;")

    filas = cursor.fetchall()

    if len(filas) > 0:
        string_propietarios_instituciones_obras = ''
        tuplas_filas_insertar = []
        for fila in filas:
            # print(fila)
            id_institucion = fila[0]
            id_obra = fila[1]

            id_generated = hash_sha256(f'{id_institucion}-{id_obra}')
            new_tuple = [str(id_generated), id_institucion, id_obra]
            tuplas_filas_insertar.append(tuple(new_tuple))

        string_propietarios_instituciones_obras = transformar_tuplas_string(tuplas_filas_insertar)
        try:
            cursor.execute(f'INSERT INTO PROPIETARIO_INSTITUCION_OBRA (id, id_institucion, id_obra) '
                           f'VALUES {string_propietarios_instituciones_obras}')
            conexion.commit()
        except sqlite3.Error as error:
            raise Exception("Error al intentar insertar de la tabla PROPIETARIO_INSTITUCION_OBRA: " + str(error))

    cursor.close()


def insert_personas_maximos_responsables():
    cursor = conexion.cursor()
    try:
        cursor.execute(
            """
            SELECT DISTINCT
                CASE 
                    WHEN `máximo responsable` LIKE '%(%' 
                        THEN rtrim(SUBSTR(ltrim(`máximo responsable`), 0, instr(`máximo responsable`, '('))) 
                    ELSE 
                        rtrim(ltrim(`máximo responsable`))
                END AS `máximo responsable`
            FROM institucion i LEFT JOIN persona p ON p.nombre=`máximo responsable`
            WHERE `máximo responsable` IS NOT NULL AND p.nombre IS NULL 
                AND `máximo responsable` NOT LIKE '+34%' 
                AND `máximo responsable` NOT LIKE '%http%' 
                AND `máximo responsable` NOT LIKE '%@%' 
                AND `máximo responsable` NOT LIKE '(%'
            ORDER BY `máximo responsable`;
            """
        )

        nombres_personas = cursor.fetchall()
        if len(nombres_personas) > 0:
            try:
                cursor.execute(
                    """
                    SELECT id FROM PERSONA ORDER BY id DESC LIMIT 1;
                    """
                )

                ultimo_id_personas = cursor.fetchone()[0]
                filas_insertar_personas = []
                for nombre in nombres_personas:
                    ultimo_id_personas += 1
                    nombre = '"' + str(nombre[0]) + '"'
                    new_tuple = [nombre, ultimo_id_personas]
                    filas_insertar_personas.append(tuple(new_tuple))

                string_insertar = transformar_tuplas_string(filas_insertar_personas)

                try:
                    cursor.execute(f'INSERT INTO PERSONA (nombre, id) '
                                   f'VALUES {string_insertar}')
                    conexion.commit()
                except sqlite3.Error as error:
                    raise Exception("Error al intentar insertar de la tabla PERSONA: " + str(error))

            except sqlite3.Error as error:
                raise Exception("Error al intentar obtener el último id de la tabla PERSONA: " + str(error))

    except sqlite3.Error as error:
                raise Exception("Error al intentar obtener datos de la tabla PERSONA: " + str(error))
    cursor.close()


def update_personas_maximos_responsables():
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT p.id as id_persona, i.id as id_institucion
            FROM 
                institucion i 
            INNER JOIN 
                persona p 
                    ON (rtrim(substr(ltrim(`máximo responsable`),0,instr(`máximo responsable`,'('))) = p.nombre 
                        OR rtrim(ltrim(`máximo responsable`)) = p.nombre)
                        AND `máximo responsable` IS NOT NULL;
            """
        )

        personas_a_actualizar = cursor.fetchall()
        # multiple records to be updated in tuple format
        # records_to_update = [(3000, 3), (2750, 4)]
        try:
            sql_update_query = """UPDATE institucion SET `máximo responsable` = ? WHERE id = ?"""
            cursor.executemany(sql_update_query, personas_a_actualizar)
            conexion.commit()
        except sqlite3.Error as error:
            raise Exception("Error al actualizar los maximos responsables con los id's de personas: " + str(error))

    except sqlite3.Error as error:
        raise Exception("Error al intentar obtener datos de la tabla PERSONA: " + str(error))


def poner_a_null_maximos_responsables_erroneos():
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT 
                id 
            FROM 
                INSTITUCION 
            WHERE 
                `máximo responsable` LIKE '%@%' 
                OR `máximo responsable` LIKE '%http%' 
                OR `máximo responsable` LIKE '%(%' OR `máximo responsable` LIKE '%+34%';
            """
        )
        maximos_responsables_erroneos = cursor.fetchall()
        try:
            sql_update_query = """UPDATE institucion SET `máximo responsable` = NULL WHERE id = ?"""
            cursor.executemany(sql_update_query, maximos_responsables_erroneos)
            conexion.commit()
        except sqlite3.Error as error:
            raise Exception("Error al actualizar los maximos responsables erroneos de la tabla INSTITUCION: " + str(error))
    except sqlite3.Error as error:
        raise Exception("Error al intentar borrar de la tabla INSTITUCION: " + str(error))


try:
    conexion = sqlite3.connect(timeout=60, database='pathwise.db')
    import os
    sql_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'sql', 'normalize_schema.sql')
    execute_scripts_from_sql_file(sql_path)
    conexion.commit()

    # insert_ediciones()
    insert_propietarios_personas_obras()
    insert_propietarios_instituciones_obras()
    insert_personas_maximos_responsables()
    update_personas_maximos_responsables()
    poner_a_null_maximos_responsables_erroneos()

    '''
        try:
            cursor.executescript(
                """
                INSERT INTO EDICION
                SELECT 
                    id, nombre, acceso, coordenadas, `fecha de apertura`, `fecha de cierre`, `lugar donde se celebra`, 
                    sede, id AS id_exposicion 
                FROM 
                    EXPOSICION;

                CREATE TEMPORARY TABLE t1_backup(id INTEGER PRIMARY KEY, nombre);
                INSERT INTO t1_backup SELECT id, nombre FROM EXPOSICION;
                DROP TABLE EXPOSICION;
                CREATE TABLE EXPOSICION(id INTEGER PRIMARY KEY, nombre);
                INSERT INTO EXPOSICION SELECT id, nombre FROM t1_backup;
                DROP TABLE t1_backup;
                """
            )
            conexion.commit()
        except sqlite3.Error as error:
            raise Exception("Error al intentar modificar de la tabla EXPOSICION: " + str(error))
        '''

    conexion.close()

except sqlite3.Error as error:
    raise Exception("An error occurred: " + str(error))
