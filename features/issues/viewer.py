"""
Componentes para la lista y gestión de issues.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from shared.utils import format_number


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
    
    # Configurar la tabla con altura dinámica
    num_rows = len(df)
    height = min(max(400, num_rows * 35 + 100), 1200)
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=height,
        column_config={
            "Key": st.column_config.TextColumn("🔑 Key", width="small"),
            "Resumen": st.column_config.TextColumn("📝 Resumen", width="large"),
            "Estado": st.column_config.TextColumn("📊 Estado", width="medium"),
            "Prioridad": st.column_config.TextColumn("🔥 Prioridad", width="medium"),
            "Proyecto": st.column_config.TextColumn("📁 Proyecto", width="small"),
            "Asignado": st.column_config.TextColumn("👤 Asignado", width="medium"),
            "Creado": st.column_config.DateColumn("📅 Creado", width="small"),
            "Actualizado": st.column_config.DateColumn("🔄 Actualizado", width="small"),
            "Jira Link": st.column_config.LinkColumn("🔗 Ver en Jira", width="medium")
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