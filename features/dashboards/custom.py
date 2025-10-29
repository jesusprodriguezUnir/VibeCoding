"""
Sistema de configuración y renderizado de paneles personalizables.
"""
import streamlit as st
import json
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from .widgets import widget_registry, Widget, WidgetSize
from shared.ui.ui_utils import get_safe_issues, validate_issues_data
from features.jql.queries import render_jql_query_manager


@dataclass
class DashboardConfig:
    """Configuración de un dashboard."""
    name: str
    description: str
    widgets: List[str]  # IDs de widgets
    layout: Dict[str, Any]  # Configuración de layout


class DashboardManager:
    """Gestor de dashboards personalizables."""
    
    def __init__(self):
        self.default_dashboards = self._create_default_dashboards()
    
    def _create_default_dashboards(self) -> Dict[str, DashboardConfig]:
        """Crea dashboards por defecto."""
        dashboards = {}
        
        # Dashboard ejecutivo
        dashboards['executive'] = DashboardConfig(
            name="Vista Ejecutiva",
            description="Métricas clave y resumen general",
            widgets=[
                "total_issues", "in_progress", "high_priority", "overdue",
                "status_distribution", "priority_distribution",
                "updates_timeline"
            ],
            layout={"columns": 4, "responsive": True}
        )
        
        # Dashboard personal
        dashboards['personal'] = DashboardConfig(
            name="Mi Trabajo",
            description="Focus en mis asignaciones y tareas",
            widgets=[
                "in_progress", "high_priority", "overdue",
                "my_assignments", "recent_issues"
            ],
            layout={"columns": 3, "responsive": True}
        )
        
        # Dashboard de proyecto
        dashboards['project'] = DashboardConfig(
            name="Vista de Proyecto",
            description="Análisis y progreso por proyecto",
            widgets=[
                "total_issues", "project_progress",
                "status_distribution", "activity_heatmap",
                "updates_timeline"
            ],
            layout={"columns": 2, "responsive": True}
        )
        
        # Dashboard JQL Avanzado (NUEVO)
        dashboards['jql_advanced'] = DashboardConfig(
            name="Consultas JQL Avanzadas",
            description="Widgets basados en consultas JQL específicas",
            widgets=[
                "total_issues", "in_progress", "high_priority",
                "escalations_unassigned_jql", "user_bau_escalations",
                "old_unresolved_jql", "custom_jql_widget"
            ],
            layout={"columns": 3, "responsive": True}
        )
        
        # Dashboard BAU Académico (NUEVO - específico para el usuario)
        dashboards['bau_academic'] = DashboardConfig(
            name="BAU Servicios Universitarios - Académico",
            description="Dashboard específico para BAU Académico con escalaciones y issues sin asignar",
            widgets=[
                "in_progress", "overdue", "resolution_time",
                "user_bau_escalations", "escalations_unassigned_jql",
                "blocked_issues"
            ],
            layout={"columns": 3, "responsive": True}
        )
        
        return dashboards
    
    def get_dashboard_configs(self) -> Dict[str, DashboardConfig]:
        """Obtiene configuraciones de dashboards disponibles."""
        return self.default_dashboards
    
    def get_dashboard(self, dashboard_id: str) -> DashboardConfig:
        """Obtiene configuración de un dashboard específico."""
        return self.default_dashboards.get(dashboard_id)
    
    def save_custom_dashboard(self, dashboard_id: str, config: DashboardConfig):
        """Guarda configuración de dashboard personalizado."""
        # En una implementación real, esto se guardaría en base de datos o archivo
        if 'custom_dashboards' not in st.session_state:
            st.session_state.custom_dashboards = {}
        st.session_state.custom_dashboards[dashboard_id] = config
    
    def get_custom_dashboards(self) -> Dict[str, DashboardConfig]:
        """Obtiene dashboards personalizados."""
        return st.session_state.get('custom_dashboards', {})


