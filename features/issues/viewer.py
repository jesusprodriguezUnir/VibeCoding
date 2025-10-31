"""
Componentes para la lista y gestión de issues.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from shared.utils import format_number
from shared.data_fetcher import load_more_issues, load_all_issues_batch


def render_issues_list():
    """Renderiza la lista de issues con diseño mejorado."""
    if not st.session_state.cached_issues:
        st.info("📭 No hay datos cargados. Usa la barra lateral para obtener datos.")
        return
    
    issues = st.session_state.cached_issues
    processor = st.session_state.data_processor
    
    # Mostrar información de paginación de Jira
    render_pagination_info()
    
    # Mostrar información sobre la consulta actual
    if 'last_query_params' in st.session_state:
        current_query = st.session_state.last_query_params.get('predefined_query', 'Desconocida')
        if current_query == 'Expedientes':
            st.info("📋 **Mostrando Expedientes**: Escalaciones de BAU Académico del área específica, creadas en las últimas 80 semanas, activas y sin resolver")
        elif current_query == 'Expedientes Sin Asignar':
            st.warning("🚨 **Expedientes Sin Asignar**: Escalaciones críticas que necesitan asignación inmediata de responsable")
        elif current_query == 'Pendientes':
            st.info("🚧 **Mostrando Issues Pendientes**: Issues asignados a ti con estados 'NUEVA', 'To Do', o 'ANÁLISIS'")
        elif current_query == 'En Progreso':
            st.info("⚡ **Mostrando Issues En Progreso**: Issues que están actualmente en desarrollo")
        elif current_query == 'Alta Prioridad':
            st.warning("🔥 **Mostrando Issues de Alta Prioridad**: Issues críticos que requieren atención inmediata")
    
    st.subheader(f"📋 Lista de Issues ({len(issues)} encontrados)")
    
    # Mensaje especial si no hay issues en consultas específicas
    if len(issues) == 0 and 'last_query_params' in st.session_state:
        current_query = st.session_state.last_query_params.get('predefined_query', '')
        if current_query == 'Pendientes':
            st.success("🎉 ¡Excelente! No tienes issues pendientes en este momento.")
            st.info("💡 Esto significa que no tienes tareas con estados 'NUEVA', 'To Do', o 'ANÁLISIS' asignadas.")
        elif current_query == 'En Progreso':
            st.info("📝 No tienes issues en progreso actualmente. Considera tomar un nuevo issue pendiente.")
        elif current_query == 'Alta Prioridad':
            st.success("✅ No tienes issues de alta prioridad pendientes. ¡Buen trabajo!")
        return
    
    # Opciones de visualización
    view_mode = st.radio(
        "Modo de Visualización:",
        ["📊 Tabla Detallada", "🎴 Cards Elegantes"],
        horizontal=True,
        help="Selecciona cómo quieres ver la información"
    )
    
    # Filtros interactivos
    filtered_issues = apply_filters(issues)
    
    if view_mode == "📊 Tabla Detallada":
        render_issues_table(filtered_issues, processor)
    else:
        render_issues_cards(filtered_issues)


def apply_filters(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Aplica filtros interactivos a la lista de issues."""
    with st.expander("🔍 Filtros Avanzados", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtro por estado
            all_statuses = list(set([
                issue.get('fields', {}).get('status', {}).get('name', 'Sin Estado') 
                for issue in issues
            ]))
            selected_statuses = st.multiselect(
                "Estados",
                options=all_statuses,
                default=all_statuses,
                help="Selecciona los estados a mostrar"
            )
        
        with col2:
            # Filtro por prioridad
            all_priorities = list(set([
                issue.get('fields', {}).get('priority', {}).get('name', 'Sin Prioridad') 
                for issue in issues
            ]))
            selected_priorities = st.multiselect(
                "Prioridades",
                options=all_priorities,
                default=all_priorities,
                help="Selecciona las prioridades a mostrar"
            )
        
        with col3:
            # Filtro por proyecto
            all_projects = list(set([
                issue.get('fields', {}).get('project', {}).get('key', 'Sin Proyecto') 
                for issue in issues
            ]))
            selected_projects = st.multiselect(
                "Proyectos",
                options=all_projects,
                default=all_projects,
                help="Selecciona los proyectos a mostrar"
            )
    
    # Aplicar filtros
    filtered = []
    for issue in issues:
        status = issue.get('fields', {}).get('status', {}).get('name', 'Sin Estado')
        priority = issue.get('fields', {}).get('priority', {}).get('name', 'Sin Prioridad')
        project = issue.get('fields', {}).get('project', {}).get('key', 'Sin Proyecto')
        
        if (status in selected_statuses and 
            priority in selected_priorities and 
            project in selected_projects):
            filtered.append(issue)
    
    st.info(f"📊 Mostrando {len(filtered)} de {len(issues)} issues")
    return filtered


def render_issues_table(filtered_issues: List[Dict[str, Any]], processor):
    """Renderiza la tabla de issues con configuración avanzada."""
    if not filtered_issues:
        st.warning("🔍 No hay issues que coincidan con los filtros seleccionados.")
        return
    
    base_url = st.session_state.get('base_url', '')
    
    # Preparar datos para la tabla
    table_data = []
    for issue in filtered_issues:
        fields = issue.get('fields', {})
        key = issue.get('key', 'N/A')
        issue_url = f"{base_url}/browse/{key}" if base_url else "#"
        
        table_data.append({
            'Key': issue.get('key', 'N/A'),
            'Resumen': fields.get('summary', 'Sin resumen'),
            'Estado': fields.get('status', {}).get('name', 'Sin estado'),
            'Prioridad': fields.get('priority', {}).get('name', 'Sin prioridad'),
            'Proyecto': fields.get('project', {}).get('key', 'N/A'),
            'Asignado': fields.get('assignee', {}).get('displayName', 'Sin asignar') if fields.get('assignee') else 'Sin asignar',
            'Creado': fields.get('created', 'N/A')[:10] if fields.get('created') else 'N/A',
            'Actualizado': fields.get('updated', 'N/A')[:10] if fields.get('updated') else 'N/A',
            'Jira Link': issue_url
        })
    
    df = pd.DataFrame(table_data)
    
    # Botones de exportación
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
    
    with col1:
        if st.button("📊 Exportar Excel", help="Exportar datos a archivo Excel"):
            export_to_excel(df, "expedientes_jira")
    
    with col2:
        if st.button("📄 Exportar PDF", help="Exportar datos a archivo PDF"):
            export_to_pdf(df, "expedientes_jira")
    
    with col3:
        if st.button("💾 Exportar CSV", help="Exportar datos a archivo CSV"):
            export_to_csv(df, "expedientes_jira")
    
    # Configurar la tabla con altura dinámica
    num_rows = len(df)
    height = min(max(400, num_rows * 35 + 100), 1200)
    
    st.dataframe(
        df,
        width="stretch",  # Reemplaza use_container_width=True
        hide_index=True,
        height=height,
        column_config={
            "Key": st.column_config.TextColumn("🔑 Key", width="small"),  # Más pequeño (la mitad)
            "Resumen": st.column_config.TextColumn("📝 Resumen", width="large"),  # Más grande
            "Estado": st.column_config.TextColumn("📊 Estado", width="small"),  # Más pequeño (la mitad)
            "Prioridad": st.column_config.TextColumn("🔥 Prioridad", width="small"),  # Mantener pequeño
            "Proyecto": st.column_config.TextColumn("📁 Proyecto", width="small"),
            "Asignado": st.column_config.TextColumn("👤 Asignado", width="small"),  # Mantener pequeño
            "Creado": st.column_config.DateColumn("📅 Creado", width="small"),
            "Actualizado": st.column_config.DateColumn("🔄 Actualizado", width="small"),
            "Jira Link": st.column_config.LinkColumn("🔗 Ver en Jira", width="large")  # Más grande
        }
    )
    
    # Métricas de la tabla
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total Issues", len(df))
    with col2:
        in_progress = len(df[df['Estado'].isin(['EN CURSO', 'In Progress', 'ESCALADO'])])
        st.metric("🔥 En Progreso", in_progress)
    with col3:
        high_priority = len(df[df['Prioridad'].isin(['Alto', 'High', 'Crítico', 'Highest'])])
        st.metric("⚡ Alta Prioridad", high_priority)
    with col4:
        projects = df['Proyecto'].nunique()
        st.metric("📁 Proyectos", projects)


def render_issues_cards(issues: List[Dict[str, Any]]):
    """Renderiza los issues como cards elegantes."""
    if not issues:
        st.warning("🔍 No hay issues que coincidan con los filtros seleccionados.")
        return
    
    # Configuración de paginación
    items_per_page = 10
    total_pages = (len(issues) + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        page = st.selectbox(
            "📄 Página",
            range(1, total_pages + 1),
            format_func=lambda x: f"Página {x} de {total_pages}"
        )
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(issues))
        page_issues = issues[start_idx:end_idx]
    else:
        page_issues = issues
    
    # Renderizar cards
    for issue in page_issues:
        render_issue_card(issue, st.session_state.get('base_url', ''))


def render_issue_card(issue: Dict[str, Any], base_url: str):
    """Renderiza un card individual de issue."""
    fields = issue.get('fields', {})
    key = issue.get('key', 'N/A')
    
    # Obtener información
    summary = fields.get('summary', 'Sin resumen')
    status = fields.get('status', {}).get('name', 'Sin estado')
    priority = fields.get('priority', {}).get('name', 'Sin prioridad')
    project = fields.get('project', {}).get('key', 'N/A')
    assignee = fields.get('assignee', {}).get('displayName', 'Sin asignar') if fields.get('assignee') else 'Sin asignar'
    
    # Determinar colores según estado y prioridad
    status_color = get_status_color(status)
    priority_color = get_priority_color(priority)
    
    # URL del issue
    issue_url = f"{base_url}/browse/{key}" if base_url else "#"
    
    # Crear el card usando columnas nativas de Streamlit
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### � {key}")
            st.markdown(f"**📝 {summary}**")
            
            subcol1, subcol2 = st.columns(2)
            with subcol1:
                st.markdown(f"📁 **Proyecto:** {project}")
                st.markdown(f"👤 **Asignado:** {assignee}")
            
            with subcol2:
                st.markdown(f"📊 **Estado:** {status}")
                st.markdown(f"🔥 **Prioridad:** {priority}")
        
        with col2:
            # Badges de estado
            st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <div style="background-color: {status_color}; color: white; padding: 5px 10px; border-radius: 15px; margin: 5px 0; font-size: 12px;">
                    {status}
                </div>
                <div style="background-color: {priority_color}; color: white; padding: 5px 10px; border-radius: 15px; margin: 5px 0; font-size: 12px;">
                    {priority}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Botón para ir a Jira
            if base_url:
                st.link_button(
                    "🔗 Ver en Jira",
                    issue_url,
                    use_container_width=True
                )
        
        st.markdown("---")


def get_status_color(status: str) -> str:
    """Retorna el color correspondiente al estado."""
    status_colors = {
        'To Do': '#6c757d',
        'In Progress': '#007bff',
        'EN CURSO': '#007bff',
        'ESCALADO': '#dc3545',
        'Done': '#28a745',
        'Closed': '#6c757d',
        'Resolved': '#28a745'
    }
    return status_colors.get(status, '#6c757d')


def get_priority_color(priority: str) -> str:
    """Retorna el color correspondiente a la prioridad."""
    priority_colors = {
        'Highest': '#dc3545',
        'High': '#fd7e14',
        'Alto': '#fd7e14',
        'Crítico': '#dc3545',
        'Medium': '#ffc107',
        'Low': '#28a745',
        'Lowest': '#6c757d'
    }
    return priority_colors.get(priority, '#6c757d')


def render_pagination_info():
    """Renderiza información y controles de paginación de Jira."""
    pagination = st.session_state.get('pagination_info')
    
    if not pagination:
        return
    
    try:
        total = pagination.get('total', 0)
        start_at = pagination.get('start_at', 0) 
        max_results = pagination.get('max_results', 1)  # Default a 1 para evitar división por cero
        has_more = pagination.get('has_more', False)
        
        # Validar que max_results sea válido
        if max_results <= 0:
            st.error(f"❌ Error en configuración de paginación: max_results={max_results}")
            st.write("Datos de paginación:", pagination)
            return
        
        # Calcular información de página
        current_page = (start_at // max_results) + 1
        total_pages = (total + max_results - 1) // max_results
        showing_from = start_at + 1
        showing_to = min(start_at + max_results, total)
        
    except Exception as e:
        st.error(f"❌ Error procesando paginación: {str(e)}")
        st.write("Datos de paginación:", pagination)
        return
    
    # Información de paginación
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if total > max_results:
            st.info(f"📄 Mostrando {showing_from:,}-{showing_to:,} de {total:,} issues totales (Página {current_page} de {total_pages})")
            if pagination.get('batch_loaded'):
                st.success(f"✅ Carga por lotes: {pagination.get('batch_size', 0)} issues cargados")
            else:
                st.caption(f"🔧 Debug: start_at={start_at}, max_results={max_results}, total={total}")
        else:
            st.info(f"📄 Mostrando todos los {total:,} issues encontrados")
            if total == max_results:
                st.warning(f"⚠️ Límite alcanzado: {total} issues. Puede haber más resultados - usa las opciones de carga masiva.")
    
    with col2:
        # Botón página anterior
        if current_page > 1 and not pagination.get('batch_loaded'):
            if st.button("⬅️ Página Anterior", key="prev_page"):
                load_more_issues(current_page - 1)
                st.rerun()
    
    with col3:
        # Botón página siguiente
        if has_more and not pagination.get('batch_loaded'):
            if st.button("➡️ Página Siguiente", key="next_page"):
                load_more_issues(current_page + 1)
                st.rerun()
    
    # Opciones de carga masiva
    if total > max_results:
        with st.expander("🚀 Opciones de Carga Masiva", expanded=False):
            st.markdown("**Cargar más issues de una vez:**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📥 Cargar 250", key="load_250"):
                    load_all_issues_batch(250)
            
            with col2:
                if st.button("📥 Cargar 500", key="load_500"):
                    load_all_issues_batch(500)
            
            with col3:
                if st.button("📥 Cargar 1000", key="load_1000"):
                    load_all_issues_batch(1000)
            
            with col4:
                if st.button("📥 Cargar Todo", key="load_all"):
                    load_all_issues_batch(total)
            
            st.markdown("---")
            
            # Carga personalizada
            col1, col2 = st.columns(2)
            with col1:
                custom_count = st.number_input(
                    "Cantidad personalizada:",
                    min_value=100,
                    max_value=min(5000, total),
                    value=500,
                    step=100,
                    key="custom_count"
                )
            
            with col2:
                if st.button("🎯 Cargar Cantidad", key="load_custom"):
                    load_all_issues_batch(custom_count)
            
            st.caption(f"💡 Total disponible: {total:,} issues. La carga masiva puede tardar unos segundos.")
    
    # Selector de página específica para navegación rápida (solo si no es carga masiva)
    if total_pages > 1 and not pagination.get('batch_loaded'):
        with st.expander("🔢 Ir a página específica", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                target_page = st.number_input(
                    "Número de página",
                    min_value=1,
                    max_value=total_pages,
                    value=current_page,
                    key="page_selector"
                )
            with col2:
                if st.button("🚀 Ir", key="go_to_page"):
                    if target_page != current_page:
                        load_more_issues(target_page)
                        st.rerun()
                    else:
                        st.info("Ya estás en esa página")
    
    # Botón para resetear a paginación normal
    if pagination.get('batch_loaded'):
        st.markdown("---")
        if st.button("🔄 Volver a Paginación Normal", key="reset_pagination"):
            # Resetear a la primera página con el tamaño original
            original_max = st.session_state.get('last_query_params', {}).get('max_results', 100)
            load_more_issues(1, original_max)
    
    st.markdown("---")


def export_to_excel(df: pd.DataFrame, filename: str):
    """Exporta DataFrame a Excel y permite descarga."""
    try:
        from io import BytesIO
        import xlsxwriter
        
        output = BytesIO()
        
        # Crear archivo Excel con formato
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Issues')
            
            # Obtener el workbook y worksheet para formato
            workbook = writer.book
            worksheet = writer.sheets['Issues']
            
            # Formato para encabezados
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BD',
                'border': 1
            })
            
            # Escribir encabezados con formato
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Ajustar ancho de columnas
            worksheet.set_column('A:A', 15)  # Key
            worksheet.set_column('B:B', 50)  # Resumen
            worksheet.set_column('C:C', 15)  # Estado
            worksheet.set_column('D:D', 12)  # Prioridad
            worksheet.set_column('E:E', 12)  # Proyecto
            worksheet.set_column('F:F', 20)  # Asignado
            worksheet.set_column('G:G', 12)  # Creado
            worksheet.set_column('H:H', 12)  # Actualizado
            worksheet.set_column('I:I', 30)  # Jira Link
        
        st.download_button(
            label="💾 Descargar Excel",
            data=output.getvalue(),
            file_name=f"{filename}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Haz clic para descargar el archivo Excel"
        )
        
    except ImportError:
        st.error("❌ Para exportar a Excel necesitas instalar: pip install xlsxwriter")
    except Exception as e:
        st.error(f"❌ Error exportando a Excel: {str(e)}")


def export_to_csv(df: pd.DataFrame, filename: str):
    """Exporta DataFrame a CSV y permite descarga."""
    try:
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="💾 Descargar CSV",
            data=csv,
            file_name=f"{filename}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="Haz clic para descargar el archivo CSV"
        )
        
    except Exception as e:
        st.error(f"❌ Error exportando a CSV: {str(e)}")


