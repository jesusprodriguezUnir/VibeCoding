# 📊 VibeCoding - Visualizador de Asignaciones Jira

Una aplicación web moderna y completa para visualizar y gestionar tus asignaciones de Jira con interfaz Streamlit, análisis avanzado, dashboards personalizables y arquitectura modular.

## ⚡ Guía de Inicio Rápido

### 🚀 Para Empezar en 5 Minutos

1. **Clonar y preparar**:
   ```bash
   git clone https://github.com/jesusprodriguezUnir/VibeCoding.git
   cd VibeCoding
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows
   pip install -r requirements.txt
   ```

2. **Configurar Jira**:
   ```bash
   # Crear archivo .env con tus credenciales:
   JIRA_BASE_URL=https://tu-instancia.atlassian.net
   JIRA_EMAIL=tu-email@empresa.com
   JIRA_TOKEN=tu_token_de_api
   ```

3. **Ejecutar aplicación**:
   ```bash
   .\.venv\Scripts\streamlit.exe run app.py --server.port 8508
   ```

4. **Abrir navegador**: http://localhost:8508

### 📱 Apps de Ejemplo Desplegadas
- **Demo Live**: https://vibecoding-demo.streamlit.app *(próximamente)*
- **Documentación**: Consulta `GUIA_DESPLIEGUE_STREAMLIT.md` para deploy completo

---

### 🖥️ Interfaz Web Elegante (Streamlit)
- **Dashboard Interactivo**: Métricas en tiempo real, gráficos dinámicos
- **Dashboards Personalizables**: Vista Ejecutiva, Mi Trabajo, Vista de Proyecto
- **Widgets Configurables**: Métricas, gráficos, tablas y análisis tipo Jira
- **Lista de Issues**: Tabla filtrable y exportable
- **Análisis Avanzado**: Timeline, burndown, heatmaps, targets semanales
- **Exportación**: CSV, JSON y Excel con un clic

### 🏗️ Arquitectura Modular Refactorizada
- **Estructura por Características**: Organización clara por funcionalidades
- **Core Modules**: Cliente Jira, configuración, estado y procesamiento de datos
- **Features**: Dashboards, JQL, análisis e issues como módulos independientes
- **Shared Components**: UI reutilizable y utilidades comunes
- **Tools & Scripts**: Diagnósticos, testing y setup automatizado
- **Test Unitarios**: Cobertura completa con pytest

### 📊 Análisis Inteligente
- **Distribuciones**: Por estado, prioridad, proyecto, asignado
- **Timeline**: Tendencias de actualizaciones y progreso
- **Burndown Charts**: Seguimiento de sprints y objetivos
- **Activity Heatmaps**: Patrones de actividad temporal
- **Weekly Targets**: Objetivos y métricas semanales
- **Filtros Avanzados**: Múltiples criterios simultáneos
- **JQL Personalizado**: Consultas flexibles con biblioteca predefinida

## 📁 Estructura del Proyecto Refactorizada

