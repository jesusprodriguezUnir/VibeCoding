"""
Sistema refactorizado de consultas JQL personalizadas.
Versión mejorada con mejor organización, categorización y performance.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from core.config import Config
from shared.utils import format_number


def format_date(date_str: str) -> str:
    """Formatea fecha de Jira a formato legible."""
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


@dataclass
class JQLQuery:
    """Definición refactorizada de una consulta JQL."""
    id: str
    name: str
    description: str
    jql: str
    max_results: int = 100
    category: str = "custom"
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la consulta a diccionario."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'jql': self.jql,
            'max_results': self.max_results,
            'category': self.category,
            'tags': self.tags,
            'created_at': self.created_at.isoformat()
        }


class JQLQueryRepository:
    """Repositorio mejorado de consultas JQL con categorización."""
    
    def __init__(self):
        self.queries: Dict[str, JQLQuery] = {}
        self._load_predefined_queries()
    
    def _load_predefined_queries(self):
        """Carga consultas predefinidas organizadas por categorías."""
        
        # Consultas básicas (integradas con Config existente)
        basic_queries = [
            JQLQuery(
                id="pending",
                name="Pendientes",
                description="Issues asignados pendientes de trabajo",
                jql=Config.PREDEFINED_QUERIES["Pendientes"],
                category="basic",
                tags=["status", "assigned", "pending"]
            ),
            JQLQuery(
                id="in_progress",
                name="En Progreso", 
                description="Issues actualmente en desarrollo",
                jql=Config.PREDEFINED_QUERIES["En Progreso"],
                category="basic",
                tags=["status", "assigned", "active"]
            ),
            JQLQuery(
                id="high_priority",
                name="Alta Prioridad",
                description="Issues críticos que requieren atención",
                jql=Config.PREDEFINED_QUERIES["Alta Prioridad"],
                category="basic",
                tags=["priority", "critical", "urgent"]
            ),
            JQLQuery(
                id="completed",
                name="Completados",
                description="Issues finalizados y cerrados",
                jql=Config.PREDEFINED_QUERIES["Completados"],
                category="basic",
                tags=["status", "done", "completed"]
            )
        ]
        
        # Consultas avanzadas para análisis y gestión
        advanced_queries = [
            JQLQuery(
                id="escalations_unassigned",
                name="Escalaciones Sin Asignar",
                description="Issues escalados que requieren asignación",
                jql='issueLinkType in ("is an escalation for") AND assignee is EMPTY AND statusCategory != done ORDER BY created DESC',
                max_results=150,
                category="management",
                tags=["escalation", "unassigned", "urgent", "management"]
            ),
            JQLQuery(
                id="old_unresolved",
                name="Issues Antiguos Sin Resolver",
                description="Issues creados hace más de 12 semanas sin resolver",
                jql='created <= -12w AND status not in (RESUELTA, CERRADA, DESESTIMADA) AND statusCategory != done ORDER BY created ASC',
                max_results=100,
                category="maintenance",
                tags=["old", "unresolved", "review", "maintenance"]
            ),
            JQLQuery(
                id="overdue_issues",
                name="Issues Vencidos",
                description="Issues con fecha de vencimiento pasada",
                jql='duedate < now() AND status not in (RESUELTA, CERRADA, DESESTIMADA) AND statusCategory != done ORDER BY duedate ASC',
                max_results=100,
                category="management",
                tags=["overdue", "deadline", "urgent"]
            ),
            JQLQuery(
                id="blocked_issues",
                name="Issues Bloqueados",
                description="Issues marcados como bloqueados",
                jql='status = "BLOQUEADA" OR labels in (blocked, blocker) ORDER BY updated DESC',
                max_results=75,
                category="management",
                tags=["blocked", "impediment", "review"]
            )
        ]
        
        # Consultas específicas del dominio universitario
        university_queries = [
            JQLQuery(
                id="expedientes_all",
                name="Expedientes",
                description="Todos los expedientes de BAU Académico activos (no cerrados ni resueltos)",
                jql=Config.PREDEFINED_QUERIES["Expedientes"],
                max_results=100,
                category="university",
                tags=["expedientes", "bau", "academic", "active"]
            ),
            JQLQuery(
                id="expedientes_pending",
                name="Expedientes Pendientes",
                description="Expedientes en estado pendiente o análisis",
                jql=Config.PREDEFINED_QUERIES["Expedientes Pendientes"],
                max_results=75,
                category="university", 
                tags=["expedientes", "pending", "analysis", "todo"]
            ),
            JQLQuery(
                id="expedientes_in_progress",
                name="Expedientes En Curso",
                description="Expedientes actualmente en proceso o escalados",
                jql=Config.PREDEFINED_QUERIES["Expedientes En Curso"],
                max_results=75,
                category="university",
                tags=["expedientes", "progress", "escalated", "active"]
            ),
            JQLQuery(
                id="expedientes_unassigned",
                name="Expedientes Sin Asignar",
                description="Expedientes que necesitan asignación de responsable",
                jql=Config.PREDEFINED_QUERIES["Expedientes Sin Asignar"],
                max_results=50,
                category="university",
                tags=["expedientes", "unassigned", "needs-assignment", "urgent"]
            ),
            JQLQuery(
                id="university_services_bau",
                name="BAU Servicios Universitarios",
                description="Issues del proyecto académico universitario",
                jql='project = "BAU Servicios Universitarios - Académico" AND status not in (RESUELTA, CERRADA, DESESTIMADA) ORDER BY priority DESC, created DESC',
                max_results=75,
                category="university",
                tags=["bau", "academic", "university", "services"]
            ),
            JQLQuery(
                id="academic_escalations",
                name="Escalaciones Académicas",
                description="Escalaciones del área académica sin responsable",
                jql='created >= -20w AND project = "BAU Servicios Universitarios - Académico" AND status not in (RESUELTA, CERRADA, DESESTIMADA) AND issueLinkType in ("is an escalation for") AND statusCategory != done AND assignee is EMPTY ORDER BY created DESC',
                max_results=50,
                category="university",
                tags=["escalation", "academic", "unassigned", "university"]
            ),
            JQLQuery(
                id="bau_escalations",
                name="Escalaciones BAU",
                description="Todas las escalaciones del proyecto BAU Académico",
                jql=Config.PREDEFINED_QUERIES["Escalaciones BAU"],
                max_results=50,
                category="university",
                tags=["escalation", "bau", "academic", "all-escalations"]
            )
        ]
        
        # Consultas de análisis temporal
        analysis_queries = [
            JQLQuery(
                id="updated_today",
                name="Actualizados Hoy",
                description="Issues con actividad en las últimas 24 horas",
                jql=Config.PREDEFINED_QUERIES["Actualizados Hoy"],
                category="analysis",
                tags=["recent", "activity", "today"]
            ),
            JQLQuery(
                id="updated_week",
                name="Actualizados Esta Semana",
                description="Issues con actividad en los últimos 7 días",
                jql=Config.PREDEFINED_QUERIES["Actualizados Esta Semana"],
                category="analysis",
                tags=["recent", "activity", "weekly"]
            ),
            JQLQuery(
                id="created_last_week",
                name="Creados la Semana Pasada",
                description="Issues creados en los últimos 7 días",
                jql='created >= -1w ORDER BY created DESC',
                max_results=150,
                category="analysis",
                tags=["recent", "created", "weekly"]
            )
        ]
        
        # Registrar todas las consultas
        all_queries = basic_queries + advanced_queries + university_queries + analysis_queries
        for query in all_queries:
            self.queries[query.id] = query
    
    def get_query(self, query_id: str) -> Optional[JQLQuery]:
        """Obtiene una consulta por ID."""
        return self.queries.get(query_id)
    
    def get_queries_by_category(self, category: str) -> List[JQLQuery]:
        """Obtiene consultas filtradas por categoría."""
        return [q for q in self.queries.values() if q.category == category]
    
    def get_queries_by_tag(self, tag: str) -> List[JQLQuery]:
        """Obtiene consultas que contienen una etiqueta específica."""
        return [q for q in self.queries.values() if tag in q.tags]
    
    def search_queries(self, search_term: str) -> List[JQLQuery]:
        """Busca consultas por nombre, descripción o tags."""
        search_term = search_term.lower()
        results = []
        
        for query in self.queries.values():
            if (search_term in query.name.lower() or
                search_term in query.description.lower() or
                any(search_term in tag.lower() for tag in query.tags)):
                results.append(query)
        
        return results
    
    def add_custom_query(self, name: str, description: str, jql: str, 
                        max_results: int = 100, tags: List[str] = None) -> str:
        """Agrega una consulta personalizada nueva."""
        query_id = f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        query = JQLQuery(
            id=query_id,
            name=name,
            description=description,
            jql=jql,
            max_results=max_results,
            category="custom",
            tags=tags or []
        )
        
        self.queries[query_id] = query
        return query_id
    
    def remove_custom_query(self, query_id: str) -> bool:
        """Elimina una consulta personalizada (solo custom)."""
        if query_id in self.queries and self.queries[query_id].category == "custom":
            del self.queries[query_id]
            return True
        return False
    
    def get_all_categories(self) -> List[str]:
        """Obtiene lista de todas las categorías disponibles."""
        return sorted(list(set(q.category for q in self.queries.values())))
    
    def get_all_tags(self) -> List[str]:
        """Obtiene lista de todas las etiquetas disponibles."""
        tags = set()
        for query in self.queries.values():
            tags.update(query.tags)
        return sorted(list(tags))
    
    def get_query_count_by_category(self) -> Dict[str, int]:
        """Obtiene conteo de consultas por categoría."""
        counts = {}
        for query in self.queries.values():
            counts[query.category] = counts.get(query.category, 0) + 1
        return counts


class JQLExecutor:
    """Ejecutor optimizado de consultas JQL con caché inteligente."""
    
    def __init__(self, cache_ttl_minutes: int = 5):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.execution_stats = {}
    
    def execute_query(self, query: JQLQuery, force_refresh: bool = False) -> Dict[str, Any]:
        """Ejecuta una consulta JQL con caché y estadísticas."""
        start_time = datetime.now()
        cache_key = f"{query.id}_{hash(query.jql)}_{query.max_results}"
        
        # Verificar caché si no se fuerza refresh
        if not force_refresh and cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < self.cache_ttl:
                execution_time = (datetime.now() - start_time).total_seconds()
                return {
                    "success": True,
                    "issues": cached_data['issues'],
                    "cached": True,
                    "query": query,
                    "execution_time": execution_time,
                    "timestamp": cached_data['timestamp']
                }
        
        # Verificar cliente Jira
        if not st.session_state.get('client'):
            return {
                "success": False,
                "error": "Cliente Jira no disponible. Verifica tu conexión.",
                "issues": [],
                "query": query,
                "cached": False
            }
        
        try:
            # Ejecutar consulta
            result = st.session_state.client.search_issues(
                jql=query.jql,
                max_results=query.max_results
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if result.get('success', False):
                issues = result.get('issues', [])
                
                # Actualizar caché
                self.cache[cache_key] = {
                    'issues': issues,
                    'timestamp': datetime.now()
                }
                
                # Actualizar estadísticas
                self._update_execution_stats(query.id, execution_time, len(issues), True)
                
                return {
                    "success": True,
                    "issues": issues,
                    "cached": False,
                    "query": query,
                    "execution_time": execution_time,
                    "timestamp": datetime.now()
                }
            else:
                error_msg = result.get('error', 'Error desconocido al ejecutar consulta')
                self._update_execution_stats(query.id, execution_time, 0, False)
                
                return {
                    "success": False,
                    "error": error_msg,
                    "issues": [],
                    "query": query,
                    "cached": False,
                    "execution_time": execution_time
                }
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_execution_stats(query.id, execution_time, 0, False)
            
            return {
                "success": False,
                "error": f"Error ejecutando consulta: {str(e)}",
                "issues": [],
                "query": query,
                "cached": False,
                "execution_time": execution_time
            }
    
    def _update_execution_stats(self, query_id: str, execution_time: float, 
                               result_count: int, success: bool):
        """Actualiza estadísticas de ejecución."""
        if query_id not in self.execution_stats:
            self.execution_stats[query_id] = {
                'total_executions': 0,
                'successful_executions': 0,
                'total_time': 0,
                'last_execution': None,
                'last_result_count': 0
            }
        
        stats = self.execution_stats[query_id]
        stats['total_executions'] += 1
        stats['total_time'] += execution_time
        stats['last_execution'] = datetime.now()
        stats['last_result_count'] = result_count
        
        if success:
            stats['successful_executions'] += 1
    
    def get_execution_stats(self, query_id: str) -> Dict[str, Any]:
        """Obtiene estadísticas de ejecución para una consulta."""
        if query_id not in self.execution_stats:
            return {}
        
        stats = self.execution_stats[query_id]
        avg_time = stats['total_time'] / stats['total_executions'] if stats['total_executions'] > 0 else 0
        success_rate = stats['successful_executions'] / stats['total_executions'] if stats['total_executions'] > 0 else 0
        
        return {
            'total_executions': stats['total_executions'],
            'successful_executions': stats['successful_executions'],
            'success_rate': success_rate,
            'average_execution_time': avg_time,
            'last_execution': stats['last_execution'],
            'last_result_count': stats['last_result_count']
        }
    
    def validate_jql(self, jql: str) -> Dict[str, Any]:
        """Valida sintaxis y seguridad de JQL."""
        if not jql.strip():
            return {"valid": False, "error": "JQL no puede estar vacío"}
        
        # Validaciones de seguridad
        forbidden_keywords = ['DELETE', 'DROP', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE']
        jql_upper = jql.upper()
        
        for keyword in forbidden_keywords:
            if keyword in jql_upper:
                return {"valid": False, "error": f"Comando '{keyword}' no permitido por seguridad"}
        
        # Validación sintáctica con Jira
        try:
            if st.session_state.get('client'):
                test_result = st.session_state.client.search_issues(
                    jql=jql, 
                    max_results=1
                )
                
                if test_result.get('success', False):
                    return {"valid": True, "message": "JQL válido y ejecutable"}
                else:
                    error_msg = test_result.get('error', 'JQL inválido')
                    return {"valid": False, "error": f"Error de sintaxis JQL: {error_msg}"}
            else:
                # Validaciones básicas sin conexión
                basic_keywords = ['SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY']
                if any(keyword in jql_upper for keyword in basic_keywords):
                    return {"valid": False, "error": "JQL no debe contener sintaxis SQL"}
                
                return {"valid": True, "message": "JQL sintácticamente correcto (validación completa requiere conexión)"}
                
        except Exception as e:
            return {"valid": False, "error": f"Error validando JQL: {str(e)}"}
    
    def clear_cache(self):
        """Limpia el caché de consultas."""
        self.cache.clear()
        st.success("🗑️ Caché de consultas limpiado")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Obtiene información del estado del caché."""
        total_entries = len(self.cache)
        total_size = sum(len(entry['issues']) for entry in self.cache.values())
        
        return {
            'total_entries': total_entries,
            'total_cached_issues': total_size,
            'cache_ttl_minutes': self.cache_ttl.total_seconds() / 60
        }


