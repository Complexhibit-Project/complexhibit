# Script PowerShell para cargar datos RDF en Virtuoso
# Uso: .\load_data.ps1

Write-Host "=== Cargando datos en Virtuoso ===" -ForegroundColor Green

# Configuración
$VIRTUOSO_HOST = "localhost"
$VIRTUOSO_PORT = "1111"
$VIRTUOSO_USER = "dba"
$VIRTUOSO_PASSWORD = if ($env:VIRTUOSO_DBA_PASSWORD) { $env:VIRTUOSO_DBA_PASSWORD } else { "dba" }
$GRAPH_URI = "https://w3id.org/OntoExhibit/Data"
$DATA_FILE = "/database/result.nt"

# Esperar a que Virtuoso esté listo
Write-Host "Esperando a que Virtuoso esté disponible..." -ForegroundColor Yellow
$max_attempts = 30
$attempt = 0
$connected = $false

while (-not $connected -and $attempt -lt $max_attempts) {
    $attempt++
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.Connect($VIRTUOSO_HOST, $VIRTUOSO_PORT)
        $tcpClient.Close()
        $connected = $true
        Write-Host "Virtuoso está disponible!" -ForegroundColor Green
    }
    catch {
        Write-Host "Intento $attempt/$max_attempts - Esperando..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if (-not $connected) {
    Write-Host "Error: Virtuoso no está disponible después de $max_attempts intentos" -ForegroundColor Red
    exit 1
}

# Cargar datos usando isql
Write-Host "Cargando datos desde $DATA_FILE al grafo $GRAPH_URI..." -ForegroundColor Yellow

$isqlCommands = @"
SPARQL CLEAR GRAPH <$GRAPH_URI>;
DELETE FROM DB.DBA.load_list;
ld_dir('/database', 'result.nt', '$GRAPH_URI');
SELECT * FROM DB.DBA.load_list;
rdf_loader_run();
checkpoint;
RDF_OBJ_FT_RULE_ADD(null, null, 'All');
VT_INC_INDEX_DB_DBA_RDF_OBJ();
checkpoint;
SELECT COUNT(*) FROM DB.DBA.RDF_QUAD WHERE G = iri_to_id('$GRAPH_URI');
EXIT;
"@

$isqlCommands | docker exec -i complexhibit-virtuoso isql $VIRTUOSO_PORT $VIRTUOSO_USER $VIRTUOSO_PASSWORD

Write-Host ""
Write-Host "=== Carga de datos completada ===" -ForegroundColor Green
Write-Host ""
Write-Host "Para verificar los datos cargados, accede a:" -ForegroundColor Cyan
Write-Host "  - Conductor: http://localhost:8890/conductor" -ForegroundColor White
Write-Host "  - SPARQL Endpoint: http://localhost:8890/sparql" -ForegroundColor White
Write-Host ""
Write-Host "Credenciales:" -ForegroundColor Cyan
Write-Host "  Usuario: dba" -ForegroundColor White
Write-Host "  Contraseña: dba (o la configurada en VIRTUOSO_DBA_PASSWORD)" -ForegroundColor White
