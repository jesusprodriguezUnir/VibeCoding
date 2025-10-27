# 🎯 Guía de Uso Rápido - Visualizador Jira

## 🚀 Inicio Rápido (5 minutos)

### 1. ⚡ Instalación Express
```bash
# Clona o descarga el proyecto
git clone https://github.com/jesusprodriguezUnir/VibeCoding.git
cd VibeCoding

# Configuración automática
make setup
```

### 2. 🔐 Configurar Credenciales
Edita el archivo `.env`:
```env
JIRA_BASE_URL=https://unirgen.atlassian.net
JIRA_EMAIL=jesuspedro.rodriguez@unir.net
JIRA_TOKEN=ATATT3xFfGF08-ZBAEIZMxGYVjH3oLgKzonZtqiRnNmoZY1PfOtMRNxBP7fsUKtsVDskv1GkVkovHbFPYfVwcENdNz_BvzXD_uNA3b-PrjDVR5EAz1MZH2TvtDcU7z87NXPSwFhjC9vHSBiYgBYbZeHRg3UVPl-ZrpXBDJYzeHuND6Gxm0HgJv8=7B4BEF74
```

### 3. 🖥️ Lanzar Aplicación
```bash
# Interfaz web elegante
make run
# O directamente: streamlit run app.py

# Se abre en: http://localhost:8501
```

## 🎨 Funcionalidades Principales

### 📊 Dashboard Interactivo
- **Métricas en Tiempo Real**
  - Total de issues asignados
  - Issues en progreso
  - Issues de alta prioridad
  - Actualizaciones del día

- **Gráficos Dinámicos**
  - Distribución por estado (gráfico de torta)
  - Distribución por prioridad (gráfico de barras)
  - Timeline de actualizaciones (línea temporal)

### 📋 Lista de Issues Avanzada
- **Tabla Interactiva**
  - Sorteable por cualquier columna
  - Filtros múltiples simultáneos
  - Búsqueda en tiempo real

- **Filtros Inteligentes**
  - Por estado: NUEVA, EN CURSO, CERRADA, etc.
  - Por proyecto: BAUACA, STI, PR24VLN, etc.
  - Por prioridad: Crítico, Alto, Medio, Bajo

### 📈 Análisis Temporal
- **Tendencias de Actividad**
  - Gráfico de actualizaciones diarias
  - Media móvil de 7 días
  - Estadísticas del período

- **Métricas Calculadas**
  - Promedio de actualizaciones diarias
  - Día con mayor actividad
  - Días activos vs. totales

### 💾 Exportación Flexible
- **Formato CSV**: Para Excel/Google Sheets
- **Formato JSON**: Para desarrollo/APIs
- **Descarga Directa**: Sin archivos locales
- **Nombres Inteligentes**: Con timestamp automático

## 🔍 Consultas JQL Predefinidas

### 📝 Consultas Rápidas Disponibles
1. **Mis Issues**: Todos los issues asignados
2. **En Progreso**: Issues activos (EN CURSO, ESCALADO)
3. **Pendientes**: Issues por empezar (NUEVA, ANÁLISIS)
4. **Completados**: Issues finalizados (CERRADA, RESUELTA)
5. **Alta Prioridad**: Issues críticos y altos
6. **Actualizados Hoy**: Cambios del día actual
7. **Actualizados Esta Semana**: Actividad reciente
8. **Con Fecha Vencida**: Issues con deadline pasado

### 🔧 JQL Personalizado
```jql
# Ejemplos de consultas avanzadas
project = BAUACA AND status = "EN CURSO"
assignee = currentUser() AND priority = "Alto"
updated >= -3d AND project IN (BAUACA, STI)
duedate < "2025-12-31" AND status != "CERRADA"
```

## 🎛️ Panel de Control (Sidebar)

### ⚙️ Configuración
- **Selector de Vista**: Dashboard, Lista, Análisis, Exportar
- **Consulta Rápida**: Dropdown con opciones predefinidas
- **Máximo Resultados**: Slider de 10 a 500 issues
- **JQL Personalizado**: Campo de texto libre

