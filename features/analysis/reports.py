"""
Componentes de análisis y exportación.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict, Any
from shared.utils import format_number, parse_jira_datetime, calculate_age_days
from core.config import Config


def render_analysis():
    """Renderiza la vista de análisis avanzado."""
    if not st.session_state.cached_issues:
        st.info("📭 No hay datos cargados. Usa la barra lateral para obtener datos.")
        return
    
    issues = st.session_state.cached_issues
    processor = st.session_state.data_processor
    
    st.header("🔍 Análisis Avanzado")
    
    # Pestañas de análisis
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Tendencias", 
        "👥 Equipo", 
        "⏱️ Tiempo", 
        "📊 Patrones"
    ])
    
    with tab1:
        render_trends_analysis(issues, processor)
    
    with tab2:
        render_team_analysis(issues, processor)
    
    with tab3:
        render_time_analysis(issues, processor)
    
    with tab4:
        render_patterns_analysis(issues, processor)


def render_trends_analysis(issues: List[Dict[str, Any]], processor):
    """Análisis de tendencias temporales."""
    st.subheader("📈 Análisis de Tendencias")
    
    # Selector de período
    timeline_days = st.selectbox(
        "Período de Análisis",
        [7, 15, 30, 60, 90],
        index=2,
        format_func=lambda x: f"Últimos {x} días"
    )
    
    # Gráfico de tendencias
    timeline_data = processor.get_timeline_data(issues, timeline_days)
    
    if timeline_data['dates']:
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
        
        st.plotly_chart(fig, use_container_width=True, key="timeline_trend_line")
        
        # Estadísticas de tendencia
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total = sum(timeline_data['counts'])
            st.metric("Total Actualizaciones", total)
        
        with col2:
            avg = total / len(timeline_data['counts']) if timeline_data['counts'] else 0
            st.metric("Promedio Diario", f"{avg:.1f}")
        
        with col3:
            peak = max(timeline_data['counts']) if timeline_data['counts'] else 0
            st.metric("Pico Máximo", peak)


def render_team_analysis(issues: List[Dict[str, Any]], processor):
    """Análisis del equipo y asignaciones."""
    st.subheader("👥 Análisis del Equipo")
    
    # Obtener datos de asignees
    assignee_data = {}
    for issue in issues:
        assignee = issue.get('fields', {}).get('assignee')
        if assignee:
            name = assignee.get('displayName', 'Sin nombre')
            assignee_data[name] = assignee_data.get(name, 0) + 1
        else:
            assignee_data['Sin asignar'] = assignee_data.get('Sin asignar', 0) + 1
    
    if assignee_data:
        # Gráfico de barras de asignaciones
        fig = px.bar(
            x=list(assignee_data.values()),
            y=list(assignee_data.keys()),
            orientation='h',
            title="Distribución de Issues por Asignee",
            labels={'x': 'Número de Issues', 'y': 'Asignee'}
        )
        
        fig.update_layout(height=max(300, len(assignee_data) * 40))
        st.plotly_chart(fig, use_container_width=True, key="assignee_distribution_bar")
        
        # Tabla detallada
        st.markdown("### 📊 Detalle por Asignee")
        
        assignee_df = pd.DataFrame([
            {
                'Asignee': name,
                'Issues': count,
                'Porcentaje': f"{(count/len(issues)*100):.1f}%"
            }
            for name, count in sorted(assignee_data.items(), key=lambda x: x[1], reverse=True)
        ])
        
        st.dataframe(assignee_df, use_container_width=True, hide_index=True)


def render_time_analysis(issues: List[Dict[str, Any]], processor):
    """Análisis temporal detallado."""
    st.subheader("⏱️ Análisis Temporal")
    
    # Análisis por día de la semana
    weekday_data = {i: 0 for i in range(7)}  # 0=Lunes, 6=Domingo
    weekday_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    for issue in issues:
        created = issue.get('fields', {}).get('created', '')
        if created:
            try:
                # Usar la función utilitaria para parsear fechas de forma segura
                created_date = parse_jira_datetime(created)
                if created_date:
                    created_date.weekday()  # 0=Lunes, 6=Domingo
                    weekday_data[created_date.weekday()] += 1
            except (ValueError, AttributeError):
                continue
    
    # Gráfico de días de la semana
    fig = px.bar(
        x=weekday_names,
        y=[weekday_data[i] for i in range(7)],
        title="Issues Creados por Día de la Semana",
        labels={'x': 'Día de la Semana', 'y': 'Número de Issues'}
    )
    
    st.plotly_chart(fig, use_container_width=True, key="weekday_creation_bar")
    
    # Análisis de edad de issues
    st.markdown("### 📅 Edad de Issues")
    
    today = datetime.now()
    age_ranges = {'< 1 semana': 0, '1-4 semanas': 0, '1-3 meses': 0, '> 3 meses': 0}
    
    for issue in issues:
        created = issue.get('fields', {}).get('created', '')
        if created:
            # Usar la función utilitaria para calcular edad
            age_days = calculate_age_days(created)
            
            if age_days < 7:
                age_ranges['< 1 semana'] += 1
            elif age_days < 28:
                age_ranges['1-4 semanas'] += 1
            elif age_days < 90:
                age_ranges['1-3 meses'] += 1
            else:
                age_ranges['> 3 meses'] += 1
    
    # Gráfico de edad
    fig = px.pie(
        values=list(age_ranges.values()),
        names=list(age_ranges.keys()),
        title="Distribución por Edad de Issues"
    )
    
    st.plotly_chart(fig, use_container_width=True, key="age_distribution_pie")


def render_patterns_analysis(issues: List[Dict[str, Any]], processor):
    """Análisis de patrones y correlaciones."""
    st.subheader("📊 Análisis de Patrones")
    
    # Matriz de correlación Estado vs Prioridad
    status_priority_matrix = {}
    
    for issue in issues:
        status = issue.get('fields', {}).get('status', {}).get('name', 'Sin Estado')
        priority = issue.get('fields', {}).get('priority', {}).get('name', 'Sin Prioridad')
        
        key = f"{status} - {priority}"
        status_priority_matrix[key] = status_priority_matrix.get(key, 0) + 1
    
    if status_priority_matrix:
        # Crear DataFrame para la matriz
        matrix_data = []
        for combo, count in status_priority_matrix.items():
            if ' - ' in combo:
                status, priority = combo.split(' - ', 1)
                matrix_data.append({
                    'Estado': status,
                    'Prioridad': priority,
                    'Cantidad': count
                })
        
        if matrix_data:
            df = pd.DataFrame(matrix_data)
            
            # Crear tabla pivote
            pivot_table = df.pivot_table(
                values='Cantidad', 
                index='Estado', 
                columns='Prioridad', 
                fill_value=0
            )
            
            st.markdown("### 🔄 Matriz Estado vs Prioridad")
            st.dataframe(pivot_table, use_container_width=True)
            
            # Heatmap
            fig = px.imshow(
                pivot_table.values,
                x=pivot_table.columns,
                y=pivot_table.index,
                title="Mapa de Calor: Estado vs Prioridad",
                labels={'x': 'Prioridad', 'y': 'Estado'},
                color_continuous_scale='Blues'
            )
            
            st.plotly_chart(fig, use_container_width=True, key="status_priority_heatmap")


def render_export():
    """Renderiza la vista de exportación de datos."""
    if not st.session_state.cached_issues:
        st.info("📭 No hay datos cargados. Usa la barra lateral para obtener datos.")
        return
    
    issues = st.session_state.cached_issues
    
    st.header("📤 Exportar Datos")
    
    # Formatos de exportación
    st.subheader("📊 Formatos Disponibles")
    
    # Preparar datos para exportación
    export_data = prepare_export_data(issues)
    
    # Botones de descarga en fila
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data = export_data.to_csv(index=False)
        st.download_button(
            label="📄 Descargar CSV",
            data=csv_data,
            file_name=f"jira_issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        excel_data = export_to_excel(export_data)
        st.download_button(
            label="📊 Descargar Excel",
            data=excel_data,
            file_name=f"jira_issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col3:
        json_data = export_data.to_json(orient='records', indent=2)
        st.download_button(
            label="📋 Descargar JSON",
            data=json_data,
            file_name=f"jira_issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Estadísticas de Exportación (ocupando toda la pantalla)
    st.subheader("📈 Estadísticas de Exportación")
    
    st.metric("📊 Total Issues", len(issues))
    st.metric("📁 Columnas", len(export_data.columns))
    st.metric("💾 Tamaño Estimado (CSV)", f"{len(csv_data) / 1024:.1f} KB")
    
    # Preview de los datos
    st.markdown("### 👀 Vista Previa")
    
    # Configuración de paginación
    col_preview_config, col_info = st.columns([1, 2])
    
    with col_preview_config:
        rows_per_page_options = [10, 20, 50, 100]
        rows_per_page = st.selectbox(
            "Registros por página:",
            options=rows_per_page_options,
            index=1,  # 20 por defecto
            key="preview_rows_per_page",
            help="Número de registros a mostrar por página en la vista previa"
        )
    
    with col_info:
        st.markdown("""
        **ℹ️ Información sobre límites:**
        - **Máximo 100 registros**: Viene de la configuración por defecto (`JIRA_MAX_RESULTS_DEFAULT=100`)
        - **Cambiar límite**: Modifica la variable de entorno o usa el slider en la barra lateral (hasta 1000)
        - **Paginación**: Navega por todos los registros disponibles
        """)
    
    # Obtener base_url para enlaces
    base_url = None
    try:
        jira_config = Config.get_jira_config()
        base_url = jira_config.base_url.rstrip('/')
    except:
        pass
    
    # Paginación para la vista previa
    total_rows = len(export_data)
    total_pages = (total_rows + rows_per_page - 1) // rows_per_page  # Ceiling division
    
    if total_pages > 1:
        page_options = [f"Página {i+1} ({i*rows_per_page + 1}-{(i+1)*rows_per_page if (i+1)*rows_per_page < total_rows else total_rows})" for i in range(total_pages)]
        selected_page = st.selectbox("Seleccionar página:", page_options, key="preview_page")
        current_page = page_options.index(selected_page)
        start_idx = current_page * rows_per_page
        end_idx = min(start_idx + rows_per_page, total_rows)
        preview_data = export_data.iloc[start_idx:end_idx]
    else:
        preview_data = export_data
    
    if not preview_data.empty:
        # Construir tabla Markdown con enlaces
        headers = ["Key", "Summary", "Status", "Priority", "Assignee", "Project", "Created", "Updated", "Issue Type"]
        table_md = "| " + " | ".join(headers) + " |\n"
        table_md += "|" + "|".join(["---"] * len(headers)) + "|\n"
        
        for _, row in preview_data.iterrows():
            key = str(row['Key'])
            if base_url and key:
                key_display = f"[{key}]({base_url}/browse/{key})"
            else:
                key_display = key
            
            summary = str(row['Summary'])[:40] + "..." if len(str(row['Summary'])) > 40 else str(row['Summary'])
            status = str(row['Status'])
            priority = str(row['Priority'])
            assignee = str(row['Assignee'])
            project = str(row['Project'])
            created = str(row['Created'])[:10] if str(row['Created']) else ''  # Solo fecha
            updated = str(row['Updated'])[:10] if str(row['Updated']) else ''  # Solo fecha
            issue_type = str(row['Issue_Type'])
            
            table_md += f"| {key_display} | {summary} | {status} | {priority} | {assignee} | {project} | {created} | {updated} | {issue_type} |\n"
        
        st.markdown(table_md)
        
        # Mostrar información de paginación
        if total_pages > 1:
            st.markdown(f"**Mostrando {len(preview_data)} de {total_rows} registros (Página {current_page + 1} de {total_pages})**")
    else:
        st.info("No hay datos para mostrar")


def prepare_export_data(issues: List[Dict[str, Any]]) -> pd.DataFrame:
    """Prepara los datos para exportación."""
    export_data = []
    
    for issue in issues:
        fields = issue.get('fields', {})
        
        export_data.append({
            'Key': issue.get('key', ''),
            'Summary': fields.get('summary', ''),
            'Description': fields.get('description', ''),
            'Status': fields.get('status', {}).get('name', ''),
            'Priority': fields.get('priority', {}).get('name', ''),
            'Project': fields.get('project', {}).get('key', ''),
            'Project_Name': fields.get('project', {}).get('name', ''),
            'Assignee': fields.get('assignee', {}).get('displayName', '') if fields.get('assignee') else '',
            'Reporter': fields.get('reporter', {}).get('displayName', '') if fields.get('reporter') else '',
            'Created': fields.get('created', ''),
            'Updated': fields.get('updated', ''),
            'Resolution': fields.get('resolution', {}).get('name', '') if fields.get('resolution') else '',
            'Issue_Type': fields.get('issuetype', {}).get('name', ''),
            'Labels': ', '.join(fields.get('labels', [])),
            'Components': ', '.join([c.get('name', '') for c in fields.get('components', [])]),
            'Fix_Versions': ', '.join([v.get('name', '') for v in fields.get('fixVersions', [])])
        })
    
    return pd.DataFrame(export_data)


def export_to_excel(df: pd.DataFrame) -> bytes:
    """Convierte DataFrame a Excel en bytes."""
    from io import BytesIO
    
    output = BytesIO()
    
    try:
        # Intentar usar openpyxl para mejor formato
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Issues', index=False)
            
            # Ajustar ancho de columnas
            worksheet = writer.sheets['Issues']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
                
    except ImportError:
        # Fallback a xlsxwriter si openpyxl no esta disponible
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Issues', index=False)
    
    return output.getvalue()