# Funciones de renderizado para UI
def render_jql_manager():
    """Renderiza el gestor de consultas JQL refactorizado."""
    st.markdown("### 🔍 **Gestor de Consultas JQL**")
    
    # Inicializar componentes
    if 'jql_repository' not in st.session_state:
        st.session_state.jql_repository = JQLQueryRepository()
    
    if 'jql_executor' not in st.session_state:
        st.session_state.jql_executor = JQLExecutor()
    
    repository = st.session_state.jql_repository
    executor = st.session_state.jql_executor
    
    # Pestañas principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 Explorar", 
        "▶️ Ejecutar", 
        "➕ Crear", 
        "📊 Analytics"
    ])
    
    with tab1:
        render_query_explorer(repository)
    
    with tab2:
        render_query_executor_ui(repository, executor)
    
    with tab3:
        render_query_creator(repository, executor)
    
    with tab4:
        render_query_analytics(repository)


def render_query_explorer(repository: JQLQueryRepository):
    """Renderiza explorador de consultas organizadas."""
    st.markdown("#### 📚 Explorar Consultas")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        categories = ["Todas"] + repository.get_all_categories()
        selected_category = st.selectbox("Categoría", categories)
    
    with col2:
        tags = ["Todas"] + repository.get_all_tags()
        selected_tag = st.selectbox("Etiqueta", tags)
    
    with col3:
        search_term = st.text_input("🔍 Buscar", placeholder="Buscar consultas...")
    
    # Obtener consultas filtradas
    if search_term:
        queries = repository.search_queries(search_term)
    else:
        queries = list(repository.queries.values())
    
    if selected_category != "Todas":
        queries = [q for q in queries if q.category == selected_category]
    
    if selected_tag != "Todas":
        queries = [q for q in queries if selected_tag in q.tags]
    
    # Mostrar consultas agrupadas por categoría
    if not queries:
        st.info("No se encontraron consultas con los filtros aplicados")
        return
    
    # Agrupar por categorías
    categories_dict = {}
    for query in queries:
        if query.category not in categories_dict:
            categories_dict[query.category] = []
        categories_dict[query.category].append(query)
    
    # Renderizar por categorías
    for category, category_queries in categories_dict.items():
        st.markdown(f"##### 📁 {category.title()} ({len(category_queries)})")
        
        for query in sorted(category_queries, key=lambda x: x.name):
            with st.expander(f"🔍 {query.name}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Descripción:** {query.description}")
                    
                    # Mostrar tags como badges
                    if query.tags:
                        tags_html = " ".join([f'<span style="background-color: #f0f2f6; padding: 2px 6px; border-radius: 10px; font-size: 0.8em; margin: 2px;">{tag}</span>' for tag in query.tags])
                        st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)
                    
                    st.write(f"**Máx. resultados:** {format_number(query.max_results)}")
                    
                    with st.expander("Ver JQL", expanded=False):
                        st.code(query.jql, language="sql")
                
                with col2:
                    if st.button("▶️ Ejecutar", key=f"exec_{query.id}", help="Ejecutar esta consulta"):
                        st.session_state[f"execute_query_{query.id}"] = True
                    
                    if query.category == "custom":
                        if st.button("🗑️ Eliminar", key=f"del_{query.id}", help="Eliminar consulta personalizada"):
                            if repository.remove_custom_query(query.id):
                                st.success("Consulta eliminada")
                                st.rerun()
                    
                    if st.button("📋 Copiar JQL", key=f"copy_{query.id}", help="Copiar JQL al portapapeles"):
                        st.code(query.jql, language="sql")
                        st.info("JQL copiado arriba")
        
        # Ejecutar consulta si se solicitó
        for query in category_queries:
            if st.session_state.get(f"execute_query_{query.id}", False):
                st.session_state[f"execute_query_{query.id}"] = False
                executor = st.session_state.jql_executor
                
                with st.spinner(f"Ejecutando {query.name}..."):
                    result = executor.execute_query(query, force_refresh=True)
                    
                    if result["success"]:
                        issues = result["issues"]
                        cached_info = " (desde caché)" if result.get("cached", False) else ""
                        exec_time = f" en {result.get('execution_time', 0):.2f}s"
                        
                        st.success(f"✅ {len(issues)} issues encontrados{cached_info}{exec_time}")
                        
                        if issues:
                            render_query_results_simple(issues, query.name)
                        else:
                            st.info("No se encontraron issues que coincidan con la consulta")
                    else:
                        st.error(f"❌ Error: {result['error']}")


