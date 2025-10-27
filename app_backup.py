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

# ===== CONSTANTES PARA SONARQUBE =====
NO_DATA_MESSAGE = "📭 No hay datos cargados. Usa la barra lateral para obtener datos."
IN_PROGRESS_STATUSES = ['EN CURSO', 'In Progress', 'ESCALADO']
HIGH_PRIORITY_LEVELS = ['Alto', 'High', 'Crítico', 'Highest']
FONT_FAMILY = "Arial, sans-serif"
TRANSPARENT_BG = 'rgba(0,0,0,0)'
GRID_COLOR = 'rgba(128,128,128,0.2)'
HOVER_EXTRA = "<extra></extra>"
Y_AXIS_TITLE = "<b>Número de Issues</b>"
STANDARD_FONT_SIZE = 12
TITLE_FONT_SIZE = 14
DEFAULT_MARGIN = {"t": 50, "b": 50, "l": 50, "r": 50}
TIMELINE_MARGIN = {"t": 80, "b": 50, "l": 50, "r": 50}
PROJECT_MARGIN = {"t": 50, "b": 50, "l": 100, "r": 50}

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
        st.info(NO_DATA_MESSAGE)
        return
    
    issues = st.session_state.cached_issues
    processor = st.session_state.data_processor
    
    # Dividir en funciones más pequeñas
    render_metrics_section(issues, processor)
    st.markdown("---")
    render_charts_section(issues, processor)
    render_timeline_section(issues, processor)
    render_projects_section(issues, processor)


