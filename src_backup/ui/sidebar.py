"""
Configuración y gestión del sidebar de la aplicación.
"""
import streamlit as st
from typing import Tuple
from ..config import Config
from .ui_utils import get_safe_issues, validate_issues_data, get_issues_count


def render_sidebar() -> Tuple[str, str, str, int]:
    """
    Renderiza la barra lateral con configuración.
    
    Returns:
        Tuple[str, str, str, int]: (view_type, predefined_query, custom_jql, max_results)
    """
    with st.sidebar:
        st.markdown("## ⚙️ **Configuración**")
        
        # Navegación principal
        view_type = st.selectbox(
            "🧭 Navegación",
            ["Dashboard", "Dashboard Personalizable", "Lista de Issues", "Análisis", "Exportar Datos"],
            help="Selecciona la vista que deseas explorar"
        )
        
        st.markdown("---")
        
        # Configuración de consultas
        predefined_query, custom_jql, max_results = render_query_config()
        
        st.markdown("---")
        
        # Botones de acción
        render_action_buttons()
        
        return view_type, predefined_query, custom_jql, max_results


def render_query_config() -> Tuple[str, str, int]:
    """
    Renderiza la configuración de consultas JQL.
    
    Returns:
        Tuple[str, str, int]: (predefined_query, custom_jql, max_results)
    """
    st.markdown("### 🔍 **Consultas**")
    
    # Consultas predefinidas
    predefined_query = st.selectbox(
        "Consulta Predefinida",
        [
            "Mis Issues",
            "En Progreso", 
            "Pendientes",
            "Completados",
            "Alta Prioridad",
            "Actualizados Hoy",
            "Actualizados Esta Semana",
            "Con Fecha Vencida"
        ],
        help="Selecciona una consulta predefinida común"
    )
    
    # JQL personalizado
    custom_jql = st.text_area(
        "JQL Personalizado (opcional)",
        help="Escribe tu propia consulta JQL. Si está vacío, se usará la consulta predefinida.",
        placeholder="project = 'MI-PROYECTO' AND assignee = currentUser()"
    )
    
    # Límite de resultados
    max_results = st.slider(
        "Máximo de Resultados",
        min_value=10,
        max_value=500,
        value=100,
        step=10,
        help="Número máximo de issues a recuperar"
    )
    
    return predefined_query, custom_jql, max_results


def render_action_buttons():
    """Renderiza los botones de acción del sidebar."""
    st.markdown("### 🎯 **Acciones**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.session_state.cached_issues = []
            st.session_state.data_processor = None
            st.rerun()
    
    with col2:
        if st.button("🗑️ Limpiar", use_container_width=True):
            # Importar aquí para evitar dependencias circulares
            from ..app_state import clear_cache
            clear_cache()
            st.rerun()
    
    # Estadísticas rápidas
    if validate_issues_data():
        issues_count = get_issues_count()
        st.success(f"📊 **{issues_count} issues** cargados")
        
        if st.session_state.get('data_processor'):
            issues = get_safe_issues()
            
            # Métricas rápidas con validación adicional
            try:
                in_progress = len([
                    i for i in issues 
                    if isinstance(i, dict) and 
                    i.get('fields', {}).get('status', {}).get('name', '') in ['EN CURSO', 'In Progress', 'ESCALADO']
                ])
                high_priority = len([
                    i for i in issues 
                    if isinstance(i, dict) and 
                    i.get('fields', {}).get('priority', {}).get('name', '') in ['Alto', 'High', 'Crítico', 'Highest']
                ])
                
                st.metric("🔥 En Progreso", in_progress)
                st.metric("⚡ Alta Prioridad", high_priority)
            except Exception as e:
                st.error(f"❌ Error calculando métricas: {str(e)}")
    else:
        st.info("📭 No hay datos cargados")