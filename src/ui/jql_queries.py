"""
Sistema de consultas JQL personalizadas para widgets de dashboard.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from ..jira_client import JiraClient
from .ui_utils import get_safe_issues, validate_issues_data


@dataclass
class CustomJQLQuery:
    """Definición de una consulta JQL personalizada."""
    id: str
    name: str
    description: str
    jql: str
    max_results: int = 100
    refresh_interval: int = 300  # segundos
    last_executed: Optional[datetime] = None
    cached_results: Optional[List[Dict]] = None


class JQLQueryManager:
    """Gestor de consultas JQL personalizadas."""
    
    def __init__(self):
        self.queries = {}
        self._init_predefined_queries()
    
    def _init_predefined_queries(self):
        """Inicializa consultas predefinidas útiles."""
        
        # Escalaciones sin asignar
        self.add_query(CustomJQLQuery(
            id="escalations_unassigned",
            name="Escalaciones Sin Asignar",
            description="Issues escalados que no tienen asignee",
            jql='issueLinkType in ("is an escalation for") AND assignee is EMPTY AND statusCategory != done ORDER BY created DESC',
            max_results=50
        ))
        
        # Issues antiguos sin resolver
        self.add_query(CustomJQLQuery(
            id="old_unresolved",
            name="Issues Antiguos Sin Resolver",
            description="Issues creados hace más de 12 semanas sin resolver",
            jql='created >= -80w AND status not in (RESUELTA, CERRADA, DESESTIMADA) AND statusCategory != done ORDER BY created ASC',
            max_results=100
        ))
        
        # Servicios universitarios específicos
        self.add_query(CustomJQLQuery(
            id="university_services_bau",
            name="BAU Servicios Universitarios",
            description="Issues del proyecto BAU Servicios Universitarios - Académico",
            jql='project = "BAU Servicios Universitarios - Académico" AND status not in (RESUELTA, CERRADA, DESESTIMADA) ORDER BY priority DESC, created DESC',
            max_results=75
        ))
        
        # Query del usuario específica
        self.add_query(CustomJQLQuery(
            id="user_specific_query",
            name="Escalaciones BAU Académico Sin Asignar",
            description="Escalaciones del área académica creadas en últimas 80 semanas sin asignar",
            jql='created >= -80w AND project = "BAU Servicios Universitarios - Académico" AND status not in (RESUELTA, CERRADA, DESESTIMADA) AND Subarea = "ari:cloud:cmdb::object/d80a641b-f11a-4ae4-8159-a153bbcbb09d/34" AND issueLinkType in ("is an escalation for") AND statusCategory != done AND assignee is EMPTY ORDER BY created DESC',
            max_results=50
        ))
        
        # Issues de alta prioridad pendientes
        self.add_query(CustomJQLQuery(
            id="high_priority_pending",
            name="Alta Prioridad Pendientes",
            description="Issues de alta prioridad que requieren atención inmediata",
            jql='priority in (High, Highest, Crítico, Alto) AND status not in (RESUELTA, CERRADA, DESESTIMADA) AND statusCategory != done ORDER BY priority DESC, created ASC',
            max_results=30
        ))
        
        # Issues vencidos
        self.add_query(CustomJQLQuery(
            id="overdue_issues",
            name="Issues Vencidos",
            description="Issues con fecha de vencimiento pasada",
            jql='duedate < now() AND status not in (RESUELTA, CERRADA, DESESTIMADA) AND statusCategory != done ORDER BY duedate ASC',
            max_results=40
        ))
    
    def add_query(self, query: CustomJQLQuery):
        """Añade una consulta al gestor."""
        self.queries[query.id] = query
    
    def get_query(self, query_id: str) -> Optional[CustomJQLQuery]:
        """Obtiene una consulta por ID."""
        return self.queries.get(query_id)
    
    def get_all_queries(self) -> Dict[str, CustomJQLQuery]:
        """Obtiene todas las consultas."""
        return self.queries.copy()
    
    def execute_query(self, query_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Ejecuta una consulta JQL y cachea los resultados."""
        query = self.get_query(query_id)
        if not query:
            return {"success": False, "error": f"Query {query_id} not found", "issues": []}
        
        # Verificar si necesitamos refrescar
        now = datetime.now()
        needs_refresh = (
            force_refresh or 
            query.last_executed is None or 
            query.cached_results is None or
            (now - query.last_executed).seconds > query.refresh_interval
        )
        
        if not needs_refresh and query.cached_results is not None:
            return {"success": True, "issues": query.cached_results, "cached": True}
        
        # Ejecutar consulta
        if not st.session_state.client:
            return {"success": False, "error": "Cliente Jira no disponible", "issues": []}
        
        try:
            result = st.session_state.client.search_issues(
                jql=query.jql,
                max_results=query.max_results
            )
            
            if result.get('success', False):
                query.cached_results = result.get('issues', [])
                query.last_executed = now
                return {"success": True, "issues": query.cached_results, "cached": False}
            else:
                return {"success": False, "error": result.get('error', 'Error unknown'), "issues": []}
                
        except Exception as e:
            return {"success": False, "error": str(e), "issues": []}
    
    def create_custom_query(self, name: str, description: str, jql: str, max_results: int = 100) -> str:
        """Crea una consulta personalizada nueva."""
        # Generar ID único
        query_id = f"custom_{len([q for q in self.queries.keys() if q.startswith('custom_')])}"
        
        query = CustomJQLQuery(
            id=query_id,
            name=name,
            description=description,
            jql=jql,
            max_results=max_results
        )
        
        self.add_query(query)
        return query_id
    
    def delete_query(self, query_id: str) -> bool:
        """Elimina una consulta personalizada."""
        if query_id in self.queries and query_id.startswith('custom_'):
            del self.queries[query_id]
            return True
        return False
    
    def validate_jql(self, jql: str) -> Dict[str, Any]:
        """Valida una consulta JQL."""
        if not jql.strip():
            return {"valid": False, "error": "JQL no puede estar vacío"}
        
        # Validaciones básicas
        if 'DELETE' in jql.upper() or 'DROP' in jql.upper():
            return {"valid": False, "error": "JQL contiene comandos no permitidos"}
        
        # Intentar ejecutar una versión limitada para validar sintaxis
        test_jql = f"({jql}) AND maxResults <= 1"
        
        try:
            if st.session_state.client:
                result = st.session_state.client.search_issues(jql=test_jql, max_results=1)
                if result.get('success', False):
                    return {"valid": True, "message": "JQL válido"}
                else:
                    return {"valid": False, "error": result.get('error', 'Error en JQL')}
            else:
                return {"valid": True, "message": "JQL básico válido (no se puede validar completamente sin conexión)"}
        except Exception as e:
            return {"valid": False, "error": f"Error validando JQL: {str(e)}"}


