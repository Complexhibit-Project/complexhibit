# Complexhibit Frontend

Aplicación frontend para Complexhibit, construida con Next.js.

## Inicio Rápido

### Requisitos Previos

- Node.js 18+
- Servicios del backend ejecutándose (ver README raíz)

### Instalación

```bash
npm install
```

### Configuración

La aplicación depende de variables de entorno para la conexión con la API.
Cuando se ejecuta vía Docker (desde la raíz), estas se inyectan automáticamente.

Para desarrollo local:
1. Crea un archivo `.env.local` en este directorio.
2. Añade lo siguiente:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Ejecución Local

```bash
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000) en tu navegador.

## Estructura del Proyecto

- `src/app`: Páginas y layouts del App Router.
- `src/components`: Componentes UI reutilizables.
- `src/lib`: Funciones de utilidad y clientes API.

## ✨ Características Principales

- **Contadores en Home**: Visualización en tiempo real de la cantidad de entidades (Exposiciones, Obras, etc.) en las tarjetas de inicio.
- **Búsqueda Semántica**: Interfaz para buscar en el grafo de conocimiento.
- **Exportación de Detalle**: Descarga de fichas de detalle en formatos PDF (HTML), JSON y HTML plano.
- **Consultas de Ejemplo**: Selector interactivo de consultas SPARQL con visualización de resultados integrada.
- **Inserción de Datos**: Formularios protegidos (requiere login) para añadir nuevos datos.
- **Registro Mejorado**: Registro de usuarios con selección de tipo de institución.
- **Analíticas y Dashboard**: Panel de administración para visualizar métricas de uso (descargas, visitas) y sistema de tracking integrado.
