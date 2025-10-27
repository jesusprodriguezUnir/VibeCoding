#!/usr/bin/env python3
"""
Aplicación principal Streamlit para visualizar asignaciones de Jira.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
import sys
from dotenv import load_dotenv

# Cargar variables de entorno explícitamente
load_dotenv()

# Agregar src al path para imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.jira_client import JiraClient, JiraAPIError
from src.data_processor import JiraDataProcessor
from src.config import Config
from src.utils import setup_logging, validate_env_file, format_number

# Configurar página
st.set_page_config(
    page_title="Visualizador de Asignaciones Jira",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar logging
logger = setup_logging()

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .status-badge {
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
    }
    .stButton > button {
        width: 100%;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Inicializa el estado de la sesión."""
    if 'jira_client' not in st.session_state:
        st.session_state.jira_client = None
    if 'data_processor' not in st.session_state:
        st.session_state.data_processor = JiraDataProcessor()
    if 'last_fetch' not in st.session_state:
        st.session_state.last_fetch = None
    if 'cached_issues' not in st.session_state:
        st.session_state.cached_issues = []


def check_configuration():
    """Verifica la configuración y muestra errores si es necesario."""
    validation = validate_env_file()
    
    if not validation['valid']:
        st.error("❌ " + validation['message'])
        
        if validation.get('missing_file'):
            st.info("💡 Sigue estos pasos para configurar:")
            st.code("""
            1. Copia el archivo de ejemplo:
               cp .env.example .env
            
            2. Edita .env con tus credenciales de Jira:
               JIRA_BASE_URL=https://tu-instancia.atlassian.net
               JIRA_EMAIL=tu-email@empresa.com
               JIRA_TOKEN=tu_token_de_api
            """)
        
        st.stop()
    
    return validation


def create_jira_client():
    """Crea y prueba conexión con el cliente Jira."""
    if st.session_state.jira_client is None:
        try:
            st.session_state.jira_client = JiraClient()
            
            # Probar conexión
            connection_result = st.session_state.jira_client.test_connection()
            
            if connection_result['success']:
                st.success(f"✅ {connection_result['message']}")
                return True
            else:
                st.error(f"❌ {connection_result['message']}")
                return False
                
        except Exception as e:
            st.error(f"❌ Error creando cliente Jira: {e}")
            return False
    
    return True


