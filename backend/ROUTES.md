# Referencia de Rutas de la API

**URL Base:** `http://localhost:8000/api/v1`

## 📚 Documentación
- **Docs Interactiva (Swagger):** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

## 🏠 General
- `GET /api/v1/` - Endpoint raíz (Hello World)

## 👥 Personas (Persons)
- `GET /api/v1/all_personas` - Obtener todas las personas
- `GET /api/v1/count_actants` - Contar todos los actantes
- `GET /api/v1/get_persona/{id}` - Obtener persona por ID
- `POST /api/v1/post_persona` - Crear nueva persona

## 🏛️ Instituciones (Institutions)
- `GET /api/v1/all_instituciones` - Obtener todas las instituciones
- `GET /api/v1/count_instituciones` - Contar todas las instituciones
- `GET /api/v1/get_institucion/{id}` - Obtener institución por ID
- `POST /api/v1/post_institucion` - Crear nueva institución

## 🎨 Exposiciones (Exhibitions)
- `GET /api/v1/all_exposiciones` - Obtener todas las exposiciones
- `GET /api/v1/count_exposiciones` - Contar todas las exposiciones
- `POST /api/v1/post_exposicion` - Crear nueva exposición

## 🖼️ Obras (Artworks)
- `GET /api/v1/all_obras` - Obtener todas las obras
- `GET /api/v1/count_obras` - Contar todas las obras
- `POST /api/v1/post_obra` - Crear nueva obra

## 🔍 Miscelánea
- `GET /api/v1/semantic_search?q={query}` - Búsqueda semántica
- `GET /api/v1/all_classes` - Obtener todas las clases de la ontología
- `GET /api/v1/get_object_any_type/{type}/{id}` - Obtener cualquier objeto por tipo e ID

## 🔐 Usuarios (Autenticación)
- `GET /api/v1/users/me` - Obtener información del usuario actual (requiere autenticación)
- `GET /api/v1/secure-endpoint` - Ejemplo de endpoint seguro (requiere autenticación)

## 📝 Ejemplos

### Probar endpoint básico:
```bash
curl http://localhost:8000/api/v1/
```

### Contar exposiciones:
```bash
curl http://localhost:8000/api/v1/count_exposiciones
```

### Obtener todas las personas:
```bash
curl http://localhost:8000/api/v1/all_personas
```

### Búsqueda semántica:
```bash
curl "http://localhost:8000/api/v1/semantic_search?q=picasso"
```

**Nota:** Todas las rutas requieren el prefijo `/api/v1` según está configurado en la variable `DEPLOY_PATH` de tu archivo `.env`.