```
📦 VibeCoding/
├── 📱 app.py                      # Aplicación Streamlit principal
├── 📋 requirements.txt           # Dependencias Python
├── ⚙️ pytest.ini                # Configuración de tests
├── 🛠️ Makefile                  # Comandos automatizados
├── � .gitignore                 # Archivos ignorados por Git
├── 🔧 .streamlit/               # Configuración Streamlit
│   ├── ⚙️ config.toml           # Config producción
│   └── 🔑 secrets.toml.example  # Plantilla secrets
├── 🎯 core/                     # Módulos centrales
│   ├── 🔗 jira_client.py        # Cliente API Jira
│   ├── 📊 data_processor.py     # Procesamiento de datos
│   ├── ⚙️ config.py            # Configuración centralizada
│   └── 🏠 app_state.py         # Estado de la aplicación
├── 🎨 features/                 # Funcionalidades por módulos
│   ├── 📊 dashboards/          # Dashboards personalizables
│   │   ├── 🎛️ custom.py        # Dashboard customizable
│   │   └── 📈 widgets.py       # Widgets tipo Jira
│   ├── 🔍 jql/                 # Gestión de consultas JQL
│   │   └── 📝 queries.py       # Consultas predefinidas
│   ├── 📊 analysis/            # Análisis avanzado
│   │   └── 📋 reports.py       # Reportes y análisis
│   └── 📋 issues/              # Gestión de issues
│       └── 👁️ viewer.py        # Visualizador de issues
├── 🔄 shared/                   # Componentes compartidos
│   ├── 📊 data_fetcher.py       # Fetcher de datos compartido
│   ├── 🛠️ utils.py             # Utilidades comunes
│   └── 🎨 ui/                  # Componentes UI reutilizables
│       ├── 🏠 layout.py        # Layouts principales
│       ├── 📊 dashboard.py     # Dashboard base
│       ├── 🎯 sidebar.py       # Barra lateral
│       └── 🧩 ui_utils.py      # Utilidades UI
├── 🛠️ tools/                   # Herramientas y scripts
│   ├── 🩺 diagnostics/         # Scripts de diagnóstico
│   ├── 🧪 testing/             # Herramientas de testing
│   └── ⚙️ setup/              # Scripts de configuración
├── 🧪 tests/                   # Test unitarios
│   ├── 🧪 test_jira_client.py  # Tests cliente Jira
│   ├── 📊 test_data_processor.py # Tests procesador
│   ├── ⚙️ test_config.py       # Tests configuración
│   ├── 🛠️ test_utils.py        # Tests utilidades
│   ├── 🔧 conftest.py         # Fixtures pytest
│   └── 📦 __init__.py         # Paquete tests
└── 📚 docs/                    # Documentación
    ├── � user/               # Documentación de usuario
    ├── 🔧 dev/                # Documentación de desarrollo
    └── � history/            # Historial de cambios
```

## 🛠️ Instalación y Configuración

### 📋 Requisitos Previos
- **Python 3.9+** (recomendado 3.11+)
- **Git** para clonar el repositorio
- **Credenciales Jira** (URL, email, token API)

### 🚀 Instalación Rápida

#### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/jesusprodriguezUnir/VibeCoding.git
cd VibeCoding
```

#### Paso 2: Crear Entorno Virtual
```bash
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Windows CMD
python -m venv .venv
.venv\Scripts\activate.bat

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

#### Paso 3: Instalar Dependencias
```bash
# Instalación completa
pip install -r requirements.txt

# Verificar instalación
python -c "import streamlit; print('✅ Streamlit instalado correctamente')"
```

#### Paso 4: Configurar Credenciales Jira

##### Opción A: Variables de Entorno (Desarrollo)
```bash
# Crear archivo .env
cp .env.example .env

# Editar .env con tus credenciales:
JIRA_BASE_URL=https://tu-instancia.atlassian.net
JIRA_EMAIL=tu-email@empresa.com
JIRA_TOKEN=tu_token_de_api
```

##### Opción B: Streamlit Secrets (Producción)
```bash
# Crear archivo de secrets local
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Editar .streamlit/secrets.toml:
[jira]
base_url = "https://tu-instancia.atlassian.net"
email = "tu-email@empresa.com"
token = "tu_token_de_api"
```

### 🔑 Obtener Token de API de Jira

1. **Acceder a tu perfil**: Ve a `https://id.atlassian.com/manage-profile/security/api-tokens`
2. **Crear token**: Haz clic en "Create API token"
3. **Copiar token**: Guarda el token generado (solo se muestra una vez)
4. **Configurar**: Añade el token al archivo `.env` o `secrets.toml`

## 🚀 Cómo Ejecutar la Aplicación

### 🎯 Método Recomendado: Scripts Automáticos

#### Windows PowerShell
```powershell
# Método más fácil - usar script automático
.\start_app.ps1

# O ejecutar paso a paso:
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\streamlit.exe run app.py --server.port 8508
```

