"""
Lógica de obtención y procesamiento de datos.
"""
import streamlit as st
from core.jira_client import JiraAPIError
from core.data_processor import JiraDataProcessor
from core.config import Config


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
        # Validar que no sea un separador visual
        if predefined_query.startswith("───") and predefined_query.endswith("───"):
            st.warning("⚠️ Por favor selecciona una consulta válida")
            return
            
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
                total = result.get('total', 0)
                start_at = result.get('start_at', 0)  # Esto viene del cliente que ya convierte startAt -> start_at
                max_results_returned = result.get('max_results', 0)  # Esto viene del cliente que ya convierte maxResults -> max_results
                
                if issues:
                    st.session_state.cached_issues = issues
                    st.session_state.data_processor = JiraDataProcessor()
                    
                    # Validar y normalizar datos de paginación
                    total = max(0, total)
                    start_at = max(0, start_at)
                    max_results_returned = max(1, max_results_returned)  # Asegurar que sea al menos 1
                    
                    # Guardar información de paginación
                    st.session_state.pagination_info = {
                        'total': total,
                        'start_at': start_at,
                        'max_results': max_results_returned,
                        'current_jql': jql_query,
                        'has_more': (start_at + max_results_returned) < total
                    }
                    
                    # Información detallada del resultado
                    if total > max_results_returned:
                        st.success(f"✅ Mostrando {len(issues)} de {total:,} issues totales (página {(start_at // max_results_returned) + 1})")
                        st.info(f"📄 Hay {total - (start_at + max_results_returned):,} issues adicionales disponibles")
                    else:
                        st.success(f"✅ {len(issues)} issues obtenidos exitosamente")
                else:
                    st.warning("⚠️ No se encontraron issues con la consulta especificada")
                    st.session_state.cached_issues = []
                    st.session_state.pagination_info = None
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


def load_more_issues(page_number: int = None, page_size: int = None):
    """Carga más issues de la consulta actual usando paginación.
    
    Args:
        page_number: Número de página específica a cargar (1-based)
        page_size: Tamaño de página a usar (si es diferente del actual)
    """
    if not st.session_state.get('pagination_info'):
        st.error("❌ No hay información de paginación disponible")
        return
        
    if not st.session_state.get('client'):
        st.error("❌ Cliente Jira no inicializado")
        return
    
    pagination = st.session_state.pagination_info
    current_jql = pagination['current_jql']
    
    # Usar page_size pasado o el actual
    max_results = page_size or pagination['max_results']
    
    # Calcular start_at basado en el número de página
    if page_number:
        start_at = (page_number - 1) * max_results
    else:
        start_at = pagination['start_at'] + max_results
    
    try:
        with st.spinner("🔄 Cargando más resultados..."):
            result = st.session_state.client.search_issues(
                jql=current_jql,
                max_results=max_results,
                start_at=start_at
            )
            
            if result.get('success', False):
                new_issues = result.get('issues', [])
                total = result.get('total', 0)
                
                if new_issues:
                    # Actualizar issues y paginación
                    st.session_state.cached_issues = new_issues
                    st.session_state.pagination_info.update({
                        'start_at': start_at,
                        'max_results': max_results,
                        'has_more': (start_at + len(new_issues)) < total
                    })
                    
                    current_page = (start_at // max_results) + 1
                    total_pages = (total + max_results - 1) // max_results
                    
                    st.success(f"✅ Página {current_page} de {total_pages} cargada ({len(new_issues)} issues)")
                    st.rerun()
                else:
                    st.warning("⚠️ No hay más issues disponibles")
            else:
                error_msg = result.get('error', 'Error desconocido')
                st.error(f"❌ Error cargando más datos: {error_msg}")
                
    except Exception as e:
        st.error(f"❌ Error inesperado cargando más datos: {str(e)}")


def load_all_issues_batch(max_total_results: int = 1000):
    """Carga múltiples páginas de issues hasta alcanzar el límite deseado.
    
    Args:
        max_total_results: Número máximo total de issues a cargar
    """
    if not st.session_state.get('pagination_info'):
        st.error("❌ No hay información de paginación disponible")
        return
        
    if not st.session_state.get('client'):
        st.error("❌ Cliente Jira no inicializado")
        return
    
    pagination = st.session_state.pagination_info
    current_jql = pagination['current_jql']
    total_available = pagination['total']
    
    # Determinar cuántos issues cargar realmente
    target_count = min(max_total_results, total_available)
    
    # Usar páginas de 100 para optimizar la carga
    page_size = min(100, target_count)
    all_issues = []
    
    try:
        with st.spinner(f"🔄 Cargando {target_count} issues en lotes de {page_size}..."):
            for start_at in range(0, target_count, page_size):
                current_page_size = min(page_size, target_count - start_at)
                
                result = st.session_state.client.search_issues(
                    jql=current_jql,
                    max_results=current_page_size,
                    start_at=start_at
                )
                
                if result.get('success', False):
                    issues = result.get('issues', [])
                    all_issues.extend(issues)
                    
                    # Mostrar progreso
                    progress = len(all_issues) / target_count
                    st.progress(progress, f"Cargados {len(all_issues)} de {target_count} issues...")
                    
                    if len(issues) < current_page_size:
                        break  # No hay más issues
                else:
                    st.error(f"❌ Error en lote: {result.get('error', 'Unknown')}")
                    break
            
            if all_issues:
                # Actualizar con todos los issues cargados
                st.session_state.cached_issues = all_issues
                st.session_state.pagination_info.update({
                    'start_at': 0,
                    'max_results': len(all_issues),
                    'has_more': len(all_issues) < total_available,
                    'batch_loaded': True,
                    'batch_size': len(all_issues)
                })
                
                st.success(f"✅ Cargados {len(all_issues)} issues de {total_available} totales")
                st.rerun()
            else:
                st.warning("⚠️ No se pudieron cargar issues")
                
    except Exception as e:
        st.error(f"❌ Error cargando lotes: {str(e)}")