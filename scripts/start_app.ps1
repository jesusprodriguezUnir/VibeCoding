# Script de inicio para la aplicación Jira Viewer
# Asegura que se use el entorno virtual correcto

Write-Host "🚀 Iniciando Jira Viewer (Mejorado)..." -ForegroundColor Green
Write-Host "📁 Directorio: $PWD" -ForegroundColor Yellow

# Cambiar al directorio del proyecto
Set-Location "C:\Temp\VibeCoding"

# Activar entorno virtual
Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Yellow
& "C:\Temp\VibeCoding\.venv\Scripts\Activate.ps1"

# Verificar dependencias críticas
Write-Host "🔍 Verificando dependencias..." -ForegroundColor Yellow
$dependencies = @("streamlit", "plotly", "pandas", "requests")
foreach ($dep in $dependencies) {
    $installed = & pip list | Select-String $dep
    if ($installed) {
        Write-Host "  ✅ $dep instalado" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $dep NO encontrado" -ForegroundColor Red
        Write-Host "  Instalando $dep..." -ForegroundColor Yellow
        & pip install $dep
    }
}

# Mostrar información del entorno
Write-Host "🐍 Python ejecutable:" -ForegroundColor Yellow
& python -c "import sys; print(f'  {sys.executable}')"

Write-Host "📦 Versión Streamlit:" -ForegroundColor Yellow
& streamlit version

# Mostrar características nuevas
Write-Host ""
Write-Host "🎨 NUEVAS CARACTERÍSTICAS:" -ForegroundColor Cyan
Write-Host "  🎴 Vista de Cards Elegantes con enlaces directos a Jira" -ForegroundColor Green
Write-Host "  📊 Vista de Tabla Mejorada con columnas de enlaces" -ForegroundColor Green
Write-Host "  🔍 Filtros avanzados más intuitivos" -ForegroundColor Green
Write-Host "  📄 Paginación automática para mejor performance" -ForegroundColor Green
Write-Host ""

# Iniciar aplicación
Write-Host "🚀 Iniciando Streamlit..." -ForegroundColor Green
Write-Host "🌐 URL: http://localhost:8501" -ForegroundColor Cyan
Write-Host "📋 Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host ""

& streamlit run app.py