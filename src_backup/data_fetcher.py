"""
Lógica de obtención y procesamiento de datos.
"""
import streamlit as st
from .jira_client import JiraAPIError
from .data_processor import JiraDataProcessor
from .config import Config


def fetch_data(predefined_query: str, custom_jql: str, max_results: int):
    """
    Obtiene datos de Jira y los procesa.
    
    Args:
        predefined_query: Nombre de la consulta predefinida
        custom_jql: Consulta JQL personalizada
        max_results: Número máximo de resultados
    """
    if not st.session_state.client:
        st.error("❌ Cliente Jira no inicializado")
        return
    
    # Determinar qué consulta usar
    if custom_jql.strip():
        jql_query = custom_jql.strip()
    else:
        # Usar consulta predefinida del Config
        jql_query = Config.PREDEFINED_QUERIES.get(predefined_query, predefined_query)
    
    try:
        with st.spinner("🔄 Obteniendo datos de Jira..."):
            result = st.session_state.client.search_issues(
                jql=jql_query,
                max_results=max_results
            )
            
            if result.get('success', False):
                issues = result.get('issues', [])
                if issues:
                    st.session_state.cached_issues = issues
                    st.session_state.data_processor = JiraDataProcessor()
                    st.success(f"✅ {len(issues)} issues obtenidos exitosamente")
                else:
                    st.warning("⚠️ No se encontraron issues con la consulta especificada")
                    st.session_state.cached_issues = []
                    st.session_state.data_processor = None
            else:
                error_msg = result.get('error', 'Error desconocido')
                st.error(f"❌ Error obteniendo datos: {error_msg}")
                st.session_state.cached_issues = []
                st.session_state.data_processor = None
                
    except JiraAPIError as e:
        st.error(f"❌ Error de API de Jira: {str(e)}")
        st.session_state.cached_issues = []
        st.session_state.data_processor = None
        
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        st.session_state.cached_issues = []
        st.session_state.data_processor = None