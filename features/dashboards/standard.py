"""
Componentes de dashboard y visualizaciones.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any
from shared.utils import format_number
from shared.ui.ui_utils import get_safe_issues, validate_issues_data


# Constantes para gráficos
FONT_FAMILY = "Arial, sans-serif"
TRANSPARENT_BG = 'rgba(0,0,0,0)'
GRID_COLOR = 'rgba(128,128,128,0.2)'
STANDARD_FONT_SIZE = 12
TITLE_FONT_SIZE = 14
DEFAULT_MARGIN = {"t": 50, "b": 50, "l": 50, "r": 50}
TIMELINE_MARGIN = {"t": 80, "b": 50, "l": 50, "r": 50}


def render_dashboard():
    """Renderiza el dashboard principal con métricas y gráficos."""
    if not validate_issues_data():
        st.info("📭 No hay datos cargados. Usa la barra lateral para obtener datos.")
        return
    
    issues = get_safe_issues()
    processor = st.session_state.data_processor
    
    # Validar que issues es una lista
    if not isinstance(issues, list):
        st.error("❌ Error: Los datos de issues no tienen el formato correcto.")
        return
    
    # Dividir en secciones modulares
    render_metrics_section(issues, processor)
    st.markdown("---")
    render_recent_issues_section(issues)
    st.markdown("---")
    render_charts_section(issues, processor)
    render_timeline_section(issues, processor)
    render_projects_section(issues, processor)


def render_metrics_section(issues: List[Dict[str, Any]], processor):
    """Renderiza la sección de métricas principales."""
    st.markdown("### 📊 **Resumen Ejecutivo**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_issues = len(issues)
        st.metric(
            label="📋 Total Issues",
            value=format_number(total_issues),
            help="Número total de issues recuperados"
        )
    
    with col2:
        # Issues en progreso
        in_progress_count = len([
            i for i in issues 
            if i.get('fields', {}).get('status', {}).get('name', '') in ['EN CURSO', 'In Progress', 'ESCALADO']
        ])
        percentage = (in_progress_count / total_issues * 100) if total_issues > 0 else 0
        st.metric(
            label="🔥 En Progreso",
            value=format_number(in_progress_count),
            delta=f"{percentage:.1f}%",
            help="Issues actualmente en progreso"
        )
    
    with col3:
        # Issues de alta prioridad
        high_priority_count = len([
            i for i in issues 
            if i.get('fields', {}).get('priority', {}).get('name', '') in ['Alto', 'High', 'Crítico', 'Highest']
        ])
        percentage = (high_priority_count / total_issues * 100) if total_issues > 0 else 0
        st.metric(
            label="⚡ Alta Prioridad",
            value=format_number(high_priority_count),
            delta=f"{percentage:.1f}%",
            help="Issues de prioridad alta o crítica"
        )
    
    with col4:
        # Issues actualizados hoy
        today_updates = get_today_updates(issues)
        st.metric(
            label="📅 Actualizados Hoy",
            value=format_number(today_updates),
            help="Issues actualizados en las últimas 24 horas"
        )


def get_today_updates(issues: List[Dict[str, Any]]) -> int:
    """Calcula el número de issues actualizados hoy."""
    from datetime import datetime, date
    
    today = date.today()
    today_updates = 0
    
    for issue in issues:
        try:
            updated = issue.get('fields', {}).get('updated', '')
            if updated:
                updated_date = datetime.fromisoformat(
                    updated.replace('Z', '+00:00')
                ).date()
                if updated_date == today:
                    today_updates += 1
        except (ValueError, TypeError):
            continue
    
    return today_updates


def render_recent_issues_section(issues: List[Dict[str, Any]]):
    """Renderiza la sección de issues recientes con enlaces a Jira."""
    st.markdown("### 🕒 **Issues Recientes**")
    
    base_url = st.session_state.get('base_url', '')
    
    # Ordenar por fecha de actualización (más recientes primero)
    sorted_issues = sorted(
        issues,
        key=lambda x: x.get('fields', {}).get('updated', ''),
        reverse=True
    )
    
    # Mostrar los 5 más recientes
    recent_issues = sorted_issues[:5]
    
    if not recent_issues:
        st.info("📭 No hay issues recientes para mostrar.")
        return
    
    for i, issue in enumerate(recent_issues, 1):
        fields = issue.get('fields', {})
        key = issue.get('key', 'N/A')
        summary = fields.get('summary', 'Sin resumen')
        status = fields.get('status', {}).get('name', 'Sin estado')
        updated = fields.get('updated', 'N/A')[:10] if fields.get('updated') else 'N/A'
        
        # URL del issue
        issue_url = f"{base_url}/browse/{key}" if base_url else "#"
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"**{i}. 🔑 {key}** - {summary[:80]}{'...' if len(summary) > 80 else ''}")
            st.markdown(f"📊 *{status}* • 📅 *Actualizado: {updated}*")
        
        with col2:
            if base_url:
                st.link_button(
                    "🔗 Ver",
                    issue_url,
                    use_container_width=True
                )
        
        if i < len(recent_issues):
            st.markdown("---")


def render_charts_section(issues: List[Dict[str, Any]], processor):
    """Renderiza la sección de gráficos principales."""
    col1, col2 = st.columns(2)
    
    with col1:
        render_status_pie_chart(issues, processor)
    
    with col2:
        render_priority_bar_chart(issues, processor)


def render_status_pie_chart(issues: List[Dict[str, Any]], processor):
    """Renderiza el gráfico de pastel de estados."""
    st.subheader("📈 Distribución por Estado")
    
    status_summary = processor.get_status_summary(issues)
    if status_summary:
        # Crear gráfico de pastel elegante
        fig = px.pie(
            values=list(status_summary.values()),
            names=list(status_summary.keys()),
            title="<b>Estados de Issues</b>",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate="<b>%{label}</b><br>" +
                        "Issues: %{value}<br>" +
                        "Porcentaje: %{percent}<br>" +
                        "<extra></extra>",
            marker_line={'color': '#000000', 'width': 2}
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
    else:
        st.info("📝 No hay suficientes datos para mostrar distribución por estado.")


def render_priority_bar_chart(issues: List[Dict[str, Any]], processor):
    """Renderiza el gráfico de barras de prioridades."""
    st.subheader("🔥 Distribución por Prioridad")
    
    priority_summary = processor.get_priority_summary(issues)
    if priority_summary:
        # Crear gráfico de barras elegante
        priorities = list(priority_summary.keys())
        counts = list(priority_summary.values())
        
        fig = px.bar(
            x=priorities,
            y=counts,
            title="<b>Prioridades de Issues</b>",
            color=counts,
            color_continuous_scale="Reds",
            text=counts
        )
        
        fig.update_traces(
            texttemplate='%{text}',
            textposition='outside',
            hovertemplate="<b>%{x}</b><br>" +
                        "Issues: %{y}<br>" +
                        "<extra></extra>"
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
                'title': "<b>Número de Issues</b>",
                'title_font': {'size': TITLE_FONT_SIZE},
                'tickfont': {'size': STANDARD_FONT_SIZE},
                'gridcolor': GRID_COLOR
            },
            showlegend=False,
            margin=DEFAULT_MARGIN
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📝 No hay suficientes datos para mostrar distribución por prioridad.")


def render_timeline_section(issues: List[Dict[str, Any]], processor):
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


def render_projects_section(issues: List[Dict[str, Any]], processor):
    """Renderiza la sección de distribución por proyecto."""
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