def render_metrics_section(issues, processor):
    """Renderiza la sección de métricas principales."""
    st.markdown("### 📊 **Resumen Ejecutivo**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_issues = len(issues)
        st.metric(
            label="📋 Total Issues",
            value=format_number(total_issues),
            help="Número total de issues asignados"
        )
    
    with col2:
        status_summary = processor.get_status_summary(issues)
        in_progress = sum(count for status, count in status_summary.items() 
                         if status in IN_PROGRESS_STATUSES)
        percentage = (in_progress / total_issues * 100) if total_issues > 0 else 0
        st.metric(
            label="⚡ En Progreso",
            value=format_number(in_progress),
            delta=f"{percentage:.1f}% del total",
            help="Issues actualmente en desarrollo"
        )
    
    with col3:
        priority_summary = processor.get_priority_summary(issues)
        high_priority = sum(count for priority, count in priority_summary.items() 
                           if priority in HIGH_PRIORITY_LEVELS)
        percentage = (high_priority / total_issues * 100) if total_issues > 0 else 0
        st.metric(
            label="🔥 Alta Prioridad",
            value=format_number(high_priority),
            delta=f"{percentage:.1f}% del total",
            delta_color="inverse",
            help="Issues críticos y de alta prioridad"
        )
    
    with col4:
        today_updates = get_today_updates(issues)
        st.metric(
            label="📅 Actualizados Hoy",
            value=format_number(today_updates),
            delta="Actividad reciente",
            help="Issues con cambios en las últimas 24 horas"
        )


def get_today_updates(issues):
    """Calcula issues actualizados hoy."""
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
            except (ValueError, TypeError):
                continue
    return today_updates
    
    st.markdown("---")
    
def render_charts_section(issues, processor):
    """Renderiza la sección de gráficos principales."""
    col1, col2 = st.columns(2)
    
    with col1:
        render_status_pie_chart(issues, processor)
    
    with col2:
        render_priority_bar_chart(issues, processor)


def render_status_pie_chart(issues, processor):
    """Renderiza gráfico de distribución por estado."""
    st.subheader("📊 Distribución por Estado")
    status_data = processor.get_status_summary(issues)
    if status_data:
        # Colores elegantes para estados
        status_colors = {
            'NUEVA': '#FF6B6B',      # Rojo suave
            'EN CURSO': '#4ECDC4',   # Turquesa
            'ESCALADO': '#FF8E53',   # Naranja
            'ANÁLISIS': '#45B7D1',   # Azul
            'CERRADA': '#96CEB4',    # Verde suave
            'RESUELTA': '#FFEAA7'    # Amarillo suave
        }
        
        colors = [status_colors.get(status, '#DDA0DD') for status in status_data.keys()]
        
        fig = px.pie(
            values=list(status_data.values()),
            names=list(status_data.keys()),
            title="<b>Issues por Estado</b>",
            color_discrete_sequence=colors
        )
        
        fig.update_traces(
            textposition='auto',
            textinfo='percent+label',
            textfont_size=STANDARD_FONT_SIZE,
            marker={'line': {'color': '#FFFFFF', 'width': 2}},
            hovertemplate="<b>%{label}</b><br>" +
                        "Issues: %{value}<br>" +
                        "Porcentaje: %{percent}<br>" +
                        HOVER_EXTRA
        )
        
        fig.update_layout(
            font={'family': FONT_FAMILY, 'size': STANDARD_FONT_SIZE},
            plot_bgcolor=TRANSPARENT_BG,
            paper_bgcolor=TRANSPARENT_BG,
            margin=DEFAULT_MARGIN,
            showlegend=True,
            legend={
                'orientation': "v",
                'yanchor': "middle",
                'y': 0.5,
                'xanchor': "left",
                'x': 1.05
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_priority_bar_chart(issues, processor):
    """Renderiza gráfico de distribución por prioridad."""
    st.subheader("🎯 Distribución por Prioridad")
    priority_data = processor.get_priority_summary(issues)
    if priority_data:
        # Gradiente de colores para prioridades
        priority_colors = {
            'Highest': '#E74C3C',    # Rojo intenso
            'High': '#F39C12',       # Naranja
            'Medium': '#F1C40F',     # Amarillo
            'Low': '#2ECC71',        # Verde
            'Lowest': '#3498DB'      # Azul
        }
        
        colors = [priority_colors.get(priority, '#95A5A6') for priority in priority_data.keys()]
        
        fig = px.bar(
            x=list(priority_data.keys()),
            y=list(priority_data.values()),
            title="<b>Issues por Prioridad</b>",
            color=list(priority_data.values()),
            color_discrete_sequence=colors,
            text=list(priority_data.values())
        )
        
        fig.update_traces(
            texttemplate='%{text}',
            textposition='outside',
            marker={
                'line': {'color': 'rgba(255,255,255,0.8)', 'width': 1},
                'opacity': 0.8
            },
            hovertemplate="<b>%{x}</b><br>" +
                        "Issues: %{y}<br>" +
                        HOVER_EXTRA
        )
        
        fig.update_layout(
            font={'family': FONT_FAMILY, 'size': STANDARD_FONT_SIZE},
            plot_bgcolor=TRANSPARENT_BG,
            paper_bgcolor=TRANSPARENT_BG,
            xaxis={
                'title': "<b>Prioridad</b>",
                'title_font': {'size': TITLE_FONT_SIZE},
                'tickfont': {'size': STANDARD_FONT_SIZE},
                'gridcolor': GRID_COLOR
            },
            yaxis={
                'title': Y_AXIS_TITLE,
                'title_font': {'size': TITLE_FONT_SIZE},
                'tickfont': {'size': STANDARD_FONT_SIZE},
                'gridcolor': GRID_COLOR
            },
            showlegend=False,
            margin=DEFAULT_MARGIN
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_timeline_section(issues, processor):
    """Renderiza la sección de timeline de actualizaciones."""
    st.subheader("📈 Timeline de Actualizaciones (últimos 30 días)")
    timeline_data = processor.get_timeline_data(issues, 30)
    if timeline_data['dates']:
        fig = go.Figure()
        
        # Línea principal con gradiente
        fig.add_trace(go.Scatter(
            x=timeline_data['dates'],
            y=timeline_data['counts'],
            mode='lines+markers',
            name='Actualizaciones',
            line={
                'color': 'rgba(102, 126, 234, 1)',
                'width': 3,
                'shape': 'spline',
                'smoothing': 0.3
            },
            marker={
                'size': 8,
                'color': 'rgba(102, 126, 234, 1)',
                'line': {'color': 'rgba(255, 255, 255, 0.8)', 'width': 2}
            },
            fill='tonexty',
            fillcolor='rgba(102, 126, 234, 0.1)',
            hovertemplate="<b>%{x}</b><br>" +
                        "Issues actualizados: %{y}<br>" +
                        "<extra></extra>"
        ))
        
        # Línea de media móvil (7 días)
        if len(timeline_data['counts']) >= 7:
            moving_avg = []
            for i in range(len(timeline_data['counts'])):
                start_idx = max(0, i - 3)
                end_idx = min(len(timeline_data['counts']), i + 4)
                avg = sum(timeline_data['counts'][start_idx:end_idx]) / (end_idx - start_idx)
                moving_avg.append(avg)
            
            fig.add_trace(go.Scatter(
                x=timeline_data['dates'],
                y=moving_avg,
                mode='lines',
                name='Media Móvil (7 días)',
                line={
                    'color': 'rgba(243, 156, 18, 0.8)',
                    'width': 2,
                    'dash': 'dash'
                },
                hovertemplate="<b>%{x}</b><br>" +
                            "Media móvil: %{y:.1f}<br>" +
                            "<extra></extra>"
            ))
        
        fig.update_layout(
            title="<b>Evolución de Actualizaciones de Issues</b>",
            xaxis={
                'title': "<b>Fecha</b>",
                'title_font': {'size': 14},
                'tickfont': {'size': 12},
                'gridcolor': 'rgba(128,128,128,0.2)',
                'showgrid': True
            },
            yaxis={
                'title': "<b>Número de Issues</b>",
                'title_font': {'size': 14},
                'tickfont': {'size': 12},
                'gridcolor': 'rgba(128,128,128,0.2)',
                'showgrid': True
            },
            hovermode='x unified',
            font={'family': "Arial, sans-serif", 'size': 12},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend={
                'orientation': "h",
                'yanchor': "bottom",
                'y': 1.02,
                'xanchor': "right",
                'x': 1
            },
            margin=TIMELINE_MARGIN
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Estadísticas adicionales del timeline
        if timeline_data['counts']:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_updates = sum(timeline_data['counts'])
                st.metric("📊 Total Actualizaciones", format_number(total_updates))
            
            with col2:
                avg_daily = total_updates / len(timeline_data['counts']) if timeline_data['counts'] else 0
                st.metric("📈 Promedio Diario", f"{avg_daily:.1f}")
            
            with col3:
                max_day = max(timeline_data['counts']) if timeline_data['counts'] else 0
                st.metric("🔥 Pico Máximo", format_number(max_day))
            
            with col4:
                active_days = sum(1 for count in timeline_data['counts'] if count > 0)
                st.metric("📅 Días Activos", format_number(active_days))


def render_projects_section(issues, processor):
    """Renderiza la sección de distribución por proyecto."""
    # Gráfico adicional: Distribución por Proyecto
    st.markdown("---")
    st.subheader("🏢 Distribución por Proyecto")
    
    project_summary = processor.get_project_summary(issues)
    if project_summary and len(project_summary) > 1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Gráfico de barras horizontales para proyectos
            projects = list(project_summary.keys())
            counts = list(project_summary.values())
            
            fig = px.bar(
                x=counts,
                y=projects,
                orientation='h',
                title="<b>Issues por Proyecto</b>",
                color=counts,
                color_continuous_scale="Blues",
                text=counts
            )
            
            fig.update_traces(
                texttemplate='%{text}',
                textposition='outside',
                hovertemplate="<b>%{y}</b><br>" +
                            "Issues: %{x}<br>" +
                            "Porcentaje: %{customdata:.1f}%<br>" +
                            "<extra></extra>",
                customdata=[count/sum(counts)*100 for count in counts]
            )
            
            fig.update_layout(
                font={'family': "Arial, sans-serif", 'size': 12},
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis={
                    'title': "<b>Número de Issues</b>",
                    'title_font': {'size': 14},
                    'tickfont': {'size': 12},
                    'gridcolor': 'rgba(128,128,128,0.2)'
                },
                yaxis={
                    'title': "<b>Proyecto</b>",
                    'title_font': {'size': 14},
                    'tickfont': {'size': 12}
                },
                showlegend=False,
                margin={'t': 50, 'b': 50, 'l': 100, 'r': 50},
                height=max(300, len(projects) * 40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Tabla resumen de proyectos
            st.markdown("**📊 Resumen por Proyecto**")
            
            project_df = pd.DataFrame([
                {
                    "Proyecto": k,
                    "Issues": v,
                    "Porcentaje": f"{(v/len(issues)*100):.1f}%"
                }
                for k, v in project_summary.items()
            ]).sort_values("Issues", ascending=False)
            
            st.dataframe(
                project_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Proyecto": st.column_config.TextColumn("📁 Proyecto", width="medium"),
                    "Issues": st.column_config.NumberColumn("📊 Issues", width="small"),
                    "Porcentaje": st.column_config.TextColumn("📈 %", width="small")
                }
            )
            
            # Estadística destacada
            if project_df.shape[0] > 0:
                top_project = project_df.iloc[0]
                st.success(f"🏆 **Proyecto Principal:** {top_project['Proyecto']}")
                st.info(f"📊 **{top_project['Issues']} issues** ({top_project['Porcentaje']})")
    else:
        st.info("📝 Todos los issues pertenecen al mismo proyecto o no hay datos suficientes para mostrar distribución.")


def render_issues_list():
    """Renderiza la lista de issues con diseño mejorado."""
    if not st.session_state.cached_issues:
        st.info("📭 No hay datos cargados. Usa la barra lateral para obtener datos.")
        return
    
    issues = st.session_state.cached_issues
    processor = st.session_state.data_processor
    
    st.subheader(f"📋 Lista de Issues ({len(issues)} encontrados)")
    
    # Opciones de visualización
    view_mode = st.radio(
        "Modo de Visualización:",
        ["📊 Tabla Detallada", "🎴 Cards Elegantes"],
        horizontal=True,
        key="view_mode"
    )
    
    st.markdown("---")
    
    # Filtros adicionales
    with st.expander("🔍 Filtros Avanzados", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtro por estado
            all_statuses = [
                issue.get('fields', {}).get('status', {}).get('name', 'Unknown')
                for issue in issues
            ]
            unique_statuses = list(set(all_statuses))
            selected_statuses = st.multiselect(
                "Estado",
                unique_statuses,
                default=unique_statuses,
                key="status_filter"
            )
        
        with col2:
            # Filtro por proyecto
            all_projects = [
                issue.get('fields', {}).get('project', {}).get('key', 'Unknown')
                for issue in issues
            ]
            unique_projects = list(set(all_projects))
            selected_projects = st.multiselect(
                "Proyecto",
                unique_projects,
                default=unique_projects,
                key="project_filter"
            )
        
        with col3:
            # Filtro por prioridad
            all_priorities = [
                issue.get('fields', {}).get('priority', {}).get('name', 'Unknown')
                for issue in issues
            ]
            unique_priorities = list(set(all_priorities))
            selected_priorities = st.multiselect(
                "Prioridad",
                unique_priorities,
                default=unique_priorities,
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
    
    # Mostrar según el modo seleccionado
    if filtered_issues:
        if view_mode == "🎴 Cards Elegantes":
            render_issues_cards(filtered_issues)
        else:
            render_issues_table(filtered_issues, processor)
        
        st.success(f"✨ Mostrando {len(filtered_issues)} de {len(issues)} issues")
    else:
        st.warning("🔍 No hay issues que coincidan con los filtros seleccionados")


def render_issues_cards(issues):
    """Renderiza issues como cards elegantes."""
    base_url = st.session_state.jira_client.base_url if st.session_state.jira_client else "https://your-jira.atlassian.net"
    
    # Paginación
    items_per_page = 6
    total_pages = (len(issues) + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        page = st.selectbox(
            "📄 Página",
            range(1, total_pages + 1),
            format_func=lambda x: f"Página {x} de {total_pages}",
            key="page_selector"
        )
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_issues = issues[start_idx:end_idx]
    else:
        page_issues = issues[:items_per_page]
    
    # Renderizar cards en columnas
    for i in range(0, len(page_issues), 2):
        col1, col2 = st.columns(2)
        
        # Card izquierda
        with col1:
            if i < len(page_issues):
                render_issue_card(page_issues[i], base_url)
        
        # Card derecha  
        with col2:
            if i + 1 < len(page_issues):
                render_issue_card(page_issues[i + 1], base_url)


def render_issue_card(issue, base_url):
    """Renderiza una card individual para un issue usando componentes nativos de Streamlit."""
    fields = issue.get('fields', {})
    key = issue.get('key', 'N/A')
    summary = fields.get('summary', 'Sin título')
    status = fields.get('status', {}).get('name', 'Unknown')
    priority = fields.get('priority', {}).get('name', 'Unknown')
    project = fields.get('project', {}).get('key', 'Unknown')
    assignee = fields.get('assignee', {})
    assignee_name = assignee.get('displayName', 'Sin asignar') if assignee else 'Sin asignar'
    updated = fields.get('updated', '')
    
    # URL del issue
    issue_url = f"{base_url}/browse/{key}"
    
    # Colores por prioridad
    priority_colors = {
        'Highest': '🔴',
        'High': '🟠', 
        'Medium': '🟡',
        'Low': '🟢',
        'Lowest': '🔵'
    }
    priority_icon = priority_colors.get(priority, '⚪')
    
    # Colores por estado
    status_colors = {
        'NUEVA': '🆕',
        'EN CURSO': '⚡',
        'ESCALADO': '🚨',
        'ANÁLISIS': '🔍',
        'CERRADA': '✅',
        'RESUELTA': '✅'
    }
    status_icon = status_colors.get(status, '📋')
    
    # Formatear fecha
    if updated:
        try:
            dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
            formatted_date = dt.strftime('%d/%m/%y %H:%M')
        except (ValueError, TypeError):
            formatted_date = updated[:10]
    else:
        formatted_date = 'N/A'
    
    # Card usando componentes nativos de Streamlit
    with st.container():
        # Crear un contenedor con borde
        st.markdown("---")
        
        # Título con icono de estado
        st.markdown(f"### {status_icon} **{key}**")
        
        # Resumen del issue
        summary_short = summary[:100] + '...' if len(summary) > 100 else summary
        st.markdown(f"**📝 Resumen:** {summary_short}")
        
        # Información en columnas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**📁 Proyecto:** `{project}`")
            st.markdown(f"**{priority_icon} Prioridad:** `{priority}`")
        
        with col2:
            st.markdown(f"**👤 Asignado:** {assignee_name}")
            st.markdown(f"**📅 Actualizado:** {formatted_date}")
        
        # Estado con color
        if status in ['CERRADA', 'RESUELTA']:
            st.success(f"📊 Estado: {status}")
        elif status in ['EN CURSO', 'ESCALADO']:
            st.info(f"📊 Estado: {status}")
        elif status == 'NUEVA':
            st.warning(f"� Estado: {status}")
        else:
            st.info(f"📊 Estado: {status}")
        
        # Botón para ir a Jira
        col1, col2, _ = st.columns([1, 2, 1])
        with col2:
            if st.button(f"🔗 Ver {key} en Jira", key=f"jira_{key}", use_container_width=True, type="primary"):
                st.success(f"🚀 Abriendo {key} en Jira...")
                st.markdown(f"**Enlace directo:** [{key}]({issue_url})")
                st.balloons()
        
        st.markdown("---")


def render_issues_table(filtered_issues, processor):
    """Renderiza issues como tabla detallada."""
    df = processor.format_issues_for_display(filtered_issues)
    
    # Agregar columna de enlace
    base_url = st.session_state.jira_client.base_url if st.session_state.jira_client else "https://your-jira.atlassian.net"
    df['🔗 Enlace'] = df['Key'].apply(lambda key: f"{base_url}/browse/{key}")
    
    # Calcular altura dinámica basada en número de registros
    # Mínimo 400px, máximo 1200px, ~35px por fila + header
    num_rows = len(df)
    dynamic_height = min(max(400, (num_rows * 35) + 100), 1200)
    
    # Mostrar información sobre la tabla
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info(f"📊 **Mostrando {num_rows} issues** - Tabla con altura dinámica")
    with col2:
        if num_rows > 100:
            st.warning(f"⚠️ Tabla grande detectada ({num_rows} filas)")
    
    # Hacer que la tabla sea más interactiva
    st.dataframe(
        df,
        use_container_width=True,
        height=dynamic_height,
        column_config={
            "Key": st.column_config.TextColumn("🔑 Clave", width="small"),
            "Summary": st.column_config.TextColumn("📝 Resumen", width="large"),
            "Status": st.column_config.TextColumn("📊 Estado", width="small"),
            "Priority": st.column_config.TextColumn("⚡ Prioridad", width="small"),
            "Project": st.column_config.TextColumn("📁 Proyecto", width="small"),
            "Assignee": st.column_config.TextColumn("👤 Asignado", width="medium"),
            "Updated": st.column_config.DatetimeColumn("📅 Actualizado", width="medium"),
            "🔗 Enlace": st.column_config.LinkColumn(
                "🔗 Ver en Jira",
                help="Haz clic para abrir en Jira",
                width="medium"
            )
        }
    )


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
            line={'color': '#667eea', 'width': 2},
            marker={'size': 6}
        ))
        
        # Media móvil
        if len(timeline_data['counts']) > 7:
            moving_avg = pd.Series(timeline_data['counts']).rolling(window=7).mean()
            fig.add_trace(go.Scatter(
                x=timeline_data['dates'],
                y=moving_avg,
                mode='lines',
                name='Media Móvil (7 días)',
                line={'color': '#f39c12', 'width': 2, 'dash': 'dash'}
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