def export_to_pdf(df: pd.DataFrame, filename: str):
    """Exporta DataFrame a PDF y permite descarga."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from io import BytesIO
        
        buffer = BytesIO()
        
        # Crear documento PDF en orientación horizontal
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Título
        title = Paragraph(f"<b>Reporte de Issues - {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}</b>", styles['Title'])
        
        # Preparar datos para la tabla (limitar columnas para que quepa)
        pdf_data = []
        
        # Encabezados simplificados
        headers = ['Key', 'Resumen', 'Estado', 'Prioridad', 'Asignado']
        pdf_data.append(headers)
        
        # Datos (truncar resumen para que quepa)
        for _, row in df.iterrows():
            pdf_row = [
                str(row['Key'])[:15],
                str(row['Resumen'])[:40] + '...' if len(str(row['Resumen'])) > 40 else str(row['Resumen']),
                str(row['Estado'])[:15],
                str(row['Prioridad'])[:10],
                str(row['Asignado'])[:20]
            ]
            pdf_data.append(pdf_row)
        
        # Crear tabla
        table = Table(pdf_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        # Construir PDF
        elements = [title, table]
        doc.build(elements)
        
        st.download_button(
            label="💾 Descargar PDF",
            data=buffer.getvalue(),
            file_name=f"{filename}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            help="Haz clic para descargar el archivo PDF"
        )
        
    except ImportError:
        st.error("❌ Para exportar a PDF necesitas instalar: pip install reportlab")
    except Exception as e:
        st.error(f"❌ Error exportando a PDF: {str(e)}")