#### Windows CMD
```cmd
# Usar script batch
start_app.bat

# O ejecutar manualmente:
.venv\Scripts\activate.bat
.venv\Scripts\streamlit.exe run app.py --server.port 8508
```

#### Linux/Mac
```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar aplicación
streamlit run app.py --server.port 8508
```

### 🔧 Método Manual Paso a Paso

1. **Abrir terminal** en el directorio del proyecto
2. **Navegar al directorio**:
   ```bash
   cd C:\Temp\VibeCoding
   ```

3. **Activar entorno virtual**:
   ```powershell
   # PowerShell
   .\.venv\Scripts\Activate.ps1
   ```

4. **Verificar instalación**:
   ```bash
   python --version  # Debe mostrar Python 3.9+
   streamlit --version  # Debe mostrar Streamlit instalado
   ```

5. **Ejecutar aplicación**:
   ```bash
   # Usando ruta completa (más confiable)
   .\.venv\Scripts\streamlit.exe run app.py --server.port 8508
   
   # O con comando directo (si PATH está configurado)
   streamlit run app.py --server.port 8508
   ```

6. **Acceder a la aplicación**:
   - **URL Local**: http://localhost:8508
   - **URL de Red**: http://tu-ip-local:8508

### �️ Solución de Problemas Comunes

#### ❌ Error: "streamlit no se reconoce"
```bash
# Usar ruta completa al ejecutable
.\.venv\Scripts\streamlit.exe run app.py --server.port 8508
```

#### ❌ Error: "ModuleNotFoundError"
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

#### ❌ Error: "No se puede conectar a Jira"
```bash
# Verificar credenciales
python -c "from core.config import Config; config = Config.get_jira_config(); print('✅ Config OK')"
```

#### ❌ Error: "Puerto en uso"
```bash
# Usar puerto diferente
streamlit run app.py --server.port 8509
```

### 📱 Acceso a la Aplicación

Una vez ejecutada la aplicación:

1. **Se abrirá automáticamente** en tu navegador predeterminado
2. **URL principal**: http://localhost:8508
3. **URLs adicionales**:
   - Red local: http://[tu-ip]:8508
   - Externa: http://[ip-externa]:8508 (si está configurada)

### 🎛️ Configuración Avanzada

#### Puerto Personalizado
```bash
streamlit run app.py --server.port 9000
```

#### Configuración de Producción
```bash
streamlit run app.py --server.headless true --server.enableCORS false
```

#### Debug Mode
```bash
# Activar logging detallado
set LOG_LEVEL=DEBUG
streamlit run app.py --logger.level debug
```

## 🎯 Comandos Rápidos de Referencia

### 📋 Comandos Esenciales
```bash
# Iniciar aplicación (método recomendado)
python run_app.py                    # Script con verificaciones automáticas
.\start_app.ps1                      # PowerShell con diagnósticos

# Iniciar aplicación (método manual)
.\.venv\Scripts\streamlit.exe run app.py --server.port 8508

# Verificar estado
python --version                     # Verificar Python
.\.venv\Scripts\pip.exe list        # Ver dependencias instaladas
python -c "import streamlit; print(streamlit.__version__)"  # Ver versión Streamlit
```

### 🔧 Comandos de Diagnóstico
```bash
# Test de conexión Jira
python -c "from core.jira_client import JiraClient; client = JiraClient(); print(client.test_connection())"

# Verificar configuración
python -c "from core.config import Config; Config.get_jira_config(); print('✅ Config válida')"

# Test completo del sistema
python run_app.py                    # Ejecuta todas las verificaciones
```

### 🚨 Solución de Problemas Rápida
```bash
# Reinstalar dependencias
.\.venv\Scripts\pip.exe install -r requirements.txt --force-reinstall

# Recrear entorno virtual
Remove-Item .venv -Recurse -Force   # PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Verificar puertos
netstat -an | findstr :8508         # Ver si puerto está en uso
```

