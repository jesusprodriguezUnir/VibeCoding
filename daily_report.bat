@echo off
REM Script de automatización para Windows
REM Ejecuta reportes diarios de Jira

echo Generando reporte diario de Jira...
cd /d "%~dp0"

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Generar reporte de issues asignados a mí
echo Generando reporte de mis issues...
python jira_viewer.py --all --export csv --output "daily_report_%date:~-4,4%%date:~-10,2%%date:~-7,2%.csv"

REM Generar reporte de actualizaciones de hoy
echo Generando reporte de actualizaciones de hoy...
python jira_viewer.py --recent --days 1 --export csv --output "today_updates_%date:~-4,4%%date:~-10,2%%date:~-7,2%.csv"

echo Reportes generados exitosamente!
pause