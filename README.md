# 📊 Visualizador de Asignaciones Jira - Versión Refactorizada

Una aplicación web elegante y completa para visualizar y gestionar tus asignaciones de Jira con interfaz Streamlit, análisis avanzado y test unitarios.

## 🚀 Características Principales

### 🖥️ Interfaz Web Elegante (Streamlit)
- **Dashboard Interactivo**: Métricas en tiempo real, gráficos dinámicos
- **Lista de Issues**: Tabla filtrable y exportable
- **Análisis Avanzado**: Gráficos temporales, distribuciones, tendencias
- **Exportación**: CSV y JSON con un clic

### 🔧 Arquitectura Robusta
- **Código Refactorizado**: Separación clara de responsabilidades
- **Test Unitarios**: Cobertura completa con pytest
- **Configuración Centralizada**: Gestión limpia de settings
- **Logging Avanzado**: Trazabilidad completa de operaciones

### 📊 Análisis Inteligente
- **Distribuciones**: Por estado, prioridad, proyecto
- **Timeline**: Tendencias de actualizaciones
- **Filtros Avanzados**: Múltiples criterios simultáneos
- **JQL Personalizado**: Consultas flexibles

## 📁 Estructura del Proyecto

```
📦 VibeCoding/
├── 📱 app.py                    # Aplicación Streamlit principal
├── 🖥️ jira_viewer.py           # CLI original (mantenida)
├── 📋 requirements.txt         # Dependencias
├── ⚙️ pytest.ini              # Configuración de tests
├── 🛠️ Makefile                # Comandos automatizados
├── 📂 src/                     # Código fuente refactorizado
│   ├── 🔗 jira_client.py       # Cliente API Jira
│   ├── 📊 data_processor.py    # Procesamiento de datos
│   ├── ⚙️ config.py           # Configuración centralizada
│   ├── 🛠️ utils.py            # Utilidades comunes
│   └── 📦 __init__.py         # Paquete Python
├── 🧪 tests/                  # Test unitarios
│   ├── 🧪 test_jira_client.py  # Tests cliente Jira
│   ├── 📊 test_data_processor.py # Tests procesador
│   ├── ⚙️ test_config.py       # Tests configuración
│   ├── 🛠️ test_utils.py        # Tests utilidades
│   ├── 🔧 conftest.py         # Fixtures pytest
│   └── 📦 __init__.py         # Paquete tests
└── 📚 docs/                   # Documentación
    ├── 📖 README_WEB.md        # Guía interfaz web
    ├── 🧪 TESTING.md          # Guía de testing
    └── 🚀 DEPLOYMENT.md       # Guía de despliegue
```

## 🛠️ Instalación Rápida

### Opción 1: Instalación Automática
```bash
# Usando Makefile (recomendado)
make setup
```

### Opción 2: Instalación Manual
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar credenciales
cp .env.example .env
# Editar .env con tus credenciales de Jira

# 3. Verificar instalación
make test
```

## 🔧 Configuración

### 1. Credenciales de Jira
Edita el archivo `.env`:
```env
JIRA_BASE_URL=https://tu-instancia.atlassian.net
JIRA_EMAIL=tu-email@empresa.com
JIRA_TOKEN=tu_token_de_api
```

### 2. Generar Token de API
1. Ve a [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Crear token de API
3. Copia el token al archivo `.env`

## 🚀 Uso

### 🖥️ Interfaz Web (Recomendado)
```bash
# Iniciar aplicación Streamlit
make run
# o
streamlit run app.py
```

La aplicación estará disponible en: `http://localhost:8501`

### 🖥️ Interfaz CLI (Clásica)
```bash
# Ver todas las asignaciones
make run-cli
# o
python jira_viewer.py --all

# Filtros específicos
python jira_viewer.py --status "EN CURSO"
python jira_viewer.py --recent --days 7
python jira_viewer.py --export csv
```

## 📊 Características de la Interfaz Web

### 🏠 Dashboard Principal
- **Métricas Clave**: Total issues, en progreso, alta prioridad
- **Gráficos Interactivos**: Distribuciones por estado y prioridad
- **Timeline**: Tendencia de actualizaciones (30 días)
- **Actualización en Tiempo Real**

### 📋 Lista de Issues
- **Tabla Interactiva**: Sorteable y filtrable
- **Filtros Múltiples**: Estado, proyecto, prioridad
- **Búsqueda Avanzada**: JQL personalizado
- **Vista Detallada**: Información completa por issue

### 📊 Análisis Avanzado
- **Análisis Temporal**: Tendencias y patrones
- **Distribuciones**: Por proyecto, estado, prioridad
- **Media Móvil**: Suavizado de tendencias
- **Estadísticas**: Promedios, máximos, días activos

### 💾 Exportación
- **Formato CSV**: Para análisis en Excel/Sheets
- **Formato JSON**: Para integración con otras herramientas
- **Descarga Directa**: Sin necesidad de archivos locales
- **Nomenclatura Inteligente**: Timestamps automáticos

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

## 🎯 Consultas JQL Predefinidas

### 📝 Consultas Rápidas
- **Mis Issues**: `assignee = currentUser()`
- **En Progreso**: `status IN ('EN CURSO', 'ESCALADO')`
- **Pendientes**: `status IN ('NUEVA', 'ANÁLISIS')`
- **Alta Prioridad**: `priority IN ('Alto', 'Crítico')`
- **Actualizados Hoy**: `updated >= -1d`
- **Con Vencimiento**: `duedate < now()`

### 🔧 JQL Personalizado
Usar la barra lateral para consultas avanzadas:
```jql
project = MYPROJ AND assignee = currentUser() AND status = "In Progress"
```

## 🚀 Despliegue

### 🐳 Docker (Próximamente)
```dockerfile
# Configuración preparada para contenedores
FROM python:3.9-slim
COPY . /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py"]
```

### ☁️ Cloud Deploy
- **Streamlit Cloud**: Deploy directo desde GitHub
- **Heroku**: Con Procfile incluido
- **AWS/Azure**: Configuración para containers

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

## 📞 Soporte

### 📧 Contacto
- **Desarrollador**: Jesus Pedro Rodriguez
- **Email**: jesuspedro.rodriguez@unir.net
- **Repositorio**: [GitHub VibeCoding](https://github.com/jesusprodriguezUnir/VibeCoding)

### 📚 Recursos
- [Documentación Jira API](https://developer.atlassian.com/cloud/jira/platform/rest/)
- [Guía JQL](https://support.atlassian.com/jira-software-cloud/docs/advanced-searching/)
- [Streamlit Docs](https://docs.streamlit.io/)

---

**¡Disfruta gestionando tus asignaciones de Jira de forma elegante y eficiente! 🚀**