## 📊 Características de la Interfaz Web

### 🏠 Dashboard Principal
- **Métricas Clave**: Total issues, en progreso, alta prioridad, vencidos
- **Tiempo de Resolución**: Promedios y tendencias
- **Gráficos Interactivos**: Distribuciones por estado, prioridad y asignado
- **Timeline de Actualizaciones**: Tendencia de los últimos 30 días
- **Carga de Trabajo**: Distribución por asignado y proyecto
- **Actualización en Tiempo Real**: Datos frescos cada consulta

### 🎛️ Dashboards Personalizables

#### Vista Ejecutiva
- **Métricas Ejecutivas**: KPIs principales y resumen general
- **Análisis de Rendimiento**: Tiempo de resolución y eficiencia
- **Distribución de Carga**: Workload por equipos y proyectos
- **Tendencias Estratégicas**: Evolución a largo plazo

#### Mi Trabajo
- **Mis Asignaciones**: Issues personales y estado actual
- **Sprint Actual**: Progreso del sprint en curso
- **Objetivos Semanales**: Metas y seguimiento personal
- **Actividad Reciente**: Últimas actualizaciones y cambios

#### Vista de Proyecto
- **Progreso del Proyecto**: Estado general y milestones
- **Issues Bloqueados**: Impedimentos y resolución
- **Burndown Chart**: Seguimiento de sprint y release
- **Actividad del Equipo**: Heatmap de actividad temporal

### 📋 Lista de Issues Avanzada
- **Tabla Interactiva**: Sorteable, filtrable y con paginación
- **Filtros Múltiples**: Estado, proyecto, prioridad, asignado
- **Búsqueda Global**: Texto libre en summary y description
- **JQL Personalizado**: Consultas avanzadas con biblioteca predefinida
- **Vista Detallada**: Modal con información completa por issue
- **Acciones Rápidas**: Links directos a Jira para edición

### 📊 Análisis Avanzado y Reportes
- **Análisis Temporal**: Tendencias por período configurable
- **Distribuciones Dinámicas**: Por cualquier campo de Jira
- **Burndown Charts**: Seguimiento de sprints y objetivos
- **Activity Heatmaps**: Patrones de actividad por hora/día
- **Métricas de Velocidad**: Throughput y cycle time
- **Comparativas**: Períodos anteriores y benchmarks
- **Weekly Targets**: Objetivos semanales y seguimiento

### 💾 Exportación y Descarga
- **Múltiples Formatos**: CSV, JSON y Excel (.xlsx)
- **Filtros Aplicados**: Exporta solo datos visibles/filtrados
- **Nomenclatura Inteligente**: Timestamps automáticos en nombres
- **Descarga Directa**: Sin archivos temporales en servidor
- **Metadata Incluida**: Información de consulta y timestamp

### 🔍 Consultas JQL Mejoradas
- **Biblioteca Predefinida**: 15+ consultas listas para usar
- **Editor JQL**: Sintaxis highlighting y validación
- **Historial de Consultas**: Últimas 10 consultas ejecutadas
- **Favoritos**: Guardar consultas frecuentes
- **Ejemplos Integrados**: Plantillas para casos comunes
- **Validación en Tiempo Real**: Verificación de sintaxis

### 🎨 Widgets Tipo Jira
- **Widgets de Métricas**: Contadores animados y KPIs
- **Gráficos Dinámicos**: Charts interactivos con drill-down
- **Tablas Configurables**: Columns y filtros personalizables
- **Timeline Components**: Líneas de tiempo y cronologías
- **Progress Bars**: Barras de progreso y completion rates
- **Alert Widgets**: Notificaciones y destacados importantes

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
make test

# Solo tests unitarios
make test-unit

# Tests con cobertura
make test-cov

