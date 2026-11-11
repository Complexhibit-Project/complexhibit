# Script de inicialización completa del proyecto Complexhibit
# Ejecutar con: .\init.ps1

param(
    [switch]$SkipDataLoad = $false
)

Write-Host "--------------------------------------------------------" -ForegroundColor Cyan
Write-Host "     Complexhibit - Inicializacion del Proyecto         " -ForegroundColor Cyan
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Docker
Write-Host "[1/6] Verificando Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    docker-compose --version | Out-Null
    Write-Host "[OK] Docker esta instalado" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker no esta instalado o no esta en el PATH" -ForegroundColor Red
    exit 1
}

# 2. Verificar archivos necesarios
Write-Host "[2/6] Verificando archivos necesarios..." -ForegroundColor Yellow
$requiredFiles = @(
    "docker-compose.yml",
    "backend/virtuoso.ini",
    "backend/result.nt"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "[OK] $file encontrado" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] $file no encontrado" -ForegroundColor Red
        exit 1
    }
}

# 3. Verificar/Crear archivo .env
Write-Host "[3/6] Configurando variables de entorno..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.template") {
        Copy-Item ".env.template" ".env"
        Write-Host "[OK] Archivo .env creado desde .env.template" -ForegroundColor Green
        Write-Host "  [?] Recuerda editar .env con tus configuraciones" -ForegroundColor Yellow
    } else {
        Write-Host "[ERROR] No se encontro .env.template" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[OK] Archivo .env ya existe" -ForegroundColor Green
}

# 4. Detener contenedores existentes
Write-Host "[4/6] Limpiando contenedores existentes..." -ForegroundColor Yellow
docker-compose down -v 2>$null
Write-Host "[OK] Contenedores detenidos" -ForegroundColor Green

# 5. Iniciar servicios
Write-Host "[5/6] Iniciando servicios..." -ForegroundColor Yellow
docker-compose up -d

# Esperar a que Virtuoso este listo
Write-Host "  Esperando a que Virtuoso este disponible..." -ForegroundColor Cyan
$max_attempts = 60
$attempt = 0
$connected = $false

while (-not $connected -and $attempt -lt $max_attempts) {
    $attempt++
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.Connect("localhost", 1111)
        $tcpClient.Close()
        $connected = $true
    } catch {
        if ($attempt % 5 -eq 0) {
            Write-Host "  Intento $attempt/$max_attempts..." -ForegroundColor Gray
        }
        Start-Sleep -Seconds 2
    }
}

if ($connected) {
    Write-Host "[OK] Virtuoso esta disponible" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Virtuoso no respondio despues de $max_attempts intentos" -ForegroundColor Red
    Write-Host "  Ejecuta: docker logs complexhibit-virtuoso" -ForegroundColor Yellow
    exit 1
}

# 6. Cargar datos
if (-not $SkipDataLoad) {
    Write-Host "[6/6] Cargando datos en Virtuoso..." -ForegroundColor Yellow
    Write-Host "  Esto puede tardar varios minutos..." -ForegroundColor Cyan
    
    try {
        & ".\backend\scripts\load_data.ps1"
        Write-Host "[OK] Datos cargados exitosamente" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Error al cargar datos: $_" -ForegroundColor Red
        Write-Host "  Puedes cargar los datos manualmente mas tarde con:" -ForegroundColor Yellow
        Write-Host "  .\backend\scripts\load_data.ps1" -ForegroundColor White
    }
} else {
    Write-Host "[6/6] Omitiendo carga de datos (--SkipDataLoad)" -ForegroundColor Yellow
}

# Resumen
Write-Host ""
Write-Host "--------------------------------------------------------" -ForegroundColor Green
Write-Host "              [OK] Inicializacion Completada            " -ForegroundColor Green
Write-Host "--------------------------------------------------------" -ForegroundColor Green
Write-Host ""
Write-Host "Servicios disponibles:" -ForegroundColor Cyan
Write-Host "  - API:                http://localhost:8000/api/v1/" -ForegroundColor White
Write-Host "  - Virtuoso Conductor: http://localhost:8890/conductor" -ForegroundColor White
Write-Host "  - SPARQL Endpoint:    http://localhost:8890/sparql" -ForegroundColor White
Write-Host ""
Write-Host "Credenciales Virtuoso:" -ForegroundColor Cyan
Write-Host "  - Usuario:   dba" -ForegroundColor White
Write-Host "  - Contrasena: la definida en .env (VIRTUOSO_DBA_PASSWORD)" -ForegroundColor White
Write-Host ""
Write-Host "Comandos utiles:" -ForegroundColor Cyan
Write-Host "  - Ver logs:           docker-compose logs -f" -ForegroundColor White
Write-Host "  - Detener servicios:  docker-compose down" -ForegroundColor White
Write-Host "  - Reiniciar:          docker-compose restart" -ForegroundColor White
Write-Host "  - Cargar datos:       .\backend\scripts\load_data.ps1" -ForegroundColor White
Write-Host ""
