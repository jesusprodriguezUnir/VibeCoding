# Guía para Visualizar Asignaciones de Jira

## Configuración Inicial

### 1. Requisitos
- Python 3.7+
- Token de API de Jira (que proporcionarás más tarde)
- URL de tu instancia de Jira

### 2. Instalación de Dependencias
```bash
pip install requests pandas tabulate python-dotenv
```

### 3. Configuración del Token (Segura)

Crea un archivo `.env` en tu directorio de trabajo:
```
JIRA_TOKEN=tu_token_aqui
JIRA_BASE_URL=https://tu-instancia.atlassian.net
JIRA_EMAIL=tu_email@empresa.com
```

**IMPORTANTE**: Nunca subas el archivo `.env` a GitHub. Asegúrate de agregarlo a tu `.gitignore`:
```
# .gitignore
.env
*.env
```

## Uso del Script

### 1. Obtener Todas las Asignaciones
```python
python jira_viewer.py --all
```

### 2. Filtrar por Estado
```python
# Solo issues en progreso
python jira_viewer.py --status "In Progress"

# Solo issues abiertos
python jira_viewer.py --status "Open"
```

### 3. Filtrar por Proyecto
```python
python jira_viewer.py --project "PROJ"
```

### 4. Exportar a Archivo
```python
# Exportar a CSV
python jira_viewer.py --all --export csv

# Exportar a JSON
python jira_viewer.py --all --export json
```

## Funcionalidades Disponibles

### Información que se Muestra:
- **Key**: Clave del issue (ej: PROJ-123)
- **Summary**: Resumen del issue
- **Status**: Estado actual
- **Priority**: Prioridad
- **Assignee**: Persona asignada
- **Reporter**: Quien reportó el issue
- **Created**: Fecha de creación
- **Updated**: Última actualización
- **Project**: Proyecto al que pertenece
- **Issue Type**: Tipo de issue (Bug, Task, Story, etc.)

### Filtros Disponibles:
- Por estado
- Por proyecto
- Por tipo de issue
- Por prioridad
- Por fecha de creación/actualización

### Formatos de Salida:
- Tabla en consola (formato pretty)
- Exportación CSV
- Exportación JSON
- Exportación Excel (opcional)

## Comandos Útiles

### Ver Issues Asignados a Ti
```python
python jira_viewer.py --assigned-to-me
```

### Ver Issues por Sprint Activo
```python
python jira_viewer.py --active-sprint
```

### Ver Issues Actualizados Recientemente
```python
python jira_viewer.py --recent --days 7
```

### Búsqueda Personalizada con JQL
```python
python jira_viewer.py --jql "project = PROJ AND status = 'In Progress' AND assignee = currentUser()"
```

## Ejemplos de Consultas JQL Útiles

```sql
-- Mis issues en progreso
assignee = currentUser() AND status = "In Progress"

-- Issues creados esta semana
created >= -1w AND assignee = currentUser()

-- Issues de alta prioridad
assignee = currentUser() AND priority = High

-- Issues por resolver antes de cierta fecha
assignee = currentUser() AND duedate <= "2024-12-31"

-- Issues en sprint activo
assignee = currentUser() AND sprint in openSprints()
```

## Configuración Avanzada

### Personalizar Campos a Mostrar
Edita el archivo `config.json`:
```json
{
  "fields": [
    "key",
    "summary",
    "status",
    "priority",
    "assignee",
    "reporter",
    "created",
    "updated",
    "project",
    "issuetype",
    "duedate",
    "labels",
    "components"
  ],
  "max_results": 100,
  "default_jql": "assignee = currentUser() ORDER BY updated DESC"
}
```

## Solución de Problemas

### Error de Autenticación
- Verifica que tu token sea válido
- Asegúrate de que el email en `.env` sea correcto
- Confirma que la URL base sea la correcta

### Error de Permisos
- Verifica que tengas acceso a los proyectos que intentas consultar
- Algunos campos pueden requerir permisos especiales

### Límites de Rate
- El script incluye manejo automático de rate limiting
- Si tienes muchos issues, usa paginación

## Seguridad

### Mejores Prácticas:
1. **Nunca hardcodees el token en el código**
2. **Usa siempre archivos `.env` para credenciales**
3. **Agrega `.env` a tu `.gitignore`**
4. **Rota tu token periódicamente**
5. **Usa tokens con permisos mínimos necesarios**

### Generar Token de Jira:
1. Ve a tu perfil de Atlassian
2. Seguridad → Crear y administrar tokens de API
3. Crear token de API
4. Copia el token (solo se muestra una vez)

## Automatización

### Ejecución Programada (Windows Task Scheduler)
```batch
@echo off
cd /d "C:\Temp\VibeCoding"
python jira_viewer.py --all --export csv --output daily_report.csv
```

### Script de Reporte Diario
```python
python jira_viewer.py --assigned-to-me --recent --days 1 --export csv --output today_updates.csv
```

## Extensiones Futuras

### Ideas para Mejorar:
- Dashboard web con Flask/Streamlit
- Notificaciones por email
- Integración con calendario
- Métricas y analytics
- Exportación a PDF con gráficos
- Integración con Slack/Teams

---

*Recuerda: Este archivo contiene todas las instrucciones necesarias. El token se configurará de forma segura cuando esté listo.*