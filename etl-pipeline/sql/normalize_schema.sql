	UPDATE tax SET value = 'Exposición colectiva' WHERE value LIKE 'col';
	UPDATE tax SET value = 'Catálogo' WHERE value LIKE 'catálogo';
	UPDATE REL SET RID=133313 WHERE ID=97929 AND rkey like 'catálogo';

	/* ************************************************************************************************** */
    /* EXPOSICION */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS EXPOSICION;
    CREATE TABLE EXPOSICION (
        id INTEGER PRIMARY KEY,
        nombre,
        acceso,
        coordenadas,
        `fecha de apertura`,
        `fecha de cierre`,
        `lugar donde se celebra`,
        `dirección postal`,
        sede
    );

    INSERT INTO EXPOSICION (
        id,
        nombre,
        acceso,
        coordenadas,
        `fecha de apertura`,
        `fecha de cierre`,
        `lugar donde se celebra`,
        `dirección postal`,
        sede
    )
    SELECT
            DISTINCT pos.id AS id, pos.value AS nombre,
            MAX(CASE WHEN met.rkey LIKE 'acceso' THEN met.value END) acceso,
            MAX(CASE WHEN met.rkey LIKE 'coordenadas' THEN met.value END) coordenadas,
            MAX(CASE WHEN met.rkey LIKE 'fecha de apertura' THEN met.value END) `fecha de apertura`,
            MAX(CASE WHEN met.rkey LIKE 'fecha de cierre' THEN met.value END) `fecha de cierre`,
            MAX(CASE WHEN met.rkey LIKE 'lugar donde se celebra' THEN met.value END) `lugar donde se celebra`,
            MAX(CASE WHEN met.rkey LIKE 'dirección postal de exposición' THEN met.value END) `dirección postal`,
            MAX(CASE WHEN met.rkey LIKE 'sede' THEN met.value END) sede
    FROM
            pos
    LEFT JOIN
            met ON met.id=pos.id
    WHERE
            pos.value NOT LIKE '' AND pos.rkey LIKE 'exposición' AND met.rkey NOT LIKE 'geoetiqueta'
    GROUP BY pos.id, pos.value
    ORDER BY pos.id;

    /* ************************************************************************************************** */
    /* INSTITUCION */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS INSTITUCION;
    CREATE TABLE INSTITUCION (
        id INTEGER PRIMARY KEY,
        nombre,
        titularidad,
        `URI HTML`,
        `URI RSS`,
        coordenadas,
        `correo electrónico`,
        fax,
        `lugar de la sede`,
        `dirección postal`,
        `máximo responsable`,
        `página web`,
        `teléfono`,
        `nombre alternativo`
    );

    INSERT INTO INSTITUCION (
        id,
        nombre,
        titularidad,
        `nombre alternativo`,
        `máximo responsable`,
        `correo electrónico`,
        `lugar de la sede`,
        `dirección postal`,
        `teléfono`,
        fax,
        `página web`,
        `URI HTML`,
        `URI RSS`,
        coordenadas
    )
    SELECT
            DISTINCT pos.id AS id, pos.value AS nombre,
            tax.value AS titularidad,
            MAX(CASE WHEN met.rkey LIKE 'nombre alternativo' THEN met.value END) `nombre alternativo`,
            MAX(CASE WHEN met.rkey LIKE 'máximo responsable' THEN met.value END) `máximo responsable`,
            MAX(CASE WHEN met.rkey LIKE 'correo electrónico' THEN met.value END) `correo electrónico`,
            MAX(CASE WHEN met.rkey LIKE 'lugar de la sede' THEN met.value END) `lugar de la sede`,
            MAX(CASE WHEN met.rkey LIKE 'dirección postal de institución' THEN met.value END) `dirección postal`,
            MAX(CASE WHEN met.rkey LIKE 'teléfono' THEN met.value END) `teléfono`,
            MAX(CASE WHEN met.rkey LIKE 'fax' THEN met.value END) fax,
            MAX(CASE WHEN met.rkey LIKE 'página web' THEN met.value END) `página web`,
            MAX(CASE WHEN met.rkey LIKE 'URI HTML' THEN met.value END) `URI HTML`,
            MAX(CASE WHEN met.rkey LIKE 'URI RSS' THEN met.value END) `URI RSS`,
            MAX(CASE WHEN met.rkey LIKE 'coordenadas' THEN met.value END) coordenadas
    FROM
            pos
    LEFT JOIN
            met ON met.id=pos.id
    LEFT JOIN
            tax ON pos.id=tax.id AND tax.rkey LIKE 'titularidad de institución'
    WHERE
            pos.value NOT LIKE '' AND pos.rkey LIKE 'institución'
    GROUP BY pos.id, pos.value
    ORDER BY pos.id;


    /* ************************************************************************************************** */
    /* PERSONA */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS PERSONA;
    CREATE TABLE PERSONA (
        id INTEGER PRIMARY KEY,
        nombre,
		tipo,
		`género`,
		`lugar de origen`,
		`fecha de nacimiento`,
        `fecha de defunción`,
        `dirección postal`,
        coordenadas
    );

    INSERT INTO PERSONA (
        id,
        nombre,
		tipo,
		`género`,
		`lugar de origen`,
		`fecha de nacimiento`,
        `fecha de defunción`,
        `dirección postal`,
        coordenadas
    )
    SELECT
            DISTINCT pos.id AS id, pos.value AS nombre,
			MAX(CASE WHEN met.rkey LIKE 'tipo de actor' THEN met.value END) tipo,
			MAX(CASE WHEN met.rkey LIKE 'género' THEN met.value END) `género`,
			MAX(CASE WHEN met.rkey LIKE 'nacionalidad de origen' THEN met.value END) `lugar de origen`,
            MAX(CASE WHEN met.rkey LIKE 'fecha de nacimiento' THEN met.value END) `fecha de nacimiento`,
            MAX(CASE WHEN met.rkey LIKE 'fecha de defunción' THEN met.value END) `fecha de defunción`,
            MAX(CASE WHEN met.rkey LIKE 'dirección postal de actor' THEN met.value END) `dirección postal`,
			MAX(CASE WHEN met.rkey LIKE 'coordenadas' THEN met.value END) coordenadas

    FROM
            pos
    LEFT JOIN
            met ON met.id=pos.id
    WHERE
            pos.value NOT LIKE '' AND pos.rkey LIKE 'actor'
    GROUP BY pos.id, pos.value
    ORDER BY pos.id;

	UPDATE PERSONA SET tipo = 'Grupo de personas' WHERE tipo LIKE 'Group of persons';

    /* ************************************************************************************************** */
    /* DISPOSITIVO_INSCRIPCION */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS `DISPOSITIVO_INSCRIPCION`;
    CREATE TABLE `DISPOSITIVO_INSCRIPCION` (
        id INTEGER PRIMARY KEY,
        nombre,
        `fecha de publicación`,
        `lugar de publicación`,
        `tipo de catálogo`
    );

    INSERT INTO `DISPOSITIVO_INSCRIPCION` (
        id,
        nombre,
        `fecha de publicación`,
        `lugar de publicación`,
        `tipo de catálogo`
    )
    SELECT
            DISTINCT pos.id AS id, pos.value AS nombre,
            MAX(CASE WHEN met.rkey LIKE 'fecha de publicación' THEN met.value END) `fecha de publicación`,
            MAX(CASE WHEN met.rkey LIKE 'lugar de publicación' THEN met.value END) `lugar de publicación`,
            MAX(CASE WHEN met.rkey LIKE 'tipo de catálogo' THEN met.value END) `tipo de catálogo`

    FROM
            pos
    LEFT JOIN
            met ON met.id=pos.id
    WHERE
            pos.value NOT LIKE '' AND pos.rkey LIKE 'catálogo'
    GROUP BY pos.id, pos.value
    ORDER BY pos.id;


    /* ************************************************************************************************** */
    /* OBRA DE ARTE */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS `OBRA DE ARTE`;
    CREATE TABLE `OBRA DE ARTE` (
        id INTEGER PRIMARY KEY,
        nombre,
        `fecha de comienzo`,
        `fecha de terminación`,
        `lugar de creación de la obra`,
        `título alternativo`,
		autor
    );

    INSERT INTO `OBRA DE ARTE` (
        id,
        nombre,
        `fecha de comienzo`,
        `fecha de terminación`,
        `lugar de creación de la obra`,
        `título alternativo`,
		autor
    )
    SELECT
            DISTINCT pos.id AS id, pos.value AS nombre,
            MAX(CASE WHEN met.rkey LIKE 'fecha de comienzo' THEN met.value END) `fecha de comienzo`,
            MAX(CASE WHEN met.rkey LIKE 'fecha de terminación' THEN met.value END) `fecha de terminación`,
            MAX(CASE WHEN met.rkey LIKE 'lugar de creación de la obra' THEN met.value END) `lugar de creación de la obra`,
            MAX(CASE WHEN met.rkey LIKE 'título alternativo' THEN met.value END) `título alternativo`,
			NULL AS autor
    FROM
            pos
    LEFT JOIN
            met ON met.id=pos.id
    WHERE
            pos.value NOT LIKE '' AND pos.rkey LIKE 'obra de arte'
    GROUP BY pos.id, pos.value
    ORDER BY pos.id;

	UPDATE `OBRA DE ARTE` SET autor = (SELECT rel.rid AS autor FROM rel WHERE rel.id=`OBRA DE ARTE`.id AND rel.rkey LIKE 'autoría de la obra');


    /* ************************************************************************************************** */
    /* EMPRESAS */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS EMPRESA;
    CREATE TABLE EMPRESA(id INTEGER PRIMARY KEY, nombre, categoria, `dimensión`, `lugar de la sede`);
    INSERT INTO EMPRESA(id, nombre, categoria, `dimensión`, `lugar de la sede`)
    SELECT
            DISTINCT pos.id AS id, pos.value AS nombre,
            tax.value AS categoria,
            MAX(CASE WHEN met.rkey LIKE 'dimensión' THEN met.value END) `dimensión`,
            MAX(CASE WHEN met.rkey LIKE 'lugar de la sede' THEN met.value END) `lugar de la sede`
    FROM
            pos
    LEFT JOIN
            met ON met.id=pos.id
    LEFT JOIN
            tax ON pos.id=tax.id
    WHERE
            pos.value NOT LIKE '' AND pos.rkey LIKE 'empresa'
    GROUP BY pos.id, pos.value
    ORDER BY pos.id;


    /* ************************************************************************************************** */
    /* TIPOLOGIA */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS TIPOLOGIA;
    CREATE TABLE TIPOLOGIA(
        id INTEGER PRIMARY KEY,
        nombre
    );

    INSERT INTO TIPOLOGIA (nombre)
    SELECT DISTINCT UPPER(SUBSTR(value,1,1)) || SUBSTR(value,2,LENGTH(value)) AS nombre FROM tax WHERE rkey LIKE '%tipo%' order by nombre;


    /* ************************************************************************************************** */
    /* M2M TIPOLOGIA_EXPOSICION */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS TIPOLOGIA_EXPOSICION;
    CREATE TABLE TIPOLOGIA_EXPOSICION(
        id INTEGER PRIMARY KEY,
        id_exposicion INTEGER,
        id_tipologia INTEGER,
        FOREIGN KEY(id_tipologia) REFERENCES TIPOLOGIA(id),
        FOREIGN KEY(id_exposicion) REFERENCES EXPOSICION(id)

    );

    INSERT INTO TIPOLOGIA_EXPOSICION (id_exposicion, id_tipologia)
    SELECT tax.id AS id_exposicion, tipologia.id AS tipologia_id FROM tax INNER JOIN tipologia ON tax.value=tipologia.nombre AND rkey LIKE 'tipo de exposición' ORDER BY id_exposicion;


    /* ************************************************************************************************** */
    /* M2M TIPOLOGIA_INSTITUCION */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS TIPOLOGIA_INSTITUCION;
    CREATE TABLE TIPOLOGIA_INSTITUCION(
        id INTEGER PRIMARY KEY,
        id_institucion INTEGER,
        id_tipologia INTEGER,
        FOREIGN KEY(id_tipologia) REFERENCES TIPOLOGIA(id),
        FOREIGN KEY(id_institucion) REFERENCES INSTITUCION(id)

    );

    INSERT INTO TIPOLOGIA_INSTITUCION (id_institucion, id_tipologia)
    SELECT tax.id AS id_institucion, tipologia.id AS tipologia_id FROM tax INNER JOIN tipologia ON tax.value=tipologia.nombre AND rkey LIKE 'tipología de institución' ORDER BY id_institucion;


    /* ************************************************************************************************** */
    /* M2M TIPOLOGIA_OBRA_DE_ARTE */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS TIPOLOGIA_OBRA_DE_ARTE;
    CREATE TABLE TIPOLOGIA_OBRA_DE_ARTE(
        id INTEGER PRIMARY KEY,
        id_obra INTEGER,
        id_tipologia INTEGER,
        FOREIGN KEY(id_tipologia) REFERENCES TIPOLOGIA(id),
        FOREIGN KEY(id_obra) REFERENCES `OBRA DE ARTE`(id)

    );

    INSERT INTO TIPOLOGIA_OBRA_DE_ARTE (id_obra, id_tipologia)
    SELECT tax.id AS id_obra, tipologia.id AS tipologia_id FROM tax INNER JOIN tipologia ON tax.value=tipologia.nombre AND rkey LIKE 'tipo de obra de arte' ORDER BY id_obra;


    /* ************************************************************************************************** */
    /* M2M TIPOLOGIA_DISPOSITIVO_INSCRIPCION */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS TIPOLOGIA_DISPOSITIVO_INSCRIPCION;
    CREATE TABLE TIPOLOGIA_DISPOSITIVO_INSCRIPCION(
        id INTEGER PRIMARY KEY,
        id_dispositivo_inscripcion INTEGER,
        id_tipologia INTEGER,
        FOREIGN KEY(id_tipologia) REFERENCES TIPOLOGIA(id),
        FOREIGN KEY(id_dispositivo_inscripcion) REFERENCES `DISPOSITIVO_INSCRIPCION`(id)

    );

    INSERT INTO TIPOLOGIA_DISPOSITIVO_INSCRIPCION (id_dispositivo_inscripcion, id_tipologia)
    SELECT tax.id AS id_dispositivo_inscripcion, tipologia.id AS tipologia_id FROM tax INNER JOIN tipologia ON tax.value=tipologia.nombre AND rkey LIKE 'tipología de catálogo' ORDER BY id_dispositivo_inscripcion;


    /* ************************************************************************************************** */
    /* PERIODO HISTORICO*/
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS `PERIODO HISTORICO`;
    CREATE TABLE `PERIODO HISTORICO` (
        id INTEGER PRIMARY KEY,
        periodo
    );

    INSERT INTO `PERIODO HISTORICO` (periodo)
    SELECT DISTINCT UPPER(SUBSTR(value,1,1)) || SUBSTR(value,2,LENGTH(value)) AS periodo FROM tax WHERE rkey LIKE 'periodo histórico' ORDER BY periodo;


    /* ************************************************************************************************** */
    /* M2M PERIODO_HISTORICO_EXPOSICION*/
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS PERIODO_HISTORICO_EXPOSICION;
    CREATE TABLE PERIODO_HISTORICO_EXPOSICION (
        id INTEGER PRIMARY KEY,
        id_exposicion INTEGER,
        id_periodo INTEGER,
        FOREIGN KEY(id_periodo) REFERENCES `PERIODO HISTORICO`(id),
        FOREIGN KEY(id_exposicion) REFERENCES EXPOSICION (id)
    );

    INSERT INTO PERIODO_HISTORICO_EXPOSICION (id_exposicion, id_periodo)
        SELECT tax.id AS id_exposicion, ph.id AS id_periodo
        FROM tax
        INNER JOIN pos ON pos.ID=tax.ID AND pos.rkey LIKE 'exposición'
        INNER JOIN `PERIODO HISTORICO` AS ph ON tax.value=ph.periodo AND tax.rkey LIKE 'periodo histórico'
        ORDER BY id_exposicion;


    /* ************************************************************************************************** */
    /* M2M PERIODO_HISTORICO_OBRA_DE_ARTE*/
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS PERIODO_HISTORICO_OBRA_DE_ARTE;
    CREATE TABLE PERIODO_HISTORICO_OBRA_DE_ARTE (
        id INTEGER PRIMARY KEY,
        id_obra INTEGER,
        id_periodo INTEGER,
        FOREIGN KEY(id_periodo) REFERENCES `PERIODO HISTORICO` (id),
        FOREIGN KEY(id_obra) REFERENCES `OBRA DE ARTE` (id)
    );

    INSERT INTO PERIODO_HISTORICO_OBRA_DE_ARTE (id_obra, id_periodo)
        SELECT tax.id AS id_obra, ph.id AS id_periodo
        FROM tax
        INNER JOIN pos ON pos.ID=tax.ID AND pos.rkey LIKE 'obra de arte'
        INNER JOIN `PERIODO HISTORICO` AS ph ON tax.value=ph.periodo AND tax.rkey LIKE 'periodo histórico'
        ORDER BY id_obra;


    /* ************************************************************************************************** */
    /* MOVIMIENTO ARTISTICO */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS `MOVIMIENTO ARTISTICO`;
    CREATE TABLE `MOVIMIENTO ARTISTICO` (
        id INTEGER PRIMARY KEY,
        movimiento
    );

    INSERT INTO `MOVIMIENTO ARTISTICO` (movimiento)
    SELECT DISTINCT UPPER(SUBSTR(value,1,1)) || SUBSTR(value,2,LENGTH(value)) AS movimiento FROM tax WHERE rkey LIKE 'movimiento artístico' ORDER BY movimiento;


    /* ************************************************************************************************** */
    /* M2M MOVIMIENTO_ARTISTICO_EXPOSICION*/
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS MOVIMIENTO_ARTISTICO_EXPOSICION;
    CREATE TABLE MOVIMIENTO_ARTISTICO_EXPOSICION (
        id INTEGER PRIMARY KEY,
        id_exposicion INTEGER,
        id_movimiento INTEGER,
        FOREIGN KEY(id_movimiento) REFERENCES `MOVIMIENTO ARTISTICO`(id),
        FOREIGN KEY(id_exposicion) REFERENCES EXPOSICION (id)
    );

    INSERT INTO MOVIMIENTO_ARTISTICO_EXPOSICION (id_exposicion, id_movimiento)
    SELECT tax.id AS id_exposicion, ma.id AS id_movimiento FROM tax INNER JOIN `MOVIMIENTO ARTISTICO` AS ma ON tax.value=ma.movimiento AND rkey LIKE 'movimiento artístico' ORDER BY id_exposicion;


    /* ************************************************************************************************** */
    /* M2M MOVIMIENTO_ARTISTICO_OBRA_DE_ARTE*/
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS MOVIMIENTO_ARTISTICO_OBRA_DE_ARTE;
    CREATE TABLE MOVIMIENTO_ARTISTICO_OBRA_DE_ARTE (
        id INTEGER PRIMARY KEY,
        id_obra INTEGER,
        id_movimiento INTEGER,
        FOREIGN KEY(id_movimiento) REFERENCES `MOVIMIENTO ARTISTICO` (id),
        FOREIGN KEY(id_obra) REFERENCES `OBRA DE ARTE` (id)
    );

    INSERT INTO MOVIMIENTO_ARTISTICO_OBRA_DE_ARTE (id_obra, id_movimiento)
    SELECT tax.id AS id_obra, ma.id AS id_movimiento FROM tax INNER JOIN `MOVIMIENTO ARTISTICO` AS ma ON tax.value=ma.movimiento AND rkey LIKE 'movimiento artístico' ORDER BY id_obra;


    /* ************************************************************************************************** */
    /* M2M MOVIMIENTO_ARTISTICO_DISPOSITIVO_INSCRIPCION */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS MOVIMIENTO_ARTISTICO_DISPOSITIVO_INSCRIPCION;
    CREATE TABLE MOVIMIENTO_ARTISTICO_DISPOSITIVO_INSCRIPCION (
        id INTEGER PRIMARY KEY,
        id_dispositivo_inscripcion INTEGER,
        id_movimiento INTEGER,
        FOREIGN KEY(id_movimiento) REFERENCES `MOVIMIENTO ARTISTICO` (id),
        FOREIGN KEY(id_dispositivo_inscripcion) REFERENCES `DISPOSITIVO_INSCRIPCION` (id)
    );

    INSERT INTO MOVIMIENTO_ARTISTICO_DISPOSITIVO_INSCRIPCION (id_dispositivo_inscripcion, id_movimiento)
    SELECT tax.id AS id_dispositivo_inscripcion, ma.id AS id_movimiento FROM tax INNER JOIN `MOVIMIENTO ARTISTICO` AS ma ON tax.value=ma.movimiento AND rkey LIKE 'movimiento artístico' ORDER BY id_dispositivo_inscripcion;


    /* ************************************************************************************************** */
    /* EDITORIAL */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS EDITORIAL;
    CREATE TABLE EDITORIAL (
        id INTEGER PRIMARY KEY,
        nombre
    );

    INSERT INTO EDITORIAL (id, nombre)
	SELECT DISTINCT pos.id AS id, pos.value AS nombre FROM tax INNER JOIN pos ON tax.value=pos.value AND tax.rkey LIKE 'editorial de catálogo' order by pos.id;


    /* ************************************************************************************************** */
    /* M2M EDITORIAL_DISPOSITIVO_INSCRIPCION */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS EDITORIAL_DISPOSITIVO_INSCRIPCION;
    CREATE TABLE EDITORIAL_DISPOSITIVO_INSCRIPCION (
        id INTEGER PRIMARY KEY,
        id_dispositivo_inscripcion INTEGER,
        id_editorial INTEGER,
        FOREIGN KEY(id_editorial) REFERENCES EDITORIAL (id),
        FOREIGN KEY(id_dispositivo_inscripcion) REFERENCES `DISPOSITIVO_INSCRIPCION` (id)
    );

    INSERT INTO EDITORIAL_DISPOSITIVO_INSCRIPCION (id_dispositivo_inscripcion, id_editorial)
    SELECT tax.id AS id_dispositivo_inscripcion, ed.id AS id_editorial FROM tax INNER JOIN EDITORIAL AS ed ON tax.value=ed.nombre AND rkey LIKE 'editorial de catálogo' ORDER BY id_dispositivo_inscripcion;


    /* ************************************************************************************************** */
    /* ACTIVIDAD */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS ACTIVIDAD;
    CREATE TABLE ACTIVIDAD (
        id INTEGER PRIMARY KEY,
        nombre
    );

    INSERT INTO ACTIVIDAD (nombre)
    SELECT DISTINCT UPPER(SUBSTR(value,1,1)) || SUBSTR(value,2,LENGTH(value)) AS nombre FROM tax WHERE rkey LIKE 'actividad de actor' ORDER BY nombre;


    /* ************************************************************************************************** */
    /* M2M ACTIVIDAD_PERSONA */
    /* ************************************************************************************************** */

    DROP TABLE IF EXISTS ACTIVIDAD_PERSONA;
    CREATE TABLE ACTIVIDAD_PERSONA (
        id INTEGER PRIMARY KEY,
        id_persona INTEGER,
        id_actividad INTEGER,
        FOREIGN KEY(id_persona) REFERENCES PERSONA (id),
        FOREIGN KEY(id_actividad) REFERENCES ACTIVIDAD (id)
    );

    INSERT INTO ACTIVIDAD_PERSONA (id_persona, id_actividad)
    SELECT tax.id AS id_persona, a.id AS id_actividad FROM tax INNER JOIN ACTIVIDAD AS a ON tax.value=a.nombre AND rkey LIKE 'actividad de actor' ORDER BY id_persona;


	/* **************************************** */
	/* PROPIETARIO_PERSONA_OBRA */
	/* **************************************** */

    DROP TABLE IF EXISTS PROPIETARIO_PERSONA_OBRA;
    CREATE TABLE PROPIETARIO_PERSONA_OBRA (
        id TEXT PRIMARY KEY,
        id_persona INTEGER,
        id_obra INTEGER,
		`fecha inicio`,
		`fecha de fin`,
        FOREIGN KEY(id_persona) REFERENCES PERSONA (id),
        FOREIGN KEY(id_obra) REFERENCES `OBRA DE ARTE` (id)
    );




	/* **************************************** */
	/* PROPIETARIO_INSTITUCION_OBRA */
	/* **************************************** */

    DROP TABLE IF EXISTS PROPIETARIO_INSTITUCION_OBRA;
    CREATE TABLE PROPIETARIO_INSTITUCION_OBRA (
        id TEXT PRIMARY KEY,
        id_institucion INTEGER,
        id_obra INTEGER,
		`fecha inicio`,
		`fecha de fin`,
        FOREIGN KEY(id_institucion) REFERENCES INSTITUCION (id),
        FOREIGN KEY(id_obra) REFERENCES `OBRA DE ARTE` (id)
    );




	/* **************************************** */
	/* AUTORIA_PERSONA_DISPOSITIVO_INSCRIPCION */
	/* **************************************** */

    DROP TABLE IF EXISTS AUTORIA_PERSONA_DISPOSITIVO_INSCRIPCION;
    CREATE TABLE AUTORIA_PERSONA_DISPOSITIVO_INSCRIPCION (
        id INTEGER PRIMARY KEY,
        id_persona INTEGER,
        id_dispositivo_inscripcion INTEGER,
        FOREIGN KEY(id_persona) REFERENCES PERSONA (id),
        FOREIGN KEY(id_dispositivo_inscripcion) REFERENCES `DISPOSITIVO_INSCRIPCION` (id)
    );

    INSERT INTO AUTORIA_PERSONA_DISPOSITIVO_INSCRIPCION (id_persona, id_dispositivo_inscripcion)
    SELECT rid AS id_persona, id AS id_dispositivo_inscripcion FROM rel WHERE rkey LIKE 'actor autor' AND ridtype LIKE 'actor' ORDER BY id;


	/* **************************************** */
	/* AUTORIA_INSTITUCION_DISPOSITIVO_INSCRIPCION */
	/* **************************************** */

    DROP TABLE IF EXISTS AUTORIA_INSTITUCION_DISPOSITIVO_INSCRIPCION;
    CREATE TABLE AUTORIA_INSTITUCION_DISPOSITIVO_INSCRIPCION (
        id INTEGER PRIMARY KEY,
        id_institucion INTEGER,
        id_dispositivo_inscripcion INTEGER,
        FOREIGN KEY(id_institucion) REFERENCES INSTITUCION (id),
        FOREIGN KEY(id_dispositivo_inscripcion) REFERENCES `DISPOSITIVO_INSCRIPCION` (id)
    );

    INSERT INTO AUTORIA_INSTITUCION_DISPOSITIVO_INSCRIPCION (id_institucion, id_dispositivo_inscripcion)
    SELECT rid AS id_institucion, id AS id_dispositivo_inscripcion FROM rel WHERE rkey LIKE 'actor autor' AND ridtype LIKE 'institución' ORDER BY id;


	/* **************************************** */
	/* M2M EXPOSICION_PRESENTA_INSTITUCION */
	/* **************************************** */

    DROP TABLE IF EXISTS EXPOSICION_PRESENTA_INSTITUCION;
    CREATE TABLE EXPOSICION_PRESENTA_INSTITUCION (
        id INTEGER PRIMARY KEY,
        id_institucion INTEGER,
        id_exposicion INTEGER,
        FOREIGN KEY(id_exposicion) REFERENCES EXPOSICION (id),
        FOREIGN KEY(id_institucion) REFERENCES INSTITUCION (id)
    );

    INSERT INTO EXPOSICION_PRESENTA_INSTITUCION (id_institucion, id_exposicion)
    SELECT rid AS id_institucion, id AS id_exposicion FROM rel WHERE rkey LIKE 'actor artista' AND ridtype LIKE 'institución' ORDER BY id;


	/* **************************************** */
	/* M2M EXPOSICION_PRESENTA_PERSONA */
	/* **************************************** */

    DROP TABLE IF EXISTS EXPOSICION_PRESENTA_PERSONA;
    CREATE TABLE EXPOSICION_PRESENTA_PERSONA (
        id INTEGER PRIMARY KEY,
        id_persona INTEGER,
        id_exposicion INTEGER,
        FOREIGN KEY(id_exposicion) REFERENCES EXPOSICION (id),
        FOREIGN KEY(id_persona) REFERENCES PERSONA (id)
    );

    INSERT INTO EXPOSICION_PRESENTA_PERSONA (id_persona, id_exposicion)
    SELECT rid AS id_persona, id AS id_exposicion FROM rel WHERE rkey LIKE 'actor artista' AND ridtype LIKE 'actor' ORDER BY id;


	/* **************************************** */
        /* M2M PATROCINIO_DISPOSITIVO_INSCRIPCION_INSTITUCION */
	/* **************************************** */

    DROP TABLE IF EXISTS PATROCINIO_DISPOSITIVO_INSCRIPCION_INSTITUCION;
    CREATE TABLE PATROCINIO_DISPOSITIVO_INSCRIPCION_INSTITUCION (
        id INTEGER PRIMARY KEY,
        id_institucion INTEGER,
        id_dispositivo_inscripcion INTEGER,
        FOREIGN KEY(id_dispositivo_inscripcion) REFERENCES `DISPOSITIVO_INSCRIPCION` (id),
        FOREIGN KEY(id_institucion) REFERENCES INSTITUCION (id)
    );

    INSERT INTO PATROCINIO_DISPOSITIVO_INSCRIPCION_INSTITUCION (id_institucion, id_dispositivo_inscripcion)
    SELECT rid AS id_institucion, id AS id_dispositivo_inscripcion FROM rel WHERE rkey LIKE 'institución que lo patrocina' ORDER BY id;


	/* **************************************** */
        /* M2M DISPOSITIVO_INSCRIPCION_PRESENTA_OBRA_DE_ARTE */
	/* **************************************** */

    DROP TABLE IF EXISTS DISPOSITIVO_INSCRIPCION_PRESENTA_OBRA_DE_ARTE;
    CREATE TABLE DISPOSITIVO_INSCRIPCION_PRESENTA_OBRA_DE_ARTE (
        id INTEGER PRIMARY KEY,
        id_obra INTEGER,
        id_dispositivo_inscripcion INTEGER,
        FOREIGN KEY(id_dispositivo_inscripcion) REFERENCES `DISPOSITIVO_INSCRIPCION` (id),
        FOREIGN KEY(id_obra) REFERENCES `OBRA DE ARTE` (id)
    );

    INSERT INTO DISPOSITIVO_INSCRIPCION_PRESENTA_OBRA_DE_ARTE (id_obra, id_dispositivo_inscripcion)
    SELECT rid AS id_obra, id AS id_dispositivo_inscripcion FROM rel WHERE rkey LIKE 'obra de arte incluida' ORDER BY id;


	/* **************************************** */
        /* M2M DISPOSITIVO_INSCRIPCION_PRESENTA_ARTISTA */
	/* **************************************** */

    DROP TABLE IF EXISTS DISPOSITIVO_INSCRIPCION_PRESENTA_ARTISTA;
    CREATE TABLE DISPOSITIVO_INSCRIPCION_PRESENTA_ARTISTA (
        id INTEGER PRIMARY KEY,
        id_persona INTEGER,
        id_dispositivo_inscripcion INTEGER,
        FOREIGN KEY(id_dispositivo_inscripcion) REFERENCES `DISPOSITIVO_INSCRIPCION` (id),
        FOREIGN KEY(id_persona) REFERENCES PERSONA (id)
    );

    INSERT INTO DISPOSITIVO_INSCRIPCION_PRESENTA_ARTISTA (id_persona, id_dispositivo_inscripcion)
    SELECT rid AS id_persona, id AS id_dispositivo_inscripcion FROM rel WHERE rkey LIKE 'autor de obras de arte' ORDER BY id;


	/* **************************************** */
        /* M2M EDITOR_DISPOSITIVO_INSCRIPCION_PERSONA */
	/* **************************************** */

    DROP TABLE IF EXISTS EDITOR_DISPOSITIVO_INSCRIPCION_PERSONA;
    CREATE TABLE EDITOR_DISPOSITIVO_INSCRIPCION_PERSONA (
        id INTEGER PRIMARY KEY,
        id_persona INTEGER,
        id_dispositivo_inscripcion INTEGER,
        FOREIGN KEY(id_dispositivo_inscripcion) REFERENCES `DISPOSITIVO_INSCRIPCION` (id),
        FOREIGN KEY(id_persona) REFERENCES PERSONA (id)
    );

    INSERT INTO EDITOR_DISPOSITIVO_INSCRIPCION_PERSONA (id_persona, id_dispositivo_inscripcion)
    SELECT rid AS id_persona, id AS id_dispositivo_inscripcion FROM rel WHERE rkey LIKE 'actor editor' ORDER BY id;



    /* **************************************** */
        /* M2M ILUSTRADOR_DISPOSITIVO_INSCRIPCION_PERSONA */
	/* **************************************** */

    DROP TABLE IF EXISTS ILUSTRADOR_DISPOSITIVO_INSCRIPCION_PERSONA;
    CREATE TABLE ILUSTRADOR_DISPOSITIVO_INSCRIPCION_PERSONA (
        id INTEGER PRIMARY KEY,
        id_persona INTEGER,
        id_dispositivo_inscripcion INTEGER,
        FOREIGN KEY(id_dispositivo_inscripcion) REFERENCES `DISPOSITIVO_INSCRIPCION` (id),
        FOREIGN KEY(id_persona) REFERENCES PERSONA (id)
    );

    INSERT INTO ILUSTRADOR_DISPOSITIVO_INSCRIPCION_PERSONA (id_persona, id_dispositivo_inscripcion)
    SELECT rid AS id_persona, id AS id_dispositivo_inscripcion FROM rel WHERE rkey LIKE 'ilustrador' ORDER BY id;


	/* **************************************** */
        /* M2M INSTITUCION_MATRIZ */
	/* **************************************** */

    DROP TABLE IF EXISTS INSTITUCION_MATRIZ;
    CREATE TABLE INSTITUCION_MATRIZ (
        id INTEGER PRIMARY KEY,
		id_institucion_padre INTEGER,
        id_institucion INTEGER,
        FOREIGN KEY(id_institucion) REFERENCES INSTITUCION (id),
        FOREIGN KEY(id_institucion_padre) REFERENCES INSTITUCION (id)
    );

    INSERT INTO INSTITUCION_MATRIZ (id_institucion_padre, id_institucion)
    SELECT rid AS id_institucion_padre, id AS id_institucion FROM rel WHERE rkey LIKE 'institución matriz' ORDER BY id;


	/* **************************************** */
        /* M2M FUENTE_INFORMACION_EXPOSICION_INSTITUCION */
	/* **************************************** */

    DROP TABLE IF EXISTS FUENTE_INFORMACION_EXPOSICION_INSTITUCION;
    CREATE TABLE FUENTE_INFORMACION_EXPOSICION_INSTITUCION (
        id INTEGER PRIMARY KEY,
        id_institucion INTEGER,
        id_exposicion INTEGER,
        FOREIGN KEY(id_institucion) REFERENCES INSTITUCION (id),
        FOREIGN KEY(id_exposicion) REFERENCES EXPOSICION (id)
    );

    INSERT INTO FUENTE_INFORMACION_EXPOSICION_INSTITUCION (id_institucion, id_exposicion)
    SELECT rid AS id_institucion, id AS id_exposicion FROM rel WHERE rkey LIKE 'fuente de información' or rkey LIKE 'institución origen de la información' ORDER BY id;


	/* **************************************** */
        /* M2M ORGANIZACION_EXPOSICION_INSTITUCION */
	/* **************************************** */

    DROP TABLE IF EXISTS ORGANIZACION_EXPOSICION_INSTITUCION;
    CREATE TABLE ORGANIZACION_EXPOSICION_INSTITUCION (
        id INTEGER PRIMARY KEY,
        id_institucion INTEGER,
        id_exposicion INTEGER,
        FOREIGN KEY(id_institucion) REFERENCES INSTITUCION (id),
        FOREIGN KEY(id_exposicion) REFERENCES EXPOSICION (id)
    );

    INSERT INTO ORGANIZACION_EXPOSICION_INSTITUCION (id_institucion, id_exposicion)
    SELECT rid AS id_institucion, id AS id_exposicion FROM rel WHERE rkey LIKE 'institución organizadora' ORDER BY id;


	/* **************************************** */
        /* M2M COMISARIO_EXPOSICION_PERSONA */
	/* **************************************** */

    DROP TABLE IF EXISTS COMISARIO_EXPOSICION_PERSONA;
    CREATE TABLE COMISARIO_EXPOSICION_PERSONA (
        id INTEGER PRIMARY KEY,
        id_persona INTEGER,
        id_exposicion INTEGER,
        FOREIGN KEY(id_persona) REFERENCES PERSONA (id),
        FOREIGN KEY(id_exposicion) REFERENCES EXPOSICION (id)
    );

    INSERT INTO COMISARIO_EXPOSICION_PERSONA (id_persona, id_exposicion)
    SELECT rid AS id_persona, id AS id_exposicion FROM rel WHERE rkey LIKE 'actor comisario' ORDER BY id;


	/* **************************************** */
        /* M2M EXPOSICION_TIENE_DISPOSITIVO_INSCRIPCION */
	/* **************************************** */

    DROP TABLE IF EXISTS EXPOSICION_TIENE_DISPOSITIVO_INSCRIPCION;
    CREATE TABLE EXPOSICION_TIENE_DISPOSITIVO_INSCRIPCION (
        id INTEGER PRIMARY KEY,
        id_dispositivo_inscripcion INTEGER,
        id_exposicion INTEGER,
        FOREIGN KEY(id_dispositivo_inscripcion) REFERENCES `DISPOSITIVO_INSCRIPCION` (id),
        FOREIGN KEY(id_exposicion) REFERENCES EXPOSICION (id)
    );

    INSERT INTO EXPOSICION_TIENE_DISPOSITIVO_INSCRIPCION (id_dispositivo_inscripcion, id_exposicion)
    SELECT rid AS id_dispositivo_inscripcion, id AS id_exposicion FROM rel WHERE rkey LIKE 'catálogo' AND ridtype LIKE 'catálogo' ORDER BY id;


	/* **************************************** */
        /* M2M PATROCINIO_EXPOSICION_INSTITUCION */
	/* **************************************** */

    DROP TABLE IF EXISTS PATROCINIO_EXPOSICION_INSTITUCION;
    CREATE TABLE PATROCINIO_EXPOSICION_INSTITUCION (
        id INTEGER PRIMARY KEY,
        id_institucion INTEGER,
        id_exposicion INTEGER,
        FOREIGN KEY(id_institucion) REFERENCES INSTITUCION (id),
        FOREIGN KEY(id_exposicion) REFERENCES EXPOSICION (id)
    );

    INSERT INTO PATROCINIO_EXPOSICION_INSTITUCION (id_institucion, id_exposicion)
    SELECT rid AS id_institucion, id AS id_exposicion FROM rel WHERE rkey LIKE 'institución patrocinadora' ORDER BY id;


	/* **************************************** */
        /* M2M COLECCIONISTA_PRESTATARIO_INSTITUCION_EXPOSICION */
	/* **************************************** */

    DROP TABLE IF EXISTS COLECCIONISTA_PRESTATARIO_INSTITUCION_EXPOSICION;
    CREATE TABLE COLECCIONISTA_PRESTATARIO_INSTITUCION_EXPOSICION (
        id INTEGER PRIMARY KEY,
        id_institucion INTEGER,
        id_exposicion INTEGER,
        FOREIGN KEY(id_institucion) REFERENCES INSTITUCION (id),
        FOREIGN KEY(id_exposicion) REFERENCES EXPOSICION (id)
    );

    INSERT INTO COLECCIONISTA_PRESTATARIO_INSTITUCION_EXPOSICION (id_institucion, id_exposicion)
    SELECT rid AS id_institucion, id AS id_exposicion FROM rel WHERE rkey LIKE 'coleccionista prestatario' AND ridtype LIKE 'institución' ORDER BY id;


	/* **************************************** */
        /* M2M COLECCIONISTA_PRESTATARIO_PERSONA_EXPOSICION */
	/* **************************************** */

    DROP TABLE IF EXISTS COLECCIONISTA_PRESTATARIO_PERSONA_EXPOSICION;
    CREATE TABLE COLECCIONISTA_PRESTATARIO_PERSONA_EXPOSICION (
        id INTEGER PRIMARY KEY,
        id_persona INTEGER,
        id_exposicion INTEGER,
        FOREIGN KEY(id_persona) REFERENCES PERSONA (id),
        FOREIGN KEY(id_exposicion) REFERENCES EXPOSICION (id)
    );

    INSERT INTO COLECCIONISTA_PRESTATARIO_PERSONA_EXPOSICION (id_persona, id_exposicion)
    SELECT rid AS id_persona, id AS id_exposicion FROM rel WHERE rkey LIKE 'coleccionista prestatario' AND ridtype LIKE 'actor' ORDER BY id;


	/* **************************************** */
        /* M2M MUSEOGRAFIA_EMPRESA_EXPOSICION */
	/* **************************************** */

    DROP TABLE IF EXISTS MUSEOGRAFIA_EMPRESA_EXPOSICION;
    CREATE TABLE MUSEOGRAFIA_EMPRESA_EXPOSICION (
        id INTEGER PRIMARY KEY,
        id_exposicion INTEGER,
        id_empresa INTEGER,
        FOREIGN KEY(id_empresa) REFERENCES EMPRESA (id),
        FOREIGN KEY(id_exposicion) REFERENCES EXPOSICION (id)
    );

    INSERT INTO MUSEOGRAFIA_EMPRESA_EXPOSICION (id_exposicion, id_empresa)
    SELECT ID AS id_exposicion, RID AS id_empresa FROM rel WHERE rkey LIKE 'empresa que realiza la museografía' ORDER BY id;


	/* **************************************** */
        /* M2M EXPOSICION_MATRIZ */
	/* **************************************** */

    DROP TABLE IF EXISTS EXPOSICION_MATRIZ;
    CREATE TABLE EXPOSICION_MATRIZ (
        id INTEGER PRIMARY KEY,
        id_exposicion INTEGER,
        id_exposicion_padre INTEGER,
        FOREIGN KEY(id_exposicion) REFERENCES EXPOSICION (id),
        FOREIGN KEY(id_exposicion_padre) REFERENCES EXPOSICION (id)
    );

    INSERT INTO EXPOSICION_MATRIZ (id_exposicion, id_exposicion_padre)
    SELECT ID AS id_exposicion, RID AS id_exposicion_padre FROM rel WHERE rkey LIKE 'exposición de la que depende' ORDER BY id;


	/* **************************************** */
        /* M2M RELACION_PERSONA_INSTITUCION */
	/* **************************************** */

    DROP TABLE IF EXISTS RELACION_PERSONA_INSTITUCION;
    CREATE TABLE RELACION_PERSONA_INSTITUCION (
        id INTEGER PRIMARY KEY,
        id_persona INTEGER,
        id_institucion INTEGER,
        FOREIGN KEY(id_persona) REFERENCES PERSONA (id),
        FOREIGN KEY(id_institucion) REFERENCES INSTITUCION (id)
    );

    INSERT INTO RELACION_PERSONA_INSTITUCION (id_persona, id_institucion)
    SELECT ID AS id_persona, RID AS id_institucion FROM rel WHERE rkey LIKE 'institución con la que se relaciona' ORDER BY id;


	/* **************************************** */
        /* M2M RELACION_PERSONA_PERSONA */
	/* **************************************** */

    DROP TABLE IF EXISTS RELACION_PERSONA_PERSONA;
    CREATE TABLE RELACION_PERSONA_PERSONA (
        id INTEGER PRIMARY KEY,
        id_persona INTEGER,
        id_persona_2 INTEGER,
        FOREIGN KEY(id_persona) REFERENCES PERSONA (id),
        FOREIGN KEY(id_persona_2) REFERENCES PERSONA (id)
    );

    INSERT INTO RELACION_PERSONA_PERSONA (id_persona, id_persona_2)
    SELECT ID AS id_persona, RID AS id_persona_2 FROM rel WHERE rkey LIKE 'actor con el que se relaciona' ORDER BY id;


	/* **************************************** */
    /* PERFORMANCE INDEXES */
    /* **************************************** */

    -- Primary tables
    CREATE INDEX IF NOT EXISTS idx_exposicion_nombre ON EXPOSICION(nombre);
    CREATE INDEX IF NOT EXISTS idx_persona_nombre ON PERSONA(nombre);
    CREATE INDEX IF NOT EXISTS idx_institucion_nombre ON INSTITUCION(nombre);
    CREATE INDEX IF NOT EXISTS idx_empresa_nombre ON EMPRESA(nombre);
    CREATE INDEX IF NOT EXISTS idx_obra_arte_nombre ON `OBRA DE ARTE`(nombre);
    CREATE INDEX IF NOT EXISTS idx_dispositivo_nombre ON `DISPOSITIVO_INSCRIPCION`(nombre);

    -- M2M relationship tables
    CREATE INDEX IF NOT EXISTS idx_tipologia_exp_exp ON TIPOLOGIA_EXPOSICION(id_exposicion);
    CREATE INDEX IF NOT EXISTS idx_tipologia_exp_tipo ON TIPOLOGIA_EXPOSICION(id_tipologia);
    CREATE INDEX IF NOT EXISTS idx_tipologia_inst_inst ON TIPOLOGIA_INSTITUCION(id_institucion);
    CREATE INDEX IF NOT EXISTS idx_tipologia_inst_tipo ON TIPOLOGIA_INSTITUCION(id_tipologia);
    CREATE INDEX IF NOT EXISTS idx_tipologia_obra_obra ON TIPOLOGIA_OBRA_DE_ARTE(id_obra);
    CREATE INDEX IF NOT EXISTS idx_tipologia_obra_tipo ON TIPOLOGIA_OBRA_DE_ARTE(id_tipologia);
    
    -- Exhibition relationships
    CREATE INDEX IF NOT EXISTS idx_exp_pers_exp ON EXPOSICION_PRESENTA_PERSONA(id_exposicion);
    CREATE INDEX IF NOT EXISTS idx_exp_pers_pers ON EXPOSICION_PRESENTA_PERSONA(id_persona);
    CREATE INDEX IF NOT EXISTS idx_comisario_exp ON COMISARIO_EXPOSICION_PERSONA(id_exposicion);
    CREATE INDEX IF NOT EXISTS idx_comisario_pers ON COMISARIO_EXPOSICION_PERSONA(id_persona);
    CREATE INDEX IF NOT EXISTS idx_org_exp_inst ON ORGANIZACION_EXPOSICION_INSTITUCION(id_institucion);
    CREATE INDEX IF NOT EXISTS idx_org_exp_exp ON ORGANIZACION_EXPOSICION_INSTITUCION(id_exposicion);

    -- Activity and ownership
    CREATE INDEX IF NOT EXISTS idx_actividad_pers ON ACTIVIDAD_PERSONA(id_persona);
    CREATE INDEX IF NOT EXISTS idx_prop_pers_obra ON PROPIETARIO_PERSONA_OBRA(id_persona);
    CREATE INDEX IF NOT EXISTS idx_prop_inst_obra ON PROPIETARIO_INSTITUCION_OBRA(id_institucion);