# 🔍 Guía de Consultas JQL Personalizadas en Dashboard

Esta guía explica cómo usar las nuevas funcionalidades de consultas JQL personalizadas en el dashboard.

## 🚀 Nuevas Funcionalidades Implementadas

### 1. **Widgets con Consultas JQL Integradas**

- `escalations_unassigned_jql` — Escalaciones sin asignar
- `user_bau_escalations` — Tu consulta específica de BAU Académico
- `old_unresolved_jql` — Issues antiguos sin resolver
- `custom_jql_widget` — Widget configurable con JQL personalizada

### 2. **Gestores de Consultas JQL**

- Crear, editar y ejecutar consultas JQL personalizadas
- Validación automática de sintaxis JQL
- Cache de resultados para mejor rendimiento
- Gestión de consultas predefinidas y personalizadas

### 3. **Dashboards Predefinidos Nuevos**

- **"Consultas JQL Avanzadas"** — Widgets especializados en JQL
- **"BAU Servicios Universitarios - Académico"** — Tu dashboard específico

## 🎯 Tu Consulta Específica Implementada

Tu consulta JQL ha sido implementada como widget especializado:

```jql
created >= -80w 
AND project = "BAU Servicios Universitarios - Académico" 
AND status not in (RESUELTA, CERRADA, DESESTIMADA) 
AND Subarea = "ari:cloud:cmdb::object/d80a641b-f11a-4ae4-8159-a153bbcbb09d/34" 
AND issueLinkType in ("is an escalation for") 
AND statusCategory != done 
AND assignee is EMPTY 
ORDER BY created DESC
```

### Características del Widget

- ✅ **Ejecución automática** de la consulta
- ✅ **Métricas integradas** (total, sin asignar, alta prioridad)
- ✅ **Resaltado de urgencia** para issues críticos
- ✅ **Tabla interactiva** con filtros
- ✅ **Actualización en tiempo real**

## 📊 Cómo Usar

### Opción 1: Dashboard Predefinido "BAU Académico"

1. Ve a **Dashboard Personalizable**
2. Selecciona **"BAU Servicios Universitarios - Académico"**
3. Tu consulta aparece como widget **"BAU Académico - Escalaciones Sin Asignar"**

### Opción 2: Gestión Manual de Consultas JQL

1. Ve a **Dashboard Personalizable** → **Pestaña "Consultas JQL"**
2. En **"Consultas Disponibles"** encuentra tu consulta predefinida
3. Haz clic en **"▶️ Ejecutar"** para ver resultados
4. Haz clic en **"📊 Crear Widget"** para añadirla a un dashboard

### Opción 3: Widget JQL Configurable

1. Agrega el widget **"Consulta JQL Personalizada"** a cualquier dashboard
2. Configura tu JQL específica en el widget
3. Obtén resultados inmediatos

## 🛠️ Crear Nuevas Consultas

### En el Gestor de Consultas

1. **Pestaña "Nueva Consulta"**
2. Completa:
   - **Nombre**: "Mi Consulta Personalizada"
   - **Descripción**: Qué hace la consulta
   - **JQL**: Tu consulta personalizada
   - **Máx. Resultados**: Límite de issues
3. **Crear Consulta** → La consulta queda disponible

### Ejemplos de Consultas Útiles

```jql
# Issues sin asignar de alta prioridad
assignee is EMPTY AND priority in (High, Highest) ORDER BY created DESC

# Issues vencidos de mi proyecto
project = "MI_PROYECTO" AND duedate < now() AND status != Done

# Escalaciones recientes
issueLinkType in ("is an escalation for") AND created >= -2w

# Issues antiguos sin actualizar
updated <= -4w AND status not in (Resolved, Closed)
```

## 📈 Métricas y Análisis

Cada widget JQL proporciona:

- **📋 Total**: Número total de issues
- **👤 Sin Asignar**: Issues sin assignee
- **⚡ Alta Prioridad**: Issues críticos/altos
- **🚨 Urgencia**: Resaltado de issues que requieren atención
- **📅 Antigüedad**: Edad de los issues en días

## 🎛️ Personalización Avanzada

### Configuraciones Disponibles

- `jql_query`: Tu consulta JQL específica
- `max_results`: Límite de resultados (1-1000)
- `show_metrics`: Mostrar métricas resumidas
- `show_age`: Mostrar antigüedad de issues
- `highlight_urgent`: Resaltar issues urgentes
- `refresh_interval`: Intervalo de actualización automática

### Crear Widget Personalizado

```python
# Ejemplo de configuración
config = {
    "jql_query": "tu_consulta_aqui",
    "max_results": 100,
    "show_metrics": True,
    "highlight_urgent": True
}
```

## 🚀 Próximos Pasos

1. **Prueba tu consulta** en el dashboard "BAU Académico"
2. **Crea consultas adicionales** según tus necesidades
3. **Personaliza dashboards** combinando widgets JQL con métricas generales
4. **Experimenta** con diferentes combinaciones de widgets

## 🆘 Solución de Problemas

### Error en Consulta JQL

- Verifica la sintaxis en Jira web primero
- Usa el validador integrado en **"Nueva Consulta"**
- Revisa que los nombres de campos sean correctos

### Widget no Muestra Datos

- Verifica conexión a Jira en la barra lateral
- Confirma que la consulta devuelve resultados en Jira
- Revisa permisos de acceso a los proyectos

### Rendimiento Lento

- Reduce `max_results` en consultas complejas
- Usa filtros más específicos en JQL
- Aprovecha el cache automático (5 minutos)

¡Tu dashboard personalizado con consultas JQL está listo para usar! 🎉