# VibeCoding - Script de Inicio Mejorado
# Versión 2.0 - Con verificaciones y diagnósticos

Write-Host "🚀 VibeCoding - Iniciando Aplicación" -ForegroundColor Cyan
Write-Host "=" * 50

# Función para mostrar pasos
function Write-Step {
    param($Step, $Message)
    Write-Host "[$Step] $Message" -ForegroundColor Yellow
}

# Verificar que estamos en el directorio correcto
Write-Step "1/6" "Verificando directorio..."
if (-not (Test-Path "app.py")) {
    Write-Host "❌ Error: No se encuentra app.py en el directorio actual" -ForegroundColor Red
    Write-Host "   Asegúrate de estar en el directorio VibeCoding" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host "✅ Directorio correcto" -ForegroundColor Green

# Verificar entorno virtual
Write-Step "2/6" "Verificando entorno virtual..."
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Error: No se encuentra el entorno virtual" -ForegroundColor Red
    Write-Host "   Ejecuta: python -m venv .venv" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host "✅ Entorno virtual encontrado" -ForegroundColor Green

# Activar entorno virtual
Write-Step "3/6" "Activando entorno virtual..."
try {
    & ".\.venv\Scripts\Activate.ps1"
    Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
} catch {
    Write-Host "❌ Error activando entorno virtual: $_" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar Python y Streamlit
Write-Step "4/6" "Verificando Python y Streamlit..."
try {
    $pythonVersion = & python --version
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
    
    $streamlitVersion = & python -m streamlit --version
    Write-Host "✅ $streamlitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python o Streamlit no están disponibles" -ForegroundColor Red
    Write-Host "   Ejecuta: pip install -r requirements.txt" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar configuración (opcional)
Write-Step "5/6" "Verificando configuración..."
try {
    & python -c "from core.config import Config; Config.get_jira_config(); print('Config OK')" 2>$null
    Write-Host "✅ Configuración de Jira válida" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Advertencia: Configuración de Jira no encontrada" -ForegroundColor Yellow
    Write-Host "   Configura .env o .streamlit/secrets.toml antes de usar" -ForegroundColor Yellow
}

# Encontrar puerto disponible
Write-Step "6/6" "Verificando puerto..."
$port = 8508
for ($i = $port; $i -le 8520; $i++) {
    $connection = Test-NetConnection -ComputerName "localhost" -Port $i -InformationLevel Quiet -WarningAction SilentlyContinue
    if (-not $connection) {
        $port = $i
        break
    }
}
Write-Host "✅ Usando puerto $port" -ForegroundColor Green

# Iniciar aplicación
Write-Host ""
Write-Host "� Iniciando VibeCoding..." -ForegroundColor Green
Write-Host "🌐 URL: http://localhost:$port" -ForegroundColor Cyan
Write-Host "🛑 Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host "-" * 50

try {
    # Usar ruta completa para mayor confiabilidad
    & ".\.venv\Scripts\streamlit.exe" run app.py --server.port $port --server.headless false
} catch {
    Write-Host ""
    Write-Host "❌ Error ejecutando aplicación: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Soluciones alternativas:" -ForegroundColor Yellow
    Write-Host "1. Usar script Python: python run_app.py" -ForegroundColor White
    Write-Host "2. Reinstalar dependencias: pip install -r requirements.txt --force-reinstall" -ForegroundColor White
    Write-Host "3. Verificar entorno virtual: python --version" -ForegroundColor White
}

Write-Host ""
Write-Host "� ¡Gracias por usar VibeCoding!" -ForegroundColor Cyan
Read-Host "Presiona Enter para salir"