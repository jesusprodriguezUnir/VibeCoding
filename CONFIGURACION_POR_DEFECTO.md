# Configuración por Defecto - VibeCoding

## Valores por Defecto Configurados

### 🧭 Navegación Principal
- **Vista por defecto**: Lista de Issues
- **Orden de opciones**: Lista de Issues, Dashboard, Dashboard Personalizable, Análisis, Exportar Datos

### 🔍 Consultas JQL
- **Consulta por defecto**: Pendientes
- **Orden de opciones**: Pendientes, Mis Issues, En Progreso, Completados, Alta Prioridad, Actualizados Hoy, Actualizados Esta Semana, Con Fecha Vencida

### ⚙️ Configuración Técnica
- **Máximo de resultados por defecto**: 250 (configurable via JIRA_MAX_RESULTS_DEFAULT en .env)
- **Rango del slider**: 10 a 500 resultados
- **Recarga automática**: Activada cuando cambian los parámetros de consulta

### 📋 Experiencia de Usuario
- **Mensaje de bienvenida**: Se muestra una vez al cargar con configuración por defecto
- **Información contextual**: Banners informativos según el tipo de consulta seleccionada
- **Indicador de límites**: Avisos cuando se alcanza el máximo de resultados configurado

### 🚧 Consulta JQL para "Pendientes"
```jql
assignee = currentUser() AND status IN ('NUEVA', 'To Do', 'ANÁLISIS') ORDER BY updated DESC
```

### 💡 Flujo de Usuario Típico
1. **Al abrir la app**: Automáticamente muestra "Lista de Issues" con "Pendientes"
2. **Carga automática**: Los datos se obtienen con 250 resultados máximo
3. **Mensaje contextual**: Explica qué tipo de issues se están mostrando
4. **Interactividad**: Al cambiar filtros, se recargan automáticamente los datos

## Variables de Entorno Configurables

```env
# Configuración principal de Jira
JIRA_BASE_URL=https://tuinstancia.atlassian.net
JIRA_EMAIL=tu-email@ejemplo.com
JIRA_TOKEN=tu-token-de-api

# Configuración opcional
JIRA_MAX_RESULTS_DEFAULT=250  # Valor por defecto del slider
```

## Comandos Útiles

```bash
# Ejecutar la aplicación
.\.venv\Scripts\streamlit.exe run app.py

# Ejecutar en puerto específico
.\.venv\Scripts\streamlit.exe run app.py --server.port 8502

# Ejecutar tests
.\.venv\Scripts\python.exe -m pytest tests/ -v
```