# Tests específicos
pytest tests/test_jira_client.py -v
```

### Cobertura de Tests
- ✅ **JiraClient**: Conexión, búsquedas, manejo de errores
- ✅ **DataProcessor**: Formateo, análisis, exportación
- ✅ **Config**: Configuración, validación
- ✅ **Utils**: Utilidades, validación de archivos

### Métricas Objetivo
- **Cobertura**: >80% (configurado en pytest.ini)
- **Tests**: >50 test cases
- **Mocking**: APIs externas mockeadas

## 🔧 Desarrollo

### Comandos Útiles
```bash
# Verificar código
make lint

# Formatear código
make format

# Verificación completa
make check

# Limpiar archivos temporales
make clean
```

### Estructura de Clases

#### 🔗 JiraClient
```python
class JiraClient:
    def test_connection() -> Dict[str, Any]
    def search_issues(jql: str) -> Dict[str, Any]
    def get_my_issues() -> Dict[str, Any]
    def get_recent_issues() -> Dict[str, Any]
```

#### 📊 JiraDataProcessor
```python
class JiraDataProcessor:
    def format_issues_for_display() -> pd.DataFrame
    def get_status_summary() -> Dict[str, int]
    def get_timeline_data() -> Dict[str, List]
    def export_to_csv() -> bool
```

## 🎯 Consultas JQL Predefinidas y Personalizadas

### 📝 Biblioteca de Consultas Rápidas
```jql
# Trabajo Personal
"Mis Issues": "assignee = currentUser() ORDER BY updated DESC"
"En Progreso": "assignee = currentUser() AND status IN ('EN CURSO', 'In Progress', 'ESCALADO')"
"Pendientes": "assignee = currentUser() AND status IN ('NUEVA', 'To Do', 'ANÁLISIS')"
"Completados": "assignee = currentUser() AND status IN ('CERRADA', 'Done', 'RESUELTA')"

# Por Prioridad
"Alta Prioridad": "assignee = currentUser() AND priority IN ('High', 'Highest', 'Alto', 'Crítico')"
"Issues Críticos": "priority in (Highest, Crítico) AND status != RESUELTA"

# Por Tiempo
"Actualizados Hoy": "assignee = currentUser() AND updated >= -1d ORDER BY updated DESC"
"Actualizados Esta Semana": "assignee = currentUser() AND updated >= -1w ORDER BY updated DESC"
"Sin Actualizar (7 días)": "assignee = currentUser() AND updated <= -7d AND status != RESUELTA"

# Fechas de Vencimiento
"Con Fecha Vencida": "assignee = currentUser() AND duedate < now() AND status NOT IN ('CERRADA', 'Done', 'RESUELTA')"
"Vencen Esta Semana": "assignee = currentUser() AND duedate >= now() AND duedate <= 7d"

# Estados Especiales
"Issues Bloqueados": "status = BLOQUEADA OR labels = blocked"
"Sin Asignar": "assignee is EMPTY AND statusCategory != done"
"Escalaciones": "issueLinkType in ('is an escalation for') AND statusCategory != done"
```

### 🔧 JQL Personalizado Avanzado
```jql
# Filtros por Proyecto
project = MYPROJ AND assignee = currentUser() AND status = "In Progress"

# Búsquedas Textuales
summary ~ "bug" OR description ~ "error" AND assignee = currentUser()

# Filtros Temporales Complejos
created >= startOfWeek() AND updated >= -3d AND priority = High

# Combinaciones Avanzadas
(priority = Highest OR labels = urgent) AND status NOT IN (Done, Closed) AND assignee in (currentUser(), "team-lead")
```

### 📚 Guías JQL Integradas
- **Sintaxis Básica**: Campos, operadores y funciones
- **Filtros Temporales**: Fechas relativas y absolutas
- **Búsquedas de Texto**: Wildcards y operadores especiales
- **Funciones Avanzadas**: currentUser(), startOfDay(), etc.
- **Combinaciones**: AND, OR, NOT y agrupaciones
- **Validación**: Verificación de sintaxis en tiempo real

## 🚀 Despliegue y Producción

### ☁️ Streamlit Cloud (Recomendado)

#### � Preparación para Deploy
```bash
# 1. Verificar que todo funciona localmente
streamlit run app.py --server.port 8508

