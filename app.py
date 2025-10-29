#!/usr/bin/env python3
"""
Aplicación principal Streamlit para visualizar asignaciones de Jira.
Aplicación refactorizada en módulos especializados para mejor mantenibilidad.
"""

import streamlit as st
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Imports de módulos especializados
from core.app_state import init_session_state, create_jira_client
from shared.data_fetcher import fetch_data
from shared.ui.layout import render_header, render_info_panel
from shared.ui.sidebar import render_sidebar
from features.dashboards.standard import render_dashboard
from features.dashboards.custom import render_dashboard_selector, render_widget_gallery
from features.issues.viewer import render_issues_list
from features.analysis.reports import render_analysis, render_export
from shared.utils import setup_logging

# Configurar página
st.set_page_config(
    page_title="Visualizador de Asignaciones Jira",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar logging
logger = setup_logging()


def main():
    """Función principal de la aplicación."""
    # Inicializar estado
    init_session_state()
    
    # Renderizar encabezado
    render_header()
    
    # Verificar configuración y crear cliente
    if not create_jira_client():
        st.stop()
    
    # Renderizar sidebar y obtener configuración
    view_type, predefined_query, custom_jql, max_results = render_sidebar()
    
    # Renderizar panel de información
    render_info_panel()
    
    # Cargar datos automáticamente si no hay datos en caché
    if not st.session_state.cached_issues and not custom_jql.strip():
        fetch_data(predefined_query, custom_jql, max_results)
    
    # Renderizar vista seleccionada
    if view_type == "Dashboard":
        render_dashboard()
    elif view_type == "Dashboard Personalizable":
        render_dashboard_selector()
    elif view_type == "Lista de Issues":
        render_issues_list()
    elif view_type == "Análisis":
        render_analysis()
    elif view_type == "Exportar Datos":
        render_export()


if __name__ == "__main__":
    main()