def render_query_executor_ui(repository: JQLQueryRepository, executor: JQLExecutor):
    """Renderiza ejecutor de consultas avanzado."""
    st.markdown("#### ▶️ Ejecutor de Consultas")
    
    queries = repository.queries
    if not queries:
        st.info("No hay consultas disponibles")
        return
    
    # Selector de consulta organizado
    query_options = {}
    for category in repository.get_all_categories():
        category_queries = repository.get_queries_by_category(category)
        for query in category_queries:
            display_name = f"[{category.upper()}] {query.name}"
            query_options[display_name] = query.id
    
    selected_display = st.selectbox(
        "Seleccionar consulta", 
        list(query_options.keys()),
        key="query_executor_selector"
    )
    
    if not selected_display:
        return
    
    selected_id = query_options[selected_display]
    query = repository.get_query(selected_id)
    
    if not query:
        st.error("Consulta no encontrada")
        return
    
    # Información de la consulta
    st.info(f"📝 **{query.description}**")
    
    # Mostrar tags
    if query.tags:
        tags_str = " ".join([f"`{tag}`" for tag in query.tags])
        st.markdown(f"**Tags:** {tags_str}")
    
    # Opciones de ejecución
    col1, col2, col3 = st.columns(3)
    
    with col1:
        force_refresh = st.checkbox("🔄 Forzar actualización", help="Ignorar caché")
    
    with col2:
        show_advanced = st.checkbox("📊 Mostrar métricas avanzadas")
    
    with col3:
        show_jql = st.checkbox("👁️ Mostrar JQL")
    
    if show_jql:
        st.code(query.jql, language="sql")
    
    # Estadísticas de ejecución previas
    if show_advanced:
        stats = executor.get_execution_stats(query.id)
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Ejecuciones", stats['total_executions'])
            with col2:
                st.metric("Éxito", f"{stats['success_rate']:.1%}")
            with col3:
                st.metric("Tiempo Promedio", f"{stats['average_execution_time']:.2f}s")
            with col4:
                st.metric("Últimos Resultados", stats['last_result_count'])
    
    # Botón de ejecución
    if st.button("🚀 Ejecutar Consulta", type="primary", use_container_width=True):
        with st.spinner(f"Ejecutando {query.name}..."):
            result = executor.execute_query(query, force_refresh=force_refresh)
            
            if result["success"]:
                issues = result["issues"]
                cached_info = " (desde caché)" if result.get("cached", False) else ""
                exec_time = f" en {result.get('execution_time', 0):.2f}s"
                
                st.success(f"✅ {len(issues)} issues encontrados{cached_info}{exec_time}")
                
                if issues:
                    render_query_results_enhanced(issues, query.name, show_advanced)
                else:
                    st.info("No se encontraron issues que coincidan con la consulta")
            else:
                st.error(f"❌ Error: {result['error']}")


