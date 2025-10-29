## Instrucciones rápidas para agentes de codificación (VibeCoding)

Este repositorio es una aplicación Streamlit para visualizar y analizar asignaciones de Jira.
Las instrucciones aquí están diseñadas para que un agente (Copilot/IA) sea productivo de inmediato.

- Contexto arquitectural breve:
  - `src/jira_client.py` — Cliente HTTP hacia la API de Jira. Métodos principales: `test_connection()`, `search_issues(...)`, `get_my_issues()`. Devuelve dicts con clave `success` y datos en `issues`/`error`.
  - `src/data_fetcher.py` — Orquesta la petición y pone resultados en `st.session_state` (usa `st.session_state.client`, `cached_issues`, `data_processor`).
  - `src/data_processor.py` — Convierte la respuesta de Jira en un `pd.DataFrame` y provee resúmenes/export (ej. `format_issues_for_display`, `get_timeline_data`).
  - `src/config.py` — Fuente de verdad para queries JQL predefinidas (`Config.PREDEFINED_QUERIES`), colores y campos por defecto. Leer antes de modificar lógica JQL.
  - `src/app_state.py` — Inicializa y valida `st.session_state`. Respeta las claves: `client`, `cached_issues`, `data_processor`, `jira_token`, `base_url`.
  - `src/ui/widgets.py` — **NUEVO**: Sistema de widgets configurables para dashboards personalizables. Incluye widgets tipo Jira: métricas, gráficos, burndown, sprint tracking.
  - `src/ui/dashboard_custom.py` — **NUEVO**: Configuración de paneles personalizables con 3 dashboards predefinidos: "Vista Ejecutiva", "Mi Trabajo", "Vista de Proyecto".

- Convenciones de código y patrones observables (síguelos):
  - API externa: los wrappers de red siempre devuelven dict con `success: bool` y campos adicionales. No arrojes excepciones HTTP sin envolverlas; propaga errores en el dict (`error` string) — mira `JiraClient.search_issues`.
  - Config desde entorno: credenciales se leen desde variables de entorno `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_TOKEN` (ver `Config.get_jira_config()` y `JiraClient.__init__`). No codifiques secrets.
  - Streamlit state: evita crear variables globales fuera de `st.session_state`. Usa `app_state.init_session_state()` para inicializar.
  - Paginated APIs: `JiraClient.search_issues` acepta `start_at`/`max_results`. Mantén paginación si añades endpoints que puedan devolver >100 issues.

- Flujo típico para cambios y pruebas:
  1. Actualizar/añadir código en `src/`.
  2. Ejecutar tests unitarios: `pytest -q` o `make test` (el repositorio incluye `pytest.ini` con cobertura exigida >=80%).
  3. Para la UI: usar `.\.venv\Scripts\Activate.ps1` y luego `.\.venv\Scripts\streamlit.exe run app.py` o ejecutar `start_app.ps1` / `start_app.bat`.

- Integración y dependencias importantes:
  - Dependencias listadas en `requirements.txt`: `streamlit`, `pandas`, `requests`, `python-dotenv`, `plotly`, `pytest`, etc.
  - El cliente Jira usa `requests` con `HTTPBasicAuth`. Usa `responses` o `pytest-mock` en tests para simular llamadas.

- Sugerencias concretas para PRs y modificaciones:
  - Si tocas JQL, añade/actualiza entradas en `Config.PREDEFINED_QUERIES` (ejemplo: "Mis Issues").
  - Para nuevos endpoints externos añade cobertura unitaria en `tests/` y mocks para `requests.Session` o usa `responses`.
  - Mantén el formato de retorno del cliente: `{ 'success': True/False, 'issues': [...], 'error': '...' }`.
  - Cambios de UI deben respetar `st.session_state` y no depender de variables globales temporales.

- Ejemplos rápidos (referencias a archivos):
  - Conectar a Jira (ver `src/app_state.py:create_jira_client` y `src/jira_client.py:test_connection`).
  - Formateo tabla: `JiraDataProcessor.format_issues_for_display(issues)` (ver `src/data_processor.py`).
  - **Widgets personalizables**: `widget_registry.register(Widget(...))` para crear nuevos widgets (ver `src/ui/widgets.py`).
  - **Dashboards personalizados**: `DashboardConfig` con lista de widget IDs y configuración de layout (ver `src/ui/dashboard_custom.py:render_dashboard_selector`).

- Widgets disponibles (tipo Jira):
  - **Métricas**: `total_issues`, `in_progress`, `high_priority`, `overdue`, `resolution_time`
  - **Gráficos**: `status_distribution`, `priority_distribution`, `assignee_workload`, `project_progress`
  - **Tablas**: `recent_issues`, `my_assignments`, `current_sprint`, `blocked_issues`
  - **Análisis**: `updates_timeline`, `burndown_chart`, `activity_heatmap`, `weekly_targets`

Si algún punto está incompleto o quieres que adapte el tono/formato, dime qué sección afinar y la actualizo.