# 2. Commit y push a GitHub
git add .
git commit -m "Preparación para deploy"
git push origin main
```

#### 🌐 Deploy en Streamlit Cloud
1. **Conectar con GitHub**: Ve a [share.streamlit.io](https://share.streamlit.io)
2. **New App**: Selecciona tu repositorio `VibeCoding`
3. **Configuración**:
   - **Repository**: `jesusprodriguezUnir/VibeCoding`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: `tu-nombre-app.streamlit.app`

#### 🔑 Configurar Secrets en Streamlit Cloud
En **Advanced Settings > Secrets**, añadir:
```toml
[jira]
base_url = "https://tu-instancia.atlassian.net"
email = "tu-email@empresa.com"
token = "tu_api_token_aqui"
```

#### ✅ URLs de la App Desplegada
- **Aplicación**: `https://tu-nombre-app.streamlit.app`
- **Gestión**: [share.streamlit.io](https://share.streamlit.io) → Manage app
- **Logs**: Desde panel de gestión → Logs tab

### 🐳 Otros Métodos de Deploy

#### Heroku
```bash
# Crear Procfile
echo "web: streamlit run app.py --server.port \$PORT --server.headless true" > Procfile

# Deploy con Heroku CLI
heroku create tu-app-name
git push heroku main
```

#### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 🔧 Configuración de Producción
- **Variables de Entorno**: Soporte dual .env y Streamlit secrets
- **Logging**: Nivel WARNING en producción
- **Cache**: Optimizado para 1000+ issues
- **Rendimiento**: Lazy loading y paginación automática
- **Seguridad**: Secrets protegidos, no hay credenciales en código

## 🔒 Seguridad

### 🛡️ Buenas Prácticas
- ✅ **Tokens en .env**: Nunca en código
- ✅ **Gitignore**: Credenciales protegidas
- ✅ **HTTPS**: Conexiones seguras
- ✅ **Logging**: Trazabilidad sin exponer secrets

### 🔐 Gestión de Credenciales
- **Rotación Periódica**: Cambiar tokens cada 90 días
- **Permisos Mínimos**: Solo acceso necesario
- **Variables de Entorno**: Configuración externa

## 📈 Roadmap

### 🔜 Próximas Funcionalidades
- [ ] **Dashboard Personalizable**: Widgets configurables
- [ ] **Notificaciones**: Alertas por email/Slack
- [ ] **Reportes Programados**: Automatización
- [ ] **Múltiples Instancias**: Soporte multi-Jira
- [ ] **API REST**: Endpoint propio
- [ ] **Modo Offline**: Cache local

### 🎨 Mejoras UX
- [ ] **Temas**: Dark/Light mode
- [ ] **Responsive**: Mobile-friendly
- [ ] **PWA**: Instalable como app
- [ ] **Búsqueda Global**: Filtro unificado

## 🤝 Contribución

### 📝 Guidelines
1. **Fork** el repositorio
2. **Crear** feature branch
3. **Escribir** tests para nuevas funcionalidades
4. **Ejecutar** `make check` antes del commit
5. **Documentar** cambios en README

### 🧪 Test Guidelines
```python
# Nuevo test ejemplo
def test_nueva_funcionalidad():
    # Arrange
    client = JiraClient()
    
    # Act
    result = client.nueva_funcionalidad()
    
    # Assert
    assert result['success'] is True
```

## 🆘 Solución de Problemas

### ❌ Errores Comunes

#### Error de Conexión
```
❌ Error de conexión: 401 Unauthorized
```
**Solución**: Verificar token de API y email en `.env`

#### Error de JQL
```
❌ Error en búsqueda: Invalid JQL
```
**Solución**: Validar sintaxis JQL en Jira web primero

#### Error de Dependencias
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solución**: `make install` o `pip install -r requirements.txt`

### 🔧 Debug Mode
```bash
# Activar logging detallado
export LOG_LEVEL=DEBUG
streamlit run app.py
```

## 📞 Soporte y Contacto

### 📧 Información de Contacto
- **Desarrollador**: Jesus Pedro Rodriguez
- **Email**: jesuspedro.rodriguez@unir.net
- **Repositorio**: [GitHub VibeCoding](https://github.com/jesusprodriguezUnir/VibeCoding)
- **Issues**: [GitHub Issues](https://github.com/jesusprodriguezUnir/VibeCoding/issues)

### 📚 Documentación y Recursos
- **Guía de Despliegue**: `GUIA_DESPLIEGUE_STREAMLIT.md`
- **Guía JQL**: `GUIA_JQL_PERSONALIZADA.md`
- **Documentación API Jira**: [Atlassian Developer](https://developer.atlassian.com/cloud/jira/platform/rest/)
- **Guía JQL Oficial**: [Atlassian JQL Guide](https://support.atlassian.com/jira-software-cloud/docs/advanced-searching/)
- **Streamlit Docs**: [Streamlit Documentation](https://docs.streamlit.io/)

### 🆘 Resolución Rápida de Problemas

#### ❌ Error de Conexión Jira
```bash
# Verificar credenciales
python -c "from core.config import Config; Config.get_jira_config()"
```
**Solución**: Verificar token API, email y URL en `.env` o secrets

#### ❌ Error "streamlit no se reconoce"
```bash
# Usar ruta completa
.\.venv\Scripts\streamlit.exe run app.py --server.port 8508
```

#### ❌ Error "ModuleNotFoundError"
```bash
# Reinstalar dependencias en entorno virtual
.\.venv\Scripts\pip.exe install -r requirements.txt --force-reinstall
```

#### ❌ Error de Puerto en Uso
```bash
# Usar puerto diferente
streamlit run app.py --server.port 8509
```

### 🔧 Comandos de Diagnóstico
```bash
# Verificar Python y entorno
python --version
pip list | grep streamlit

# Test de conexión Jira
python -c "from core.jira_client import JiraClient; client = JiraClient(); print(client.test_connection())"

# Verificar configuración
python -c "from core.config import Config; print('✅ Config OK')"
```

---

## 📈 Roadmap y Próximas Funcionalidades

### 🔜 Versión 2.0 (En Desarrollo)
- [ ] **Dashboard Personalizable Completo**: Drag & drop widgets
- [ ] **Notificaciones Push**: Alertas por email/Slack/Teams
- [ ] **Reportes Programados**: Generación automática diaria/semanal
- [ ] **Múltiples Instancias Jira**: Soporte multi-tenant
- [ ] **API REST Propia**: Endpoints para integración
- [ ] **Modo Offline**: Cache persistente local

### 🎨 Mejoras UX/UI
- [ ] **Temas Avanzados**: Dark/Light mode con custom themes
- [ ] **Mobile Responsive**: Optimización completa para móviles
- [ ] **PWA Support**: Instalable como aplicación nativa
- [ ] **Búsqueda Global**: Filtro unificado cross-functional
- [ ] **Keyboard Shortcuts**: Navegación rápida por teclado
- [ ] **Tour Interactivo**: Onboarding guiado para nuevos usuarios

### 🔧 Funcionalidades Técnicas
- [ ] **GraphQL API**: Queries más eficientes
- [ ] **Real-time Sync**: WebSocket para updates en vivo
- [ ] **Plugin System**: Arquitectura de extensiones
- [ ] **Advanced Caching**: Redis/Memcached support
- [ ] **Monitoring**: Métricas de uso y performance
- [ ] **A/B Testing**: Framework de experimentación

---

**¡Gracias por usar VibeCoding! 🚀 Gestiona tus asignaciones de Jira de forma elegante y eficiente.**

*Última actualización: Octubre 2025 - Versión 1.5 (Arquitectura Modular)*