def render_query_creator(repository: JQLQueryRepository, executor: JQLExecutor):
    """Renderiza creador de consultas mejorado."""
    st.markdown("#### ➕ Crear Nueva Consulta")
    
    with st.form("create_jql_query", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Nombre *", 
                placeholder="Ej: Escalaciones Críticas",
                help="Nombre descriptivo para la consulta"
            )
            
            jql = st.text_area(
                "Consulta JQL *",
                placeholder="project = 'MI-PROYECTO' AND priority = High",
                help="Introduce tu consulta JQL. Usa el validador antes de guardar.",
                height=100
            )
        
        with col2:
            description = st.text_area(
                "Descripción *",
                placeholder="Describe qué hace esta consulta y cuándo usarla...",
                help="Descripción detallada de la funcionalidad",
                height=100
            )
            
            max_results = st.number_input(
                "Máximo resultados", 
                min_value=1, 
                max_value=1000, 
                value=100,
                help="Número máximo de resultados a obtener"
            )
        
        # Tags
        st.markdown("**Etiquetas** *(opcional)*")
        col1, col2 = st.columns(2)
        
        with col1:
            existing_tags = repository.get_all_tags()
            selected_existing_tags = st.multiselect(
                "Seleccionar etiquetas existentes",
                existing_tags,
                help="Selecciona de las etiquetas ya existentes"
            )
        
        with col2:
            new_tags_input = st.text_input(
                "Nuevas etiquetas (separadas por comas)",
                placeholder="custom, importante, proyecto-x",
                help="Agregar nuevas etiquetas separadas por comas"
            )
        
        # Botones
        col1, col2, col3 = st.columns(3)
        
        with col1:
            validate_button = st.form_submit_button("🔍 Validar JQL", help="Verificar sintaxis JQL")
        
        with col2:
            test_button = st.form_submit_button("🧪 Probar", help="Ejecutar con 1 resultado")
        
        with col3:
            create_button = st.form_submit_button("✅ Crear", type="primary", help="Crear la consulta")
        
        # Validación JQL
        if validate_button and jql:
            validation = executor.validate_jql(jql)
            if validation["valid"]:
                st.success(f"✅ {validation['message']}")
            else:
                st.error(f"❌ {validation['error']}")
        
        # Prueba de consulta
        if test_button and jql:
            validation = executor.validate_jql(jql)
            if validation["valid"]:
                test_query = JQLQuery(
                    id="test",
                    name="Test",
                    description="Test query",
                    jql=jql,
                    max_results=1
                )
                
                with st.spinner("Probando consulta..."):
                    result = executor.execute_query(test_query, force_refresh=True)
                    
                    if result["success"]:
                        st.success(f"✅ Consulta válida - {len(result['issues'])} resultado(s) de prueba")
                    else:
                        st.error(f"❌ Error en consulta: {result['error']}")
            else:
                st.error(f"❌ JQL inválido: {validation['error']}")
        
        # Creación de consulta
        if create_button:
            if not all([name.strip(), description.strip(), jql.strip()]):
                st.error("❌ Todos los campos marcados con * son obligatorios")
            else:
                # Validar JQL
                validation = executor.validate_jql(jql)
                if not validation["valid"]:
                    st.error(f"❌ JQL inválido: {validation['error']}")
                else:
                    # Procesar tags
                    all_tags = selected_existing_tags.copy()
                    if new_tags_input:
                        new_tags = [tag.strip() for tag in new_tags_input.split(",")]
                        all_tags.extend([tag for tag in new_tags if tag])
                    
                    # Eliminar duplicados manteniendo orden
                    final_tags = list(dict.fromkeys(all_tags))
                    
                    # Crear consulta
                    query_id = repository.add_custom_query(
                        name=name,
                        description=description,
                        jql=jql,
                        max_results=max_results,
                        tags=final_tags
                    )
                    
                    st.success(f"✅ Consulta '{name}' creada exitosamente")
                    st.info(f"ID: `{query_id}`")
                    
                    if final_tags:
                        tags_str = ", ".join(final_tags)
                        st.info(f"Etiquetas: {tags_str}")


