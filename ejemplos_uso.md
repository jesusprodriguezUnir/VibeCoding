# Ejemplos de Uso del Visualizador de Jira

## Instalación Rápida

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar credenciales
python jira_viewer.py --setup
# Editar .env con tus credenciales reales

# Probar conexión
python jira_viewer.py --test
```

## Ejemplos Básicos

### Ver todos mis issues
```bash
python jira_viewer.py --all
```

### Ver solo issues en progreso
```bash
python jira_viewer.py --status "In Progress"
```

### Ver issues del proyecto específico
```bash
python jira_viewer.py --project "MYPROJ"
```

### Ver issues actualizados en los últimos 3 días
```bash
python jira_viewer.py --recent --days 3
```

## Ejemplos de Exportación

### Exportar todos mis issues a CSV
```bash
python jira_viewer.py --all --export csv --output "mis_issues.csv"
```

### Exportar issues recientes a JSON
```bash
python jira_viewer.py --recent --export json --output "issues_recientes.json"
```

## Ejemplos con JQL Personalizado

### Issues de alta prioridad
```bash
python jira_viewer.py --jql "assignee = currentUser() AND priority = High"
```

### Issues vencidos
```bash
python jira_viewer.py --jql "assignee = currentUser() AND duedate < now()"
```

### Issues en sprint activo
```bash
python jira_viewer.py --jql "assignee = currentUser() AND sprint in openSprints()"
```

### Issues creados esta semana
```bash
python jira_viewer.py --jql "assignee = currentUser() AND created >= -1w"
```

### Issues por resolver (To Do, In Progress)
```bash
python jira_viewer.py --jql "assignee = currentUser() AND status in ('To Do', 'In Progress')"
```

## Ejemplos de Automatización

### Script de reporte diario (Windows)
```batch
@echo off
cd /d "C:\Temp\VibeCoding"
python jira_viewer.py --all --export csv --output "reporte_diario.csv"
python jira_viewer.py --recent --days 1 --export csv --output "actualizaciones_hoy.csv"
```

### Script de reporte semanal (PowerShell)
```powershell
Set-Location "C:\Temp\VibeCoding"
$fecha = Get-Date -Format "yyyy-MM-dd"
python jira_viewer.py --recent --days 7 --export csv --output "reporte_semanal_$fecha.csv"
```

## Formatos de Tabla

### Tabla simple
```bash
python jira_viewer.py --all --format simple
```

### Tabla con bordes
```bash
python jira_viewer.py --all --format grid
```

### Tabla plana
```bash
python jira_viewer.py --all --format plain
```

## Consultas JQL Avanzadas

### Issues asignados a mí en proyectos específicos
```bash
python jira_viewer.py --jql "assignee = currentUser() AND project in (PROJ1, PROJ2, PROJ3)"
```

### Issues actualizados por otros en la última semana
```bash
python jira_viewer.py --jql "assignee = currentUser() AND updated >= -1w AND updatedBy != currentUser()"
```

### Bugs de alta prioridad
```bash
python jira_viewer.py --jql "assignee = currentUser() AND issuetype = Bug AND priority in (High, Highest)"
```

### Issues con comentarios recientes
```bash
python jira_viewer.py --jql "assignee = currentUser() AND comment ~ 'comentario' AND updated >= -3d"
```

## Integración con Otras Herramientas

### Enviar por email (con PowerShell)
```powershell
python jira_viewer.py --all --export csv --output "reporte.csv"
Send-MailMessage -To "manager@empresa.com" -Subject "Reporte Jira" -Body "Adjunto reporte" -Attachments "reporte.csv" -SmtpServer "smtp.empresa.com"
```

### Subir a SharePoint/OneDrive
```powershell
python jira_viewer.py --all --export json --output "reporte.json"
# Usar comandos de SharePoint Online PowerShell para subir
```

## Tips y Trucos

### Ver solo campos específicos
Edita `config.json` para personalizar qué campos mostrar:
```json
{
  "fields": ["key", "summary", "status", "assignee", "updated"]
}
```

### Filtros rápidos con alias (PowerShell)
```powershell
# Agregar al perfil de PowerShell
function jira-mis-issues { python jira_viewer.py --all }
function jira-en-progreso { python jira_viewer.py --status "In Progress" }
function jira-alta-prioridad { python jira_viewer.py --jql "assignee = currentUser() AND priority = High" }
```

### Programar ejecución automática
```powershell
# Crear tarea programada en Windows
$action = New-ScheduledTaskAction -Execute "python" -Argument "jira_viewer.py --all --export csv --output daily_report.csv" -WorkingDirectory "C:\Temp\VibeCoding"
$trigger = New-ScheduledTaskTrigger -Daily -At "09:00"
Register-ScheduledTask -TaskName "JiraReporteDiario" -Action $action -Trigger $trigger
```

## Solución de Problemas Comunes

### Error de autenticación
```bash
# Verificar credenciales
python jira_viewer.py --test

# Regenerar token en Atlassian
# https://id.atlassian.com/manage-profile/security/api-tokens
```

### Issues sin mostrar
```bash
# Verificar permisos del proyecto
python jira_viewer.py --jql "project = PROJ"

# Verificar si existe el estado
python jira_viewer.py --jql "status = 'Estado Inexistente'"
```

### Límites de rate
```bash
# Reducir número de resultados
python jira_viewer.py --jql "assignee = currentUser()" | head -50
```