def render_dashboard_selector():
    """Renderiza selector de dashboard."""
    manager = DashboardManager()
    
    st.markdown("### 🎛️ **Panel de Control Personalizable**")
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🔍 Consultas JQL", "🖼️ Galería de Widgets"])
    
    with tab1:
        render_dashboard_tab(manager)
    
    with tab2:
        render_jql_query_manager()
    
    with tab3:
        render_widget_gallery()


def render_dashboard_tab(manager: DashboardManager):
    """Renderiza la pestaña principal del dashboard."""
    # Selector de dashboard
    col1, col2 = st.columns([3, 1])
    
    with col1:
        default_dashboards = manager.get_dashboard_configs()
        custom_dashboards = manager.get_custom_dashboards()
        
        all_dashboards = {**default_dashboards, **custom_dashboards}
        dashboard_options = {config.name: dashboard_id for dashboard_id, config in all_dashboards.items()}
        
        selected_name = st.selectbox(
            "Seleccionar Dashboard",
            options=list(dashboard_options.keys()),
            help="Elige un dashboard predefinido o personalizado"
        )
        
        selected_id = dashboard_options[selected_name]
        selected_config = all_dashboards[selected_id]
    
    with col2:
        if st.button("⚙️ Configurar", help="Personalizar dashboard"):
            st.session_state.show_config = True
    
    # Mostrar descripción
    st.info(f"📝 {selected_config.description}")
    
    # Renderizar dashboard seleccionado
    render_dashboard(selected_config)
    
    # Mostrar configurador si está activado
    if st.session_state.get('show_config', False):
        render_dashboard_configurator(selected_id, selected_config)


def render_dashboard(config: DashboardConfig):
    """Renderiza un dashboard según su configuración."""
    if not validate_issues_data():
        st.info("📭 No hay datos cargados. Usa la barra lateral para obtener datos.")
        return
    
    issues = get_safe_issues()
    
    if not issues:
        st.warning("⚠️ No se encontraron issues.")
        return
    
    # Organizar widgets por tamaño
    small_widgets = []
    medium_widgets = []
    large_widgets = []
    
    for widget_id in config.widgets:
        widget = widget_registry.get(widget_id)
        if widget:
            if widget.size == WidgetSize.SMALL:
                small_widgets.append(widget)
            elif widget.size == WidgetSize.MEDIUM:
                medium_widgets.append(widget)
            else:
                large_widgets.append(widget)
    
    # Renderizar widgets pequeños (métricas) en columnas
    if small_widgets:
        cols = st.columns(len(small_widgets))
        for i, widget in enumerate(small_widgets):
            with cols[i]:
                try:
                    widget.render_func(issues, widget.config)
                except Exception as e:
                    st.error(f"Error renderizando {widget.title}: {str(e)}")
        
        if medium_widgets or large_widgets:
            st.markdown("---")
    
    # Renderizar widgets medianos en pares
    if medium_widgets:
        for i in range(0, len(medium_widgets), 2):
            if i + 1 < len(medium_widgets):
                col1, col2 = st.columns(2)
                with col1:
                    try:
                        medium_widgets[i].render_func(issues, medium_widgets[i].config)
                    except Exception as e:
                        st.error(f"Error renderizando {medium_widgets[i].title}: {str(e)}")
                with col2:
                    try:
                        medium_widgets[i+1].render_func(issues, medium_widgets[i+1].config)
                    except Exception as e:
                        st.error(f"Error renderizando {medium_widgets[i+1].title}: {str(e)}")
            else:
                # Widget mediano solo
                try:
                    medium_widgets[i].render_func(issues, medium_widgets[i].config)
                except Exception as e:
                    st.error(f"Error renderizando {medium_widgets[i].title}: {str(e)}")
        
        if large_widgets:
            st.markdown("---")
    
    # Renderizar widgets grandes
    for widget in large_widgets:
        try:
            st.markdown(f"#### {widget.title}")
            widget.render_func(issues, widget.config)
            st.markdown("---")
        except Exception as e:
            st.error(f"Error renderizando {widget.title}: {str(e)}")