def render_query_analytics(repository: JQLQueryRepository):
    """Renderiza analytics y estadísticas de consultas."""
    st.markdown("#### 📊 Analytics de Consultas")
    
    queries = list(repository.queries.values())
    
    if not queries:
        st.info("No hay consultas para analizar")
        return
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Consultas", len(queries))
    
    with col2:
        custom_count = len([q for q in queries if q.category == "custom"])
        st.metric("Personalizadas", custom_count)
    
    with col3:
        categories = len(repository.get_all_categories())
        st.metric("Categorías", categories)
    
    with col4:
        tags = len(repository.get_all_tags())
        st.metric("Etiquetas", tags)
    
    # Distribución por categorías
    st.markdown("##### 📊 Distribución por Categorías")
    category_counts = repository.get_query_count_by_category()
    
    if category_counts:
        df_categories = pd.DataFrame(
            list(category_counts.items()),
            columns=['Categoría', 'Cantidad']
        ).sort_values('Cantidad', ascending=False)
        
        st.bar_chart(df_categories.set_index('Categoría'))
    
    # Tags más populares
    st.markdown("##### 🏷️ Tags Más Utilizadas")
    tag_counts = {}
    for query in queries:
        for tag in query.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    if tag_counts:
        df_tags = pd.DataFrame(
            list(tag_counts.items()),
            columns=['Tag', 'Frecuencia']
        ).sort_values('Frecuencia', ascending=False).head(15)
        
        st.dataframe(df_tags, use_container_width=True)
    else:
        st.info("No hay tags disponibles")
    
    # Información del caché
    if 'jql_executor' in st.session_state:
        executor = st.session_state.jql_executor
        cache_info = executor.get_cache_info()
        
        st.markdown("##### 💾 Estado del Caché")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Entradas en Caché", cache_info['total_entries'])
        
        with col2:
            st.metric("Issues en Caché", cache_info['total_cached_issues'])
        
        with col3:
            st.metric("TTL (minutos)", f"{cache_info['cache_ttl_minutes']:.1f}")
        
        if st.button("🗑️ Limpiar Caché"):
            executor.clear_cache()