### 🔄 Acciones
- **Actualizar Datos**: Refresca desde Jira
- **Limpiar Caché**: Elimina datos locales

### ℹ️ Información
- **Última Actualización**: Timestamp del último fetch
- **Issues en Caché**: Contador de datos locales

## 🔧 Casos de Uso Típicos

### 👤 Gestor de Proyecto
```
1. Vista Dashboard → Métricas generales
2. Filtro "En Progreso" → Revisar trabajo activo
3. Análisis Temporal → Identificar tendencias
4. Exportar CSV → Reportes semanales
```

### 👩‍💻 Desarrollador
```
1. Vista Lista → Issues pendientes
2. Filtro por Proyecto → Trabajo específico
3. JQL Personalizado → Búsquedas complejas
4. Actualizar cada hora → Seguimiento activo
```

### 📊 Analista
```
1. Vista Análisis → Tendencias detalladas
2. Timeline 30-90 días → Patrones históricos
3. Distribuciones → Carga de trabajo
4. Exportar JSON → Análisis externo
```

## 💡 Tips y Trucos

### ⚡ Productividad
- **Bookmarks**: Guarda URLs con filtros específicos
- **Refresh Automático**: F5 para actualizar datos
- **Teclado**: Tab para navegar entre filtros
- **Mobile**: Funciona en tablets y móviles

### 🔍 Búsquedas Avanzadas
```jql
# Issues urgentes sin asignar
project = BAUACA AND assignee is EMPTY AND priority = "Alto"

# Work en sprint activo
assignee = currentUser() AND sprint in openSprints()

# Issues con comentarios recientes
assignee = currentUser() AND comment ~ "comentario" AND updated >= -7d
```

### 📊 Análisis Efectivo
- **Período Corto**: 7-14 días para tendencias semanales
- **Período Largo**: 30-90 días para patrones mensuales
- **Comparación**: Usa múltiples períodos para contrastar

## ⚠️ Limitaciones y Consideraciones

### 📊 Performance
- **Máximo Recomendado**: 200-300 issues por consulta
- **Refresh**: No automático, manual por seguridad
- **Cache**: Datos persisten durante la sesión

### 🔒 Seguridad
- **Token Rotation**: Cambiar cada 90 días
- **Permisos**: Solo ve issues donde tienes acceso
- **Local**: Datos solo en tu navegador

### 🌐 Red
- **Timeout**: 30 segundos por consulta
- **Rate Limiting**: Respeta límites de Atlassian
- **Offline**: Requiere conexión a internet

## 🆘 Solución Rápida de Problemas

### ❌ "Error de conexión"
```bash
# Verificar credenciales
python jira_viewer.py --test

# Revisar .env
cat .env
```

### ❌ "No se muestran datos"
1. Verificar filtros aplicados
2. Revisar permisos del proyecto
3. Comprobar JQL en Jira web

### ❌ "Aplicación lenta"
1. Reducir número máximo de resultados
2. Usar filtros más específicos
3. Limpiar caché del navegador

### ❌ "Tests fallan"
```bash
# Reinstalar dependencias
make clean
make install
make test
```

## 📞 Contacto y Soporte

### 🔗 Enlaces Útiles
- **Repositorio**: [GitHub VibeCoding](https://github.com/jesusprodriguezUnir/VibeCoding)
- **Documentación Jira**: [API Reference](https://developer.atlassian.com/cloud/jira/platform/rest/)
- **JQL Guide**: [Advanced Search](https://support.atlassian.com/jira-software-cloud/docs/advanced-searching/)

### 📧 Soporte
- **Email**: jesuspedro.rodriguez@unir.net
- **Issues**: GitHub Issues tab
- **Documentación**: README.md completo

---

**¡Empieza a gestionar tus issues de Jira de forma visual y eficiente! 🚀**

*Tiempo estimado de configuración: 5 minutos*  
*Tiempo hasta ser productivo: 10 minutos*