def render_dashboard_configurator(dashboard_id: str, config: DashboardConfig):
    """Renderiza configurador de dashboard."""
    with st.expander("⚙️ Configurador de Dashboard", expanded=True):
        st.markdown("#### Personalizar Dashboard")
        
        # Información del dashboard actual
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Nombre del Dashboard", value=config.name)
            new_description = st.text_area("Descripción", value=config.description)
        
        with col2:
            st.markdown("**Widgets Disponibles:**")
            all_widgets = widget_registry.get_all()
            
            # Organizar widgets por tipo
            widget_categories = {
                "Métricas": [w for w in all_widgets.values() if w.widget_type.value == "metric"],
                "Gráficos": [w for w in all_widgets.values() if w.widget_type.value in ["pie_chart", "bar_chart", "line_chart"]],
                "Tablas": [w for w in all_widgets.values() if w.widget_type.value == "table"],
                "Otros": [w for w in all_widgets.values() if w.widget_type.value in ["progress", "heatmap"]]
            }
            
            selected_widgets = []
            for category, widgets in widget_categories.items():
                if widgets:
                    st.markdown(f"**{category}:**")
                    for widget in widgets:
                        if st.checkbox(
                            f"{widget.title}",
                            value=widget.id in config.widgets,
                            key=f"widget_{widget.id}"
                        ):
                            selected_widgets.append(widget.id)
        
        # Botones de acción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Guardar Personalización"):
                new_config = DashboardConfig(
                    name=new_name,
                    description=new_description,
                    widgets=selected_widgets,
                    layout=config.layout
                )
                
                manager = DashboardManager()
                custom_id = f"custom_{len(manager.get_custom_dashboards()) + 1}"
                manager.save_custom_dashboard(custom_id, new_config)
                
                st.success(f"✅ Dashboard '{new_name}' guardado como personalizado!")
                st.session_state.show_config = False
                st.rerun()
        
        with col2:
            if st.button("🔄 Restaurar Original"):
                st.session_state.show_config = False
                st.rerun()
        
        with col3:
            if st.button("❌ Cancelar"):
                st.session_state.show_config = False
                st.rerun()


def render_widget_gallery():
    """Renderiza galería de widgets disponibles."""
    st.markdown("### 🖼️ **Galería de Widgets**")
    
    all_widgets = widget_registry.get_all()
    
    if not validate_issues_data():
        st.info("📭 Carga datos desde la barra lateral para ver ejemplos de widgets.")
        
        # Mostrar lista de widgets disponibles sin datos
        for widget_id, widget in all_widgets.items():
            with st.expander(f"{widget.title} ({widget.widget_type.value})"):
                st.write(f"**Tipo:** {widget.widget_type.value}")
                st.write(f"**Tamaño:** {widget.size.value}")
                if widget.config.get('help'):
                    st.write(f"**Descripción:** {widget.config['help']}")
        return
    
    issues = get_safe_issues()
    
    # Organizar por categorías
    categories = {
        "Métricas": [w for w in all_widgets.values() if w.widget_type.value == "metric"],
        "Gráficos Circulares": [w for w in all_widgets.values() if w.widget_type.value == "pie_chart"],
        "Gráficos de Barras": [w for w in all_widgets.values() if w.widget_type.value == "bar_chart"],
        "Gráficos de Línea": [w for w in all_widgets.values() if w.widget_type.value == "line_chart"],
        "Tablas": [w for w in all_widgets.values() if w.widget_type.value == "table"],
        "Otros": [w for w in all_widgets.values() if w.widget_type.value in ["progress", "heatmap"]]
    }
    
    for category, widgets in categories.items():
        if widgets:
            st.markdown(f"#### {category}")
            
            for widget in widgets:
                with st.expander(f"{widget.title}", expanded=False):
                    try:
                        widget.render_func(issues, widget.config)
                    except Exception as e:
                        st.error(f"Error renderizando widget: {str(e)}")
            
            st.markdown("---")