def render_query_results_simple(issues: List[Dict], query_name: str):
    """Renderiza resultados de consulta de forma simple."""
    if not issues:
        st.info("No se encontraron issues")
        return
    
    # Métricas básicas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Issues", format_number(len(issues)))
    
    with col2:
        unassigned = len([i for i in issues if not i.get('fields', {}).get('assignee')])
        st.metric("Sin Asignar", format_number(unassigned))
    
    with col3:
        high_priority = len([
            i for i in issues 
            if (i.get('fields', {}).get('priority') or {}).get('name', '') in 
            ['Alto', 'High', 'Crítico', 'Highest']
        ])
        st.metric("Alta Prioridad", format_number(high_priority))
    
    # Vista de tabla compacta
    data = []
    for issue in issues[:10]:  # Mostrar solo los primeros 10
        fields = issue.get('fields', {})
        status = fields.get('status') or {}
        assignee = fields.get('assignee') or {}
        
        data.append({
            'Key': issue.get('key', 'N/A'),
            'Summary': fields.get('summary', 'N/A')[:50] + '...' if len(fields.get('summary', '')) > 50 else fields.get('summary', 'N/A'),
            'Status': status.get('name', 'N/A'),
            'Assignee': assignee.get('displayName', 'Sin asignar') if assignee else 'Sin asignar'
        })
    
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, height=300)
        
        if len(issues) > 10:
            st.info(f"Mostrando 10 de {len(issues)} issues. Usa el ejecutor para ver todos los resultados.")


def render_query_results_enhanced(issues: List[Dict], query_name: str, show_advanced: bool = False):
    """Renderiza resultados de consulta con funcionalidades avanzadas."""
    if not issues:
        st.info("No se encontraron issues")
        return
    
    # Métricas detalladas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Issues", format_number(len(issues)))
    
    with col2:
        unassigned = len([i for i in issues if not i.get('fields', {}).get('assignee')])
        st.metric("Sin Asignar", format_number(unassigned))
    
    with col3:
        high_priority = len([
            i for i in issues 
            if (i.get('fields', {}).get('priority') or {}).get('name', '') in 
            ['Alto', 'High', 'Crítico', 'Highest']
        ])
        st.metric("Alta Prioridad", format_number(high_priority))
    
    with col4:
        in_progress = len([
            i for i in issues 
            if (i.get('fields', {}).get('status') or {}).get('name', '') in 
            ['EN CURSO', 'In Progress', 'ESCALADO']
        ])
        st.metric("En Progreso", format_number(in_progress))
    
    # Opciones de visualización
    view_mode = st.radio(
        "Modo de visualización:",
        ["📊 Tabla Completa", "📑 Vista Compacta", "📈 Resumen Ejecutivo"],
        horizontal=True,
        key="results_view_mode"
    )
    
    if view_mode == "📊 Tabla Completa":
        render_full_results_table(issues)
    elif view_mode == "📑 Vista Compacta":
        render_compact_results(issues)
    else:
        render_executive_summary(issues)
    
    # Exportación
    if st.button("📥 Exportar a CSV"):
        df = create_export_dataframe(issues)
        csv = df.to_csv(index=False)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        st.download_button(
            label="Descargar CSV",
            data=csv,
            file_name=f"jira_results_{query_name}_{timestamp}.csv",
            mime="text/csv"
        )