def render_jql_query_manager():
    """Renderiza el gestor de consultas JQL."""
    st.markdown("### 🔍 **Gestor de Consultas JQL**")
    
    if 'jql_manager' not in st.session_state:
        st.session_state.jql_manager = JQLQueryManager()
    
    manager = st.session_state.jql_manager
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3 = st.tabs(["📋 Consultas Disponibles", "➕ Nueva Consulta", "▶️ Ejecutar Consulta"])
    
    with tab1:
        render_available_queries(manager)
    
    with tab2:
        render_new_query_form(manager)
    
    with tab3:
        render_query_executor(manager)


def render_available_queries(manager: JQLQueryManager):
    """Renderiza lista de consultas disponibles."""
    st.markdown("#### Consultas Disponibles")
    
    queries = manager.get_all_queries()
    
    if not queries:
        st.info("No hay consultas disponibles")
        return
    
    for query_id, query in queries.items():
        with st.expander(f"🔍 {query.name}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Descripción:** {query.description}")
                st.code(query.jql, language="sql")
                st.write(f"**Máx. resultados:** {query.max_results}")
                
                if query.last_executed:
                    st.write(f"**Última ejecución:** {query.last_executed.strftime('%Y-%m-%d %H:%M:%S')}")
                    if query.cached_results:
                        st.write(f"**Resultados en caché:** {len(query.cached_results)} issues")
            
            with col2:
                if st.button(f"▶️ Ejecutar", key=f"exec_{query_id}"):
                    st.session_state[f"execute_query_{query_id}"] = True
                
                if query_id.startswith('custom_'):
                    if st.button(f"🗑️ Eliminar", key=f"del_{query_id}"):
                        manager.delete_query(query_id)
                        st.rerun()
                
                if st.button(f"📊 Crear Widget", key=f"widget_{query_id}"):
                    st.session_state[f"create_widget_{query_id}"] = True
        
        # Ejecutar consulta si se solicitó
        if st.session_state.get(f"execute_query_{query_id}", False):
            st.session_state[f"execute_query_{query_id}"] = False
            with st.spinner(f"Ejecutando {query.name}..."):
                result = manager.execute_query(query_id, force_refresh=True)
                if result["success"]:
                    st.success(f"✅ {len(result['issues'])} issues encontrados")
                    if result['issues']:
                        render_query_results(result['issues'], query.name)
                else:
                    st.error(f"❌ Error: {result['error']}")
        
        # Crear widget si se solicitó
        if st.session_state.get(f"create_widget_{query_id}", False):
            st.session_state[f"create_widget_{query_id}"] = False
            create_widget_from_query(query_id, query)


def render_new_query_form(manager: JQLQueryManager):
    """Renderiza formulario para nueva consulta."""
    st.markdown("#### Crear Nueva Consulta")
    
    with st.form("new_jql_query"):
        name = st.text_input("Nombre de la consulta", placeholder="Ej: Escalaciones Pendientes")
        description = st.text_area("Descripción", placeholder="Describe qué hace esta consulta...")
        jql = st.text_area(
            "Consulta JQL", 
            placeholder="created >= -80w AND project = ...",
            help="Introduce tu consulta JQL personalizada"
        )
        max_results = st.number_input("Máximo resultados", min_value=1, max_value=1000, value=100)
        
        submitted = st.form_submit_button("✅ Crear Consulta")
        
        if submitted:
            if not name.strip():
                st.error("El nombre es obligatorio")
            elif not jql.strip():
                st.error("La consulta JQL es obligatoria")
            else:
                # Validar JQL
                validation = manager.validate_jql(jql)
                if validation["valid"]:
                    query_id = manager.create_custom_query(name, description, jql, max_results)
                    st.success(f"✅ Consulta '{name}' creada con ID: {query_id}")
                    st.rerun()
                else:
                    st.error(f"❌ JQL inválido: {validation['error']}")


def render_query_executor(manager: JQLQueryManager):
    """Renderiza ejecutor de consultas."""
    st.markdown("#### Ejecutar Consulta")
    
    queries = manager.get_all_queries()
    if not queries:
        st.info("No hay consultas disponibles para ejecutar")
        return
    
    # Selector de consulta
    query_options = {f"{query.name} ({query_id})": query_id for query_id, query in queries.items()}
    selected_display = st.selectbox("Seleccionar consulta", list(query_options.keys()))
    selected_id = query_options[selected_display]
    
    selected_query = manager.get_query(selected_id)
    
    if selected_query:
        st.write(f"**Descripción:** {selected_query.description}")
        st.code(selected_query.jql, language="sql")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Ejecutar Consulta"):
                with st.spinner("Ejecutando consulta..."):
                    result = manager.execute_query(selected_id, force_refresh=True)
                    if result["success"]:
                        st.success(f"✅ {len(result['issues'])} issues encontrados")
                        if result['issues']:
                            render_query_results(result['issues'], selected_query.name)
                    else:
                        st.error(f"❌ Error: {result['error']}")
        
        with col2:
            if st.button("📊 Crear Widget de esta Consulta"):
                create_widget_from_query(selected_id, selected_query)


def render_query_results(issues: List[Dict], query_name: str):
    """Renderiza resultados de una consulta."""
    st.markdown(f"#### Resultados: {query_name}")
    
    if not issues:
        st.info("No se encontraron issues")
        return
    
    # Formatear datos para tabla
    data = []
    for issue in issues:
        fields = issue.get('fields', {})
        
        # Manejar campos que pueden ser None de forma segura
        status = fields.get('status') or {}
        priority = fields.get('priority') or {}
        assignee = fields.get('assignee') or {}
        
        data.append({
            'Key': issue.get('key', 'N/A'),
            'Summary': fields.get('summary', 'N/A')[:60] + '...' if len(fields.get('summary', '')) > 60 else fields.get('summary', 'N/A'),
            'Status': status.get('name', 'N/A'),
            'Priority': priority.get('name', 'N/A'),
            'Assignee': assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned',
            'Created': format_date(fields.get('created')),
            'Updated': format_date(fields.get('updated'))
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, height=400)
    
    # Métricas rápidas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Issues", len(issues))
    with col2:
        unassigned = len([i for i in issues if not i.get('fields', {}).get('assignee')])
        st.metric("Sin Asignar", unassigned)
    with col3:
        high_priority = len([i for i in issues if (i.get('fields', {}).get('priority') or {}).get('name', '') in ['Alto', 'High', 'Crítico', 'Highest']])
        st.metric("Alta Prioridad", high_priority)


def create_widget_from_query(query_id: str, query: CustomJQLQuery):
    """Crea un widget basado en una consulta."""
    st.success(f"🎯 Widget creado para: {query.name}")
    st.info("Próximamente: El widget se agregará automáticamente a la galería de widgets disponibles.")
    
    # Aquí se integraría con el sistema de widgets
    # Por ahora mostramos el código que se usaría
    st.code(f"""
# Widget para consulta: {query.name}
widget_registry.register(Widget(
    id="query_{query_id}",
    title="{query.name}",
    widget_type=WidgetType.TABLE,
    size=WidgetSize.LARGE,
    config={{"jql_query_id": "{query_id}"}},
    render_func=render_jql_query_widget
))
    """, language="python")


def format_date(date_str: str) -> str:
    """Formatea fecha."""
    if not date_str:
        return 'N/A'
    
    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d')
        else:
            return date_str
    except (ValueError, TypeError):
        return date_str