def render_header():
    """Renderiza el header principal."""
    st.markdown("""
    <div class="main-header">
        <h1>📊 Visualizador de Asignaciones Jira</h1>
        <p>Panel interactivo para gestionar y analizar tus asignaciones de Jira</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Renderiza la barra lateral con filtros y opciones."""
    st.sidebar.title("🔧 Configuración")
    
    # Selector de vista
    view_type = st.sidebar.selectbox(
        "📋 Selecciona Vista",
        ["Dashboard", "Lista de Issues", "Análisis", "Exportar Datos"],
        key="view_type"
    )
    
    st.sidebar.markdown("---")
    
    # Filtros
    st.sidebar.subheader("🔍 Filtros")
    
    # Consulta predefinida
    predefined_query = st.sidebar.selectbox(
        "Consulta Rápida",
        list(Config.PREDEFINED_QUERIES.keys()),
        key="predefined_query"
    )
    
    # Número máximo de resultados
    max_results = st.sidebar.slider(
        "Máx. Resultados",
        min_value=10,
        max_value=500,
        value=100,
        step=10,
        key="max_results"
    )
    
    # JQL personalizado
    custom_jql = st.sidebar.text_area(
        "JQL Personalizado (opcional)",
        placeholder="project = MYPROJ AND status = 'In Progress'",
        key="custom_jql"
    )
    
    st.sidebar.markdown("---")
    
    # Botones de acción
    if st.sidebar.button("🔄 Actualizar Datos", type="primary"):
        fetch_data(predefined_query, custom_jql, max_results)
    
    if st.sidebar.button("🗑️ Limpiar Caché"):
        clear_cache()
    
    return view_type, predefined_query, custom_jql, max_results


def fetch_data(predefined_query, custom_jql, max_results):
    """Obtiene datos de Jira."""
    if not st.session_state.jira_client:
        st.error("Cliente Jira no inicializado")
        return
    
    with st.spinner("🔄 Obteniendo datos de Jira..."):
        try:
            # Usar JQL personalizado si está disponible, sino usar predefinido
            if custom_jql.strip():
                result = st.session_state.jira_client.get_issues_by_jql(
                    custom_jql, max_results
                )
            else:
                jql = Config.PREDEFINED_QUERIES[predefined_query]
                result = st.session_state.jira_client.search_issues(
                    jql, max_results
                )
            
            if result['success']:
                st.session_state.cached_issues = result['issues']
                st.session_state.last_fetch = datetime.now()
                st.success(f"✅ {len(result['issues'])} issues obtenidos exitosamente")
            else:
                st.error(f"❌ Error: {result.get('error', 'Error desconocido')}")
                
        except Exception as e:
            st.error(f"❌ Error obteniendo datos: {e}")


def clear_cache():
    """Limpia el caché de datos."""
    st.session_state.cached_issues = []
    st.session_state.last_fetch = None
    st.success("🗑️ Caché limpiado")


def render_dashboard():
    """Renderiza el dashboard principal."""
    if not st.session_state.cached_issues:
        st.info("📭 No hay datos cargados. Usa la barra lateral para obtener datos.")
        return
    
    issues = st.session_state.cached_issues
    processor = st.session_state.data_processor
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Issues", format_number(len(issues)))
    
    with col2:
        status_summary = processor.get_status_summary(issues)
        in_progress = sum(count for status, count in status_summary.items() 
                         if status in ['EN CURSO', 'In Progress', 'ESCALADO'])
        st.metric("En Progreso", format_number(in_progress))
    
    with col3:
        priority_summary = processor.get_priority_summary(issues)
        high_priority = sum(count for priority, count in priority_summary.items() 
                           if priority in ['Alto', 'High', 'Crítico', 'Highest'])
        st.metric("Alta Prioridad", format_number(high_priority))
    
    with col4:
        # Issues actualizados hoy
        today = datetime.now().date()
        today_updates = 0
        for issue in issues:
            updated_str = issue.get('fields', {}).get('updated', '')
            if updated_str:
                try:
                    updated_date = datetime.fromisoformat(
                        updated_str.replace('Z', '+00:00')
                    ).date()
                    if updated_date == today:
                        today_updates += 1
                except:
                    continue
        st.metric("Actualizados Hoy", format_number(today_updates))
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribución por Estado")
        status_data = processor.get_status_summary(issues)
        if status_data:
            fig = px.pie(
                values=list(status_data.values()),
                names=list(status_data.keys()),
                title="Issues por Estado"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Distribución por Prioridad")
        priority_data = processor.get_priority_summary(issues)
        if priority_data:
            fig = px.bar(
                x=list(priority_data.keys()),
                y=list(priority_data.values()),
                title="Issues por Prioridad",
                color=list(priority_data.values()),
                color_continuous_scale="Viridis"
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Timeline
    st.subheader("📈 Timeline de Actualizaciones (últimos 30 días)")
    timeline_data = processor.get_timeline_data(issues, 30)
    if timeline_data['dates']:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timeline_data['dates'],
            y=timeline_data['counts'],
            mode='lines+markers',
            name='Actualizaciones',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(
            title="Actualizaciones por Día",
            xaxis_title="Fecha",
            yaxis_title="Número de Issues",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)


def render_issues_list():
    """Renderiza la lista de issues."""
    if not st.session_state.cached_issues:
        st.info("📭 No hay datos cargados. Usa la barra lateral para obtener datos.")
        return
    
    issues = st.session_state.cached_issues
    processor = st.session_state.data_processor
    
    st.subheader(f"📋 Lista de Issues ({len(issues)} encontrados)")
    
    # Filtros adicionales para la tabla
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtro por estado
        all_statuses = list(set(
            issue.get('fields', {}).get('status', {}).get('name', 'Unknown')
            for issue in issues
        ))
        selected_statuses = st.multiselect(
            "Filtrar por Estado",
            all_statuses,
            default=all_statuses,
            key="status_filter"
        )
    
    with col2:
        # Filtro por proyecto
        all_projects = list(set(
            issue.get('fields', {}).get('project', {}).get('key', 'Unknown')
            for issue in issues
        ))
        selected_projects = st.multiselect(
            "Filtrar por Proyecto",
            all_projects,
            default=all_projects,
            key="project_filter"
        )
    
    with col3:
        # Filtro por prioridad
        all_priorities = list(set(
            issue.get('fields', {}).get('priority', {}).get('name', 'Unknown')
            for issue in issues
        ))
        selected_priorities = st.multiselect(
            "Filtrar por Prioridad",
            all_priorities,
            default=all_priorities,
            key="priority_filter"
        )
    
    # Aplicar filtros
    filtered_issues = []
    for issue in issues:
        fields = issue.get('fields', {})
        status = fields.get('status', {}).get('name', 'Unknown')
        project = fields.get('project', {}).get('key', 'Unknown')
        priority = fields.get('priority', {}).get('name', 'Unknown')
        
        if (status in selected_statuses and 
            project in selected_projects and 
            priority in selected_priorities):
            filtered_issues.append(issue)
    
    # Mostrar tabla
    if filtered_issues:
        df = processor.format_issues_for_display(filtered_issues)
        
        # Hacer que la tabla sea más interactiva
        st.dataframe(
            df,
            use_container_width=True,
            height=600,
            column_config={
                "Key": st.column_config.TextColumn("Clave", width="small"),
                "Summary": st.column_config.TextColumn("Resumen", width="large"),
                "Status": st.column_config.TextColumn("Estado", width="small"),
                "Priority": st.column_config.TextColumn("Prioridad", width="small"),
                "Project": st.column_config.TextColumn("Proyecto", width="small"),
                "Updated": st.column_config.DatetimeColumn("Actualizado", width="medium")
            }
        )
        
        st.info(f"Mostrando {len(filtered_issues)} de {len(issues)} issues")
    else:
        st.warning("No hay issues que coincidan con los filtros seleccionados")


def render_analysis():
    """Renderiza la página de análisis."""
    if not st.session_state.cached_issues:
        st.info("📭 No hay datos cargados. Usa la barra lateral para obtener datos.")
        return
    
    issues = st.session_state.cached_issues
    processor = st.session_state.data_processor
    
    st.subheader("📊 Análisis Detallado")
    
    # Análisis por proyecto
    st.markdown("### 🏢 Análisis por Proyecto")
    project_summary = processor.get_project_summary(issues)
    
    if project_summary:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            fig = px.bar(
                x=list(project_summary.keys()),
                y=list(project_summary.values()),
                title="Issues por Proyecto",
                color=list(project_summary.values()),
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Tabla resumen
            project_df = pd.DataFrame([
                {"Proyecto": k, "Issues": v, "Porcentaje": f"{(v/len(issues)*100):.1f}%"}
                for k, v in project_summary.items()
            ]).sort_values("Issues", ascending=False)
            
            st.dataframe(project_df, use_container_width=True)
    
    st.markdown("---")
    
    # Análisis temporal
    st.markdown("### ⏰ Análisis Temporal")
    
    timeline_days = st.slider(
        "Período de análisis (días)",
        min_value=7,
        max_value=90,
        value=30,
        key="timeline_days"
    )
    
    timeline_data = processor.get_timeline_data(issues, timeline_days)
    
    if timeline_data['dates']:
        # Gráfico de línea con tendencia
        fig = go.Figure()
        
        # Línea principal
        fig.add_trace(go.Scatter(
            x=timeline_data['dates'],
            y=timeline_data['counts'],
            mode='lines+markers',
            name='Actualizaciones Diarias',
            line=dict(color='#667eea', width=2),
            marker=dict(size=6)
        ))
        
        # Media móvil
        if len(timeline_data['counts']) > 7:
            moving_avg = pd.Series(timeline_data['counts']).rolling(window=7).mean()
            fig.add_trace(go.Scatter(
                x=timeline_data['dates'],
                y=moving_avg,
                mode='lines',
                name='Media Móvil (7 días)',
                line=dict(color='#f39c12', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title=f"Tendencia de Actualizaciones - Últimos {timeline_days} días",
            xaxis_title="Fecha",
            yaxis_title="Número de Issues",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Estadísticas
        col1, col2, col3, col4 = st.columns(4)
        
        counts = timeline_data['counts']
        with col1:
            st.metric("Promedio Diario", f"{sum(counts)/len(counts):.1f}")
        with col2:
            st.metric("Máximo Diario", max(counts))
        with col3:
            st.metric("Total Período", sum(counts))
        with col4:
            active_days = len([c for c in counts if c > 0])
            st.metric("Días Activos", f"{active_days}/{len(counts)}")


def render_export():
    """Renderiza la página de exportación."""
    if not st.session_state.cached_issues:
        st.info("📭 No hay datos cargados. Usa la barra lateral para obtener datos.")
        return
    
    issues = st.session_state.cached_issues
    processor = st.session_state.data_processor
    
    st.subheader("💾 Exportar Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Exportar CSV")
        csv_filename = st.text_input(
            "Nombre del archivo CSV",
            value=f"jira_issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            key="csv_filename"
        )
        
        if st.button("🔽 Descargar CSV", type="primary"):
            if processor.export_to_csv(issues, csv_filename):
                st.success(f"✅ Archivo CSV exportado: {csv_filename}")
                
                # Ofrecer descarga
                with open(csv_filename, 'rb') as file:
                    st.download_button(
                        label="📥 Descargar Archivo",
                        data=file.read(),
                        file_name=csv_filename,
                        mime='text/csv'
                    )
    
    with col2:
        st.markdown("### 📋 Exportar JSON")
        json_filename = st.text_input(
            "Nombre del archivo JSON",
            value=f"jira_issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            key="json_filename"
        )
        
        if st.button("🔽 Descargar JSON", type="primary"):
            if processor.export_to_json(issues, json_filename):
                st.success(f"✅ Archivo JSON exportado: {json_filename}")
                
                # Ofrecer descarga
                with open(json_filename, 'rb') as file:
                    st.download_button(
                        label="📥 Descargar Archivo",
                        data=file.read(),
                        file_name=json_filename,
                        mime='application/json'
                    )
    
    # Previsualización de datos
    st.markdown("---")
    st.markdown("### 👀 Previsualización de Datos")
    
    if issues:
        df = processor.format_issues_for_display(issues[:10])
        st.dataframe(df, use_container_width=True)
        st.info(f"Mostrando primeros 10 de {len(issues)} issues totales")


def render_info_panel():
    """Renderiza panel de información."""
    if st.session_state.last_fetch:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ℹ️ Información")
        st.sidebar.text(f"Última actualización:")
        st.sidebar.text(st.session_state.last_fetch.strftime("%H:%M:%S"))
        st.sidebar.text(f"Issues en caché: {len(st.session_state.cached_issues)}")


def main():
    """Función principal de la aplicación."""
    # Inicializar estado
    init_session_state()
    
    # Renderizar header
    render_header()
    
    # Verificar configuración
    check_configuration()
    
    # Crear cliente Jira
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
    elif view_type == "Lista de Issues":
        render_issues_list()
    elif view_type == "Análisis":
        render_analysis()
    elif view_type == "Exportar Datos":
        render_export()


if __name__ == "__main__":
    main()