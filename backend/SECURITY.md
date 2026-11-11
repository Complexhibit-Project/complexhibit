# Política de Seguridad

## Versiones Soportadas

Liberamos parches para vulnerabilidades de seguridad para las siguientes versiones:

| Versión | Soportada          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reportar una Vulnerabilidad

Tomamos la seguridad de la API Complexhibit muy en serio. Si crees que has encontrado una vulnerabilidad de seguridad, por favor repórtala como se describe a continuación.

### Por favor NO:

- Abrir un issue público en GitHub
- Divulgar la vulnerabilidad públicamente antes de que haya sido abordada

### Por favor SÍ:

1. **Envíanos un email directamente** a: [martinjs@uma.es]
2. **Incluir la siguiente información**:
   - Tipo de vulnerabilidad
   - Rutas completas de archivo(s) fuente relacionado(s) con la vulnerabilidad
   - Ubicación del código fuente afectado (tag/branch/commit o URL directa)
   - Instrucciones paso a paso para reproducir el problema
   - Código de prueba de concepto o exploit (si es posible)
   - Impacto de la vulnerabilidad

### Qué esperar:

- **Reconocimiento**: Reconoceremos la recepción de tu reporte de vulnerabilidad en 48 horas
- **Comunicación**: Te enviaremos actualizaciones regulares sobre nuestro progreso
- **Cronograma**: Nuestro objetivo es parchear vulnerabilidades críticas en 7 días
- **Crédito**: Te acreditaremos en nuestro aviso de seguridad (a menos que prefieras permanecer anónimo)

## Mejores Prácticas de Seguridad

### Para Desarrolladores

1. **Variables de Entorno**: Nunca hacer commit de archivos `.env` o secretos al repositorio
2. **Dependencias**: Mantener dependencias actualizadas con `pip-audit` o `safety`
3. **Autenticación**: Siempre usar tokens JWT para endpoints protegidos
4. **Validación de Entrada**: Usar modelos Pydantic para todas las entradas
5. **Inyección SPARQL**: Usar queries parametrizadas, nunca concatenación de strings

### Para Despliegue

1. **Solo HTTPS**: Siempre usar HTTPS en producción
2. **Gestión de Secretos**: Usar gestión apropiada de secretos (ej: AWS Secrets Manager, HashiCorp Vault)
3. **Seguridad de Docker**: 
   - Ejecutar contenedores como usuario no-root
   - Usar imágenes base oficiales
   - Escanear imágenes con Trivy o herramientas similares
4. **Seguridad de Red**: 
   - Usar firewalls para restringir acceso
   - Implementar limitación de tasa
   - Usar VPCs para acceso a base de datos

### Consideraciones de Seguridad Conocidas

1. **Secreto JWT**: El `JWT_SECRET` debe mantenerse seguro y rotarse regularmente
2. **Endpoint SPARQL**: Debe estar detrás de autenticación y no ser públicamente accesible
3. **CORS**: Configurar `allow_origins` apropiadamente para producción (no `["*"]`)

## Actualizaciones de Seguridad

Las actualizaciones de seguridad se liberarán como versiones de parche (ej: 1.0.1, 1.0.2) y se documentarán en:
- [CHANGELOG.md](CHANGELOG.md)
- [GitHub Security Advisories](https://github.com/MartinM10/ontoexhibit-api/security/advisories)
- [GitHub Releases](https://github.com/MartinM10/ontoexhibit-api/releases)

## Escaneo de Seguridad Automatizado

Este proyecto usa:
- **Dependabot**: Actualizaciones automatizadas de dependencias
- **Trivy**: Escaneo de vulnerabilidades de contenedores
- **GitHub CodeQL**: Análisis de seguridad de código
- **Safety**: Verificación de vulnerabilidades de dependencias Python

## Cumplimiento

Este proyecto sigue:
- Prácticas de seguridad OWASP Top 10
- Directrices CWE (Common Weakness Enumeration)
- Estándares de codificación segura para Python

## Contacto

Para preguntas o preocupaciones relacionadas con seguridad, contactar:
- **Email**: martinjs@uma.es

---

**Última Actualización**: 2025-11-26