def render_full_results_table(issues: List[Dict]):
    """Renderiza tabla completa de resultados."""
    data = []
    for issue in issues:
        fields = issue.get('fields', {})
        status = fields.get('status') or {}
        priority = fields.get('priority') or {}
        assignee = fields.get('assignee') or {}
        
        data.append({
            'Key': issue.get('key', 'N/A'),
            'Summary': fields.get('summary', 'N/A')[:80] + '...' if len(fields.get('summary', '')) > 80 else fields.get('summary', 'N/A'),
            'Status': status.get('name', 'N/A'),
            'Priority': priority.get('name', 'N/A'),
            'Assignee': assignee.get('displayName', 'Sin asignar') if assignee else 'Sin asignar',
            'Created': format_date(fields.get('created')),
            'Updated': format_date(fields.get('updated'))
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, height=500)


def render_compact_results(issues: List[Dict]):
    """Renderiza vista compacta de resultados."""
    for i, issue in enumerate(issues[:25]):  # Limitar para performance
        fields = issue.get('fields', {})
        status = fields.get('status', {}).get('name', 'N/A')
        priority = fields.get('priority', {}).get('name', 'N/A')
        assignee = fields.get('assignee')
        assignee_name = assignee.get('displayName', 'Sin asignar') if assignee else 'Sin asignar'
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.write(f"**{issue.get('key', 'N/A')}** - {fields.get('summary', 'N/A')[:50]}...")
        
        with col2:
            st.write(f"🏷️ {status}")
        
        with col3:
            st.write(f"⚡ {priority}")
        
        with col4:
            st.write(f"👤 {assignee_name[:15]}...")
        
        if i < min(24, len(issues) - 1):
            st.divider()
    
    if len(issues) > 25:
        st.info(f"Mostrando 25 de {len(issues)} issues. Usa la tabla completa para ver todos.")


def render_executive_summary(issues: List[Dict]):
    """Renderiza resumen ejecutivo con gráficos."""
    if not issues:
        return
    
    # Análisis de distribuciones
    status_counts = {}
    priority_counts = {}
    assignee_counts = {}
    
    for issue in issues:
        fields = issue.get('fields', {})
        
        # Status
        status = fields.get('status', {}).get('name', 'Sin Estado')
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # Priority
        priority = fields.get('priority', {}).get('name', 'Sin Prioridad')
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Assignee
        assignee = fields.get('assignee')
        if assignee:
            name = assignee.get('displayName', 'Sin Nombre')
        else:
            name = 'Sin Asignar'
        assignee_counts[name] = assignee_counts.get(name, 0) + 1
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Distribución por Estado**")
        if status_counts:
            df_status = pd.DataFrame(
                list(status_counts.items()),
                columns=['Estado', 'Cantidad']
            ).sort_values('Cantidad', ascending=False)
            st.bar_chart(df_status.set_index('Estado'))
    
    with col2:
        st.markdown("**⚡ Distribución por Prioridad**")
        if priority_counts:
            df_priority = pd.DataFrame(
                list(priority_counts.items()),
                columns=['Prioridad', 'Cantidad']
            ).sort_values('Cantidad', ascending=False)
            st.bar_chart(df_priority.set_index('Prioridad'))
    
    # Top assignees
    st.markdown("**👥 Top Asignados**")
    if assignee_counts:
        sorted_assignees = sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        df_assignees = pd.DataFrame(sorted_assignees, columns=['Asignado', 'Issues'])
        st.dataframe(df_assignees, use_container_width=True)


def create_export_dataframe(issues: List[Dict]) -> pd.DataFrame:
    """Crea DataFrame optimizado para exportación."""
    data = []
    for issue in issues:
        fields = issue.get('fields', {})
        
        status = fields.get('status') or {}
        priority = fields.get('priority') or {}
        assignee = fields.get('assignee') or {}
        project = fields.get('project') or {}
        issuetype = fields.get('issuetype') or {}
        
        data.append({
            'Key': issue.get('key', ''),
            'Summary': fields.get('summary', ''),
            'Description': fields.get('description', ''),
            'Status': status.get('name', ''),
            'Priority': priority.get('name', ''),
            'Assignee': assignee.get('displayName', '') if assignee else '',
            'Reporter': fields.get('reporter', {}).get('displayName', '') if fields.get('reporter') else '',
            'Project': project.get('name', ''),
            'Issue Type': issuetype.get('name', ''),
            'Created': format_date(fields.get('created')),
            'Updated': format_date(fields.get('updated')),
            'Due Date': format_date(fields.get('duedate')),
            'Labels': ', '.join(fields.get('labels', [])),
            'Components': ', '.join([c.get('name', '') for c in fields.get('components', [])])
        })
    
    return pd.DataFrame(data)