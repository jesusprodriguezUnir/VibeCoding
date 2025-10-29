"""
Módulo de layouts y estructura de la aplicación.
"""
import streamlit as st
from typing import Tuple, Optional


def render_header():
    """Renderiza el encabezado principal de la aplicación."""
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="color: #667eea; margin: 0;">📊 Visualizador de Asignaciones Jira</h1>
            <p style="color: #666; margin: 0.5rem 0;">Gestiona y analiza tus issues de Jira de manera inteligente</p>
        </div>
    """, unsafe_allow_html=True)


def render_info_panel():
    """Renderiza el panel de información lateral."""
    with st.expander("ℹ️ Información de la Aplicación", expanded=False):
        st.markdown("""
        ### 🎯 **Funcionalidades Principales**
        
        **📊 Dashboard Interactivo**
        - Métricas ejecutivas en tiempo real
        - Gráficos elegantes con efectos visuales
        - Timeline de actualizaciones con media móvil
        
        **📋 Gestión de Issues**
        - Lista detallada con filtros avanzados
        - Vista de cards elegantes
        - Enlaces directos a Jira
        
        **🔍 Análisis Avanzado**
        - Tendencias y patrones
        - Análisis de productividad
        - Distribución por proyecto y asignee
        
        **📤 Exportación**
        - Exportar a Excel, CSV, JSON
        - Reportes personalizados
        - Datos filtrados
        
        ### 🚀 **Cómo Usar**
        1. Configura tu token en la barra lateral
        2. Selecciona una consulta predefinida o usa JQL personalizado
        3. Explora los datos en las diferentes vistas
        4. Exporta los resultados según necesites
        
        ### 🔧 **Configuración**
        - Token de Jira válido requerido
        - Conexión a internet necesaria
        - Soporte para Jira Cloud y Server
        """)


def render_main_navigation() -> str:
    """Renderiza la navegación principal y retorna la vista seleccionada."""
    return st.sidebar.selectbox(
        "🧭 Navegación",
        ["Dashboard", "Lista de Issues", "Análisis", "Exportar Datos"],
        help="Selecciona la vista que deseas explorar"
    )