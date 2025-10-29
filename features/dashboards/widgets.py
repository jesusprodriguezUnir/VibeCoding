"""
Sistema de widgets configurables para paneles personalizados tipo Jira.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
from shared.utils import format_number, calculate_age_days
from shared.ui.ui_utils import get_safe_issues, validate_issues_data


class WidgetType(Enum):
    """Tipos de widgets disponibles."""
    METRIC = "metric"
    PIE_CHART = "pie_chart"
    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    TABLE = "table"
    PROGRESS = "progress"
    HEATMAP = "heatmap"


class WidgetSize(Enum):
    """Tamaños de widgets."""
    SMALL = "small"     # 1/4 de ancho
    MEDIUM = "medium"   # 1/2 de ancho
    LARGE = "large"     # ancho completo


@dataclass
class Widget:
    """Definición de un widget."""
    id: str
    title: str
    widget_type: WidgetType
    size: WidgetSize
    config: Dict[str, Any]
    render_func: Callable[[List[Dict], Dict], None]


class WidgetRegistry:
    """Registro de widgets disponibles."""
    
    def __init__(self):
        self.widgets = {}
        self._register_default_widgets()
    
    def register(self, widget: Widget):
        """Registra un widget."""
        self.widgets[widget.id] = widget
    
    def get(self, widget_id: str) -> Widget:
        """Obtiene un widget por ID."""
        return self.widgets.get(widget_id)
    
    def get_all(self) -> Dict[str, Widget]:
        """Obtiene todos los widgets."""
        return self.widgets.copy()
    
    def get_by_type(self, widget_type: WidgetType) -> List[Widget]:
        """Obtiene widgets por tipo."""
        return [w for w in self.widgets.values() if w.widget_type == widget_type]
    
    def _register_default_widgets(self):
        """Registra widgets por defecto."""
        
        # Widget de métricas generales
        self.register(Widget(
            id="total_issues",
            title="Total Issues",
            widget_type=WidgetType.METRIC,
            size=WidgetSize.SMALL,
            config={"icon": "📋", "help": "Número total de issues"},
            render_func=self._render_total_issues
        ))
        
        # Widget de issues en progreso
        self.register(Widget(
            id="in_progress",
            title="En Progreso",
            widget_type=WidgetType.METRIC,
            size=WidgetSize.SMALL,
            config={"icon": "🔥", "help": "Issues actualmente en progreso"},
            render_func=self._render_in_progress
        ))
        
        # Widget de alta prioridad
        self.register(Widget(
            id="high_priority",
            title="Alta Prioridad",
            widget_type=WidgetType.METRIC,
            size=WidgetSize.SMALL,
            config={"icon": "⚡", "help": "Issues de prioridad alta o crítica"},
            render_func=self._render_high_priority
        ))
        
        # Widget de vencidos
        self.register(Widget(
            id="overdue",
            title="Vencidos",
            widget_type=WidgetType.METRIC,
            size=WidgetSize.SMALL,
            config={"icon": "⏰", "help": "Issues con fecha vencida"},
            render_func=self._render_overdue
        ))
        
        # Gráfico de distribución por estado
        self.register(Widget(
            id="status_distribution",
            title="Distribución por Estado",
            widget_type=WidgetType.PIE_CHART,
            size=WidgetSize.MEDIUM,
            config={"colors": "status_colors"},
            render_func=self._render_status_distribution
        ))
        
        # Gráfico de distribución por prioridad
        self.register(Widget(
            id="priority_distribution",
            title="Distribución por Prioridad",
            widget_type=WidgetType.PIE_CHART,
            size=WidgetSize.MEDIUM,
            config={"colors": "priority_colors"},
            render_func=self._render_priority_distribution
        ))
        
        # Timeline de actualizaciones
        self.register(Widget(
            id="updates_timeline",
            title="Timeline de Actualizaciones",
            widget_type=WidgetType.LINE_CHART,
            size=WidgetSize.LARGE,
            config={"days": 30},
            render_func=self._render_updates_timeline
        ))
        
        # Tabla de issues recientes
        self.register(Widget(
            id="recent_issues",
            title="Issues Recientes",
            widget_type=WidgetType.TABLE,
            size=WidgetSize.LARGE,
            config={"limit": 10, "columns": ["key", "summary", "status", "updated"]},
            render_func=self._render_recent_issues
        ))
        
        # Mis asignaciones
        self.register(Widget(
            id="my_assignments",
            title="Mis Asignaciones",
            widget_type=WidgetType.TABLE,
            size=WidgetSize.LARGE,
            config={"limit": 15, "filter": "assignee"},
            render_func=self._render_my_assignments
        ))
        
        # Progreso por proyecto
        self.register(Widget(
            id="project_progress",
            title="Progreso por Proyecto",
            widget_type=WidgetType.BAR_CHART,
            size=WidgetSize.MEDIUM,
            config={},
            render_func=self._render_project_progress
        ))
        
        # Heatmap de actividad
        self.register(Widget(
            id="activity_heatmap",
            title="Actividad Semanal",
            widget_type=WidgetType.HEATMAP,
            size=WidgetSize.LARGE,
            config={"weeks": 8},
            render_func=self._render_activity_heatmap
        ))
        
        # Widgets específicos de Jira
        
        # Issues por resolver esta semana
        self.register(Widget(
            id="weekly_targets",
            title="Objetivos Semanales",
            widget_type=WidgetType.PROGRESS,
            size=WidgetSize.MEDIUM,
            config={"target_days": 7},
            render_func=self._render_weekly_targets
        ))
        
        # Sprint actual (simulated)
        self.register(Widget(
            id="current_sprint",
            title="Sprint Actual",
            widget_type=WidgetType.TABLE,
            size=WidgetSize.LARGE,
            config={"sprint_simulation": True},
            render_func=self._render_current_sprint
        ))
        
        # Issues por asignee
        self.register(Widget(
            id="assignee_workload",
            title="Carga de Trabajo por Persona",
            widget_type=WidgetType.BAR_CHART,
            size=WidgetSize.MEDIUM,
            config={},
            render_func=self._render_assignee_workload
        ))
        
        # Tiempo promedio de resolución
        self.register(Widget(
            id="resolution_time",
            title="Tiempo de Resolución",
            widget_type=WidgetType.METRIC,
            size=WidgetSize.SMALL,
            config={"icon": "⏱️", "help": "Tiempo promedio de resolución"},
            render_func=self._render_resolution_time
        ))
        
        # Issues bloqueados
        self.register(Widget(
            id="blocked_issues",
            title="Issues Bloqueados",
            widget_type=WidgetType.TABLE,
            size=WidgetSize.LARGE,
            config={"blocked_statuses": ["BLOQUEADA", "Blocked", "Impediment"]},
            render_func=self._render_blocked_issues
        ))
        
        # Burndown chart simplificado
        self.register(Widget(
            id="burndown_chart",
            title="Burndown (Últimos 30 días)",
            widget_type=WidgetType.LINE_CHART,
            size=WidgetSize.LARGE,
            config={"days": 30},
            render_func=self._render_burndown_chart
        ))
        
        # Widgets con consultas JQL personalizadas
        
        # Escalaciones sin asignar (basado en JQL personalizada)
        self.register(Widget(
            id="escalations_unassigned_jql",
            title="Escalaciones Sin Asignar (JQL)",
            widget_type=WidgetType.TABLE,
            size=WidgetSize.LARGE,
            config={
                "jql_query": 'issueLinkType in ("is an escalation for") AND assignee is EMPTY AND statusCategory != done ORDER BY created DESC',
                "max_results": 25,
                "show_metrics": True
            },
            render_func=self._render_jql_widget
        ))
        
        # Consulta específica del usuario
        self.register(Widget(
            id="user_bau_escalations",
            title="BAU Académico - Escalaciones Sin Asignar",
            widget_type=WidgetType.TABLE,
            size=WidgetSize.LARGE,
            config={
                "jql_query": 'created >= -80w AND project = "BAU Servicios Universitarios - Académico" AND status not in (RESUELTA, CERRADA, DESESTIMADA) AND Subarea = "ari:cloud:cmdb::object/d80a641b-f11a-4ae4-8159-a153bbcbb09d/34" AND issueLinkType in ("is an escalation for") AND statusCategory != done AND assignee is EMPTY ORDER BY created DESC',
                "max_results": 50,
                "show_metrics": True,
                "highlight_urgent": True
            },
            render_func=self._render_jql_widget
        ))
        
        # Issues antiguos sin resolver
        self.register(Widget(
            id="old_unresolved_jql",
            title="Issues Antiguos Sin Resolver",
            widget_type=WidgetType.TABLE,
            size=WidgetSize.LARGE,
            config={
                "jql_query": 'created >= -80w AND status not in (RESUELTA, CERRADA, DESESTIMADA) AND statusCategory != done ORDER BY created ASC',
                "max_results": 30,
                "show_age": True
            },
            render_func=self._render_jql_widget
        ))
        
        # Widget configurable JQL
        self.register(Widget(
            id="custom_jql_widget",
            title="Consulta JQL Personalizada",
            widget_type=WidgetType.TABLE,
            size=WidgetSize.LARGE,
            config={
                "jql_query": "",  # Se configura dinámicamente
                "max_results": 50,
                "configurable": True
            },
            render_func=self._render_configurable_jql_widget
        ))
    
    def _render_total_issues(self, issues: List[Dict], config: Dict):
        """Renderiza widget de total issues."""
        total = len(issues)
        st.metric(
            label=f"{config.get('icon', '📋')} {config.get('title', 'Total Issues')}",
            value=format_number(total),
            help=config.get('help', '')
        )
    
    def _render_in_progress(self, issues: List[Dict], config: Dict):
        """Renderiza widget de issues en progreso."""
        in_progress = [
            i for i in issues 
            if i.get('fields', {}).get('status', {}).get('name', '') in 
            ['EN CURSO', 'In Progress', 'ESCALADO', 'En desarrollo', 'Desarrollo']
        ]
        total = len(issues)
        percentage = (len(in_progress) / total * 100) if total > 0 else 0
        
        st.metric(
            label=f"{config.get('icon', '🔥')} En Progreso",
            value=format_number(len(in_progress)),
            delta=f"{percentage:.1f}%",
            help=config.get('help', '')
        )
    
    def _render_high_priority(self, issues: List[Dict], config: Dict):
        """Renderiza widget de alta prioridad."""
        high_priority = [
            i for i in issues 
            if i.get('fields', {}).get('priority', {}).get('name', '') in 
            ['Alto', 'High', 'Crítico', 'Highest', 'Critical', 'Urgent']
        ]
        total = len(issues)
        percentage = (len(high_priority) / total * 100) if total > 0 else 0
        
        st.metric(
            label=f"{config.get('icon', '⚡')} Alta Prioridad",
            value=format_number(len(high_priority)),
            delta=f"{percentage:.1f}%",
            help=config.get('help', '')
        )
    
    def _render_overdue(self, issues: List[Dict], config: Dict):
        """Renderiza widget de issues vencidos."""
        now = datetime.now()
        overdue = []
        
        for issue in issues:
            due_date_str = issue.get('fields', {}).get('duedate')
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                    if due_date < now:
                        # Verificar que no esté cerrado
                        status = issue.get('fields', {}).get('status', {}).get('name', '')
                        if status not in ['CERRADA', 'Done', 'RESUELTA', 'Closed', 'Resolved']:
                            overdue.append(issue)
                except:
                    continue
        
        st.metric(
            label=f"{config.get('icon', '⏰')} Vencidos",
            value=format_number(len(overdue)),
            delta="Requieren atención" if len(overdue) > 0 else "Todo al día",
            delta_color="inverse" if len(overdue) > 0 else "normal",
            help=config.get('help', '')
        )
    
    def _render_status_distribution(self, issues: List[Dict], config: Dict):
        """Renderiza gráfico de distribución por estado."""
        status_counts = {}
        for issue in issues:
            status = issue.get('fields', {}).get('status', {}).get('name', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Distribución por Estado"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos para mostrar")
    
    def _render_priority_distribution(self, issues: List[Dict], config: Dict):
        """Renderiza gráfico de distribución por prioridad."""
        priority_counts = {}
        for issue in issues:
            priority = issue.get('fields', {}).get('priority', {}).get('name', 'Unknown')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        if priority_counts:
            fig = px.pie(
                values=list(priority_counts.values()),
                names=list(priority_counts.keys()),
                title="Distribución por Prioridad"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos para mostrar")
    
    def _render_updates_timeline(self, issues: List[Dict], config: Dict):
        """Renderiza timeline de actualizaciones."""
        days = config.get('days', 30)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        timeline_data = {}
        for issue in issues:
            updated_str = issue.get('fields', {}).get('updated')
            if updated_str:
                try:
                    updated_date = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
                    if start_date <= updated_date <= end_date:
                        date_key = updated_date.strftime('%Y-%m-%d')
                        timeline_data[date_key] = timeline_data.get(date_key, 0) + 1
                except:
                    continue
        
        if timeline_data:
            dates = sorted(timeline_data.keys())
            counts = [timeline_data[date] for date in dates]
            
            fig = px.line(
                x=dates, y=counts,
                title=f"Actualizaciones en los últimos {days} días",
                labels={'x': 'Fecha', 'y': 'Número de actualizaciones'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay actualizaciones en el período seleccionado")
    
    def _render_recent_issues(self, issues: List[Dict], config: Dict):
        """Renderiza tabla de issues recientes."""
        limit = config.get('limit', 10)
        
        # Ordenar por fecha de actualización
        sorted_issues = sorted(
            issues,
            key=lambda x: x.get('fields', {}).get('updated', ''),
            reverse=True
        )[:limit]
        
        if sorted_issues:
            data = []
            for issue in sorted_issues:
                fields = issue.get('fields', {})
                data.append({
                    'Key': issue.get('key', 'N/A'),
                    'Summary': fields.get('summary', 'N/A')[:50] + '...' if len(fields.get('summary', '')) > 50 else fields.get('summary', 'N/A'),
                    'Status': fields.get('status', {}).get('name', 'N/A'),
                    'Actualizado': self._format_date(fields.get('updated'))
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, height=300)
        else:
            st.info("No hay issues para mostrar")
    
    def _render_my_assignments(self, issues: List[Dict], config: Dict):
        """Renderiza mis asignaciones."""
        # Filtrar issues asignados al usuario actual
        my_issues = []
        for issue in issues:
            assignee = issue.get('fields', {}).get('assignee')
            if assignee:
                # Para esta demo, mostrar todos los issues
                # En producción, filtrar por el usuario actual
                my_issues.append(issue)
        
        limit = config.get('limit', 15)
        my_issues = my_issues[:limit]
        
        if my_issues:
            data = []
            for issue in my_issues:
                fields = issue.get('fields', {})
                data.append({
                    'Key': issue.get('key', 'N/A'),
                    'Summary': fields.get('summary', 'N/A')[:60] + '...' if len(fields.get('summary', '')) > 60 else fields.get('summary', 'N/A'),
                    'Status': fields.get('status', {}).get('name', 'N/A'),
                    'Priority': fields.get('priority', {}).get('name', 'N/A'),
                    'Vencimiento': self._format_date(fields.get('duedate'))
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, height=400)
        else:
            st.info("No tienes issues asignados")
    
    def _render_project_progress(self, issues: List[Dict], config: Dict):
        """Renderiza progreso por proyecto."""
        project_stats = {}
        
        for issue in issues:
            project = issue.get('fields', {}).get('project', {}).get('key', 'Unknown')
            status = issue.get('fields', {}).get('status', {}).get('name', 'Unknown')
            
            if project not in project_stats:
                project_stats[project] = {'total': 0, 'done': 0}
            
            project_stats[project]['total'] += 1
            if status in ['CERRADA', 'Done', 'RESUELTA', 'Closed', 'Resolved']:
                project_stats[project]['done'] += 1
        
        if project_stats:
            projects = []
            progress = []
            
            for project, stats in project_stats.items():
                projects.append(project)
                progress_pct = (stats['done'] / stats['total'] * 100) if stats['total'] > 0 else 0
                progress.append(progress_pct)
            
            fig = px.bar(
                x=progress, y=projects,
                orientation='h',
                title="Progreso por Proyecto (%)",
                labels={'x': 'Porcentaje Completado', 'y': 'Proyecto'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de proyectos para mostrar")
    
    def _render_activity_heatmap(self, issues: List[Dict], config: Dict):
        """Renderiza heatmap de actividad."""
        weeks = config.get('weeks', 8)
        
        # Esta es una implementación simplificada
        # En un caso real, se podría mostrar actividad por día de la semana y hora
        activity_data = {}
        
        for issue in issues:
            updated_str = issue.get('fields', {}).get('updated')
            if updated_str:
                try:
                    updated_date = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
                    week = updated_date.strftime('%Y-W%U')
                    day = updated_date.strftime('%A')
                    
                    if week not in activity_data:
                        activity_data[week] = {}
                    activity_data[week][day] = activity_data[week].get(day, 0) + 1
                except:
                    continue
        
        if activity_data:
            st.text("🔥 Heatmap de Actividad")
            st.info("Funcionalidad de heatmap disponible en próxima versión")
        else:
            st.info("No hay datos de actividad para mostrar")
    
    def _format_date(self, date_str: str) -> str:
        """Formatea fecha."""
        if not date_str:
            return 'N/A'
        
        try:
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d')
            else:
                return date_str
        except:
            return date_str
    
    # Implementaciones de widgets específicos de Jira
    
    def _render_weekly_targets(self, issues: List[Dict], config: Dict):
        """Renderiza objetivos semanales."""
        target_days = config.get('target_days', 7)
        
        # Simular objetivos basados en issues pendientes de alta prioridad
        high_priority_pending = [
            i for i in issues 
            if (i.get('fields', {}).get('priority', {}).get('name', '') in 
                ['Alto', 'High', 'Crítico', 'Highest', 'Critical']) and
               (i.get('fields', {}).get('status', {}).get('name', '') not in 
                ['CERRADA', 'Done', 'RESUELTA', 'Closed', 'Resolved'])
        ]
        
        target_count = min(len(high_priority_pending), 10)  # Máximo 10 objetivos
        completed_count = max(0, target_count - len(high_priority_pending))
        
        progress = (completed_count / target_count * 100) if target_count > 0 else 100
        
        st.metric(
            label="🎯 Objetivos Semanales",
            value=f"{completed_count}/{target_count}",
            delta=f"{progress:.0f}% completado"
        )
        
        if target_count > 0:
            st.progress(progress / 100)
    
    def _render_current_sprint(self, issues: List[Dict], config: Dict):
        """Renderiza sprint actual (simulado)."""
        # Simular sprint tomando issues más recientes
        sprint_issues = sorted(
            issues,
            key=lambda x: x.get('fields', {}).get('updated', ''),
            reverse=True
        )[:20]  # Top 20 issues más recientes como "sprint"
        
        if sprint_issues:
            data = []
            for issue in sprint_issues:
                fields = issue.get('fields', {})
                status = fields.get('status', {}).get('name', 'N/A')
                
                # Estimar story points basado en prioridad
                priority = fields.get('priority', {}).get('name', 'Medium')
                story_points = {
                    'Crítico': 8, 'Highest': 8, 'Critical': 8,
                    'Alto': 5, 'High': 5,
                    'Medio': 3, 'Medium': 3,
                    'Bajo': 2, 'Low': 2,
                    'Más bajo': 1, 'Lowest': 1
                }.get(priority, 3)
                
                data.append({
                    'Key': issue.get('key', 'N/A'),
                    'Summary': fields.get('summary', 'N/A')[:40] + '...' if len(fields.get('summary', '')) > 40 else fields.get('summary', 'N/A'),
                    'Status': status,
                    'Story Points': story_points,
                    'Assignee': self._get_user_name(fields.get('assignee'))
                })
            
            df = pd.DataFrame(data)
            
            # Mostrar métricas del sprint
            total_points = df['Story Points'].sum()
            completed_points = df[df['Status'].isin(['CERRADA', 'Done', 'RESUELTA', 'Closed', 'Resolved'])]['Story Points'].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Points", total_points)
            with col2:
                st.metric("Completados", completed_points)
            with col3:
                progress = (completed_points / total_points * 100) if total_points > 0 else 0
                st.metric("Progreso", f"{progress:.1f}%")
            
            st.dataframe(df, use_container_width=True, height=300)
        else:
            st.info("No hay issues en el sprint actual")
    
    def _render_assignee_workload(self, issues: List[Dict], config: Dict):
        """Renderiza carga de trabajo por asignee."""
        assignee_counts = {}
        
        for issue in issues:
            assignee = self._get_user_name(issue.get('fields', {}).get('assignee'))
            if assignee != 'Unassigned':
                assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
        
        if assignee_counts:
            # Tomar top 10 asignees
            sorted_assignees = sorted(
                assignee_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            names = [item[0] for item in sorted_assignees]
            counts = [item[1] for item in sorted_assignees]
            
            fig = px.bar(
                x=counts, y=names,
                orientation='h',
                title="Issues por Asignee",
                labels={'x': 'Número de Issues', 'y': 'Asignee'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de asignees para mostrar")
    
    def _render_resolution_time(self, issues: List[Dict], config: Dict):
        """Renderiza tiempo promedio de resolución."""
        resolution_times = []
        
        for issue in issues:
            fields = issue.get('fields', {})
            created_str = fields.get('created')
            resolved_str = fields.get('resolutiondate')
            
            if created_str and resolved_str:
                try:
                    created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                    resolved = datetime.fromisoformat(resolved_str.replace('Z', '+00:00'))
                    diff = (resolved - created).days
                    resolution_times.append(diff)
                except:
                    continue
        
        if resolution_times:
            avg_days = sum(resolution_times) / len(resolution_times)
            st.metric(
                label=f"{config.get('icon', '⏱️')} Tiempo Promedio",
                value=f"{avg_days:.1f} días",
                help=config.get('help', '')
            )
        else:
            st.metric(
                label=f"{config.get('icon', '⏱️')} Tiempo Promedio",
                value="N/A",
                help="No hay datos de resolución"
            )
    
    def _render_blocked_issues(self, issues: List[Dict], config: Dict):
        """Renderiza issues bloqueados."""
        blocked_statuses = config.get('blocked_statuses', ['BLOQUEADA', 'Blocked', 'Impediment'])
        
        blocked_issues = [
            issue for issue in issues
            if issue.get('fields', {}).get('status', {}).get('name', '') in blocked_statuses
        ]
        
        if blocked_issues:
            data = []
            for issue in blocked_issues:
                fields = issue.get('fields', {})
                data.append({
                    'Key': issue.get('key', 'N/A'),
                    'Summary': fields.get('summary', 'N/A')[:50] + '...' if len(fields.get('summary', '')) > 50 else fields.get('summary', 'N/A'),
                    'Assignee': self._get_user_name(fields.get('assignee')),
                    'Bloqueado desde': self._format_date(fields.get('updated'))
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, height=200)
            
            st.warning(f"⚠️ {len(blocked_issues)} issues bloqueados requieren atención")
        else:
            st.success("✅ No hay issues bloqueados")
    
    def _render_burndown_chart(self, issues: List[Dict], config: Dict):
        """Renderiza gráfico burndown simplificado."""
        days = config.get('days', 30)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Simular burndown contando issues completados por día
        daily_completion = {}
        total_issues = len(issues)
        
        for issue in issues:
            resolved_str = issue.get('fields', {}).get('resolutiondate')
            if resolved_str:
                try:
                    resolved_date = datetime.fromisoformat(resolved_str.replace('Z', '+00:00'))
                    if start_date <= resolved_date <= end_date:
                        date_key = resolved_date.strftime('%Y-%m-%d')
                        daily_completion[date_key] = daily_completion.get(date_key, 0) + 1
                except:
                    continue
        
        # Calcular burndown acumulativo
        dates = []
        remaining = []
        current_date = start_date
        remaining_count = total_issues
        
        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            completed_today = daily_completion.get(date_key, 0)
            remaining_count = max(0, remaining_count - completed_today)
            
            dates.append(date_key)
            remaining.append(remaining_count)
            current_date += timedelta(days=1)
        
        if dates and any(r != total_issues for r in remaining):
            # Línea ideal (straight line from start to 0)
            ideal_line = [total_issues * (1 - i / len(dates)) for i in range(len(dates))]
            
            fig = go.Figure()
            
            # Línea real
            fig.add_trace(go.Scatter(
                x=dates, y=remaining,
                mode='lines+markers',
                name='Burndown Real',
                line=dict(color='blue', width=2)
            ))
            
            # Línea ideal
            fig.add_trace(go.Scatter(
                x=dates, y=ideal_line,
                mode='lines',
                name='Burndown Ideal',
                line=dict(color='red', dash='dash', width=2)
            ))
            
            fig.update_layout(
                title=f"Burndown Chart (últimos {days} días)",
                xaxis_title="Fecha",
                yaxis_title="Issues Restantes",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay suficientes datos para mostrar burndown chart")
    
    def _get_user_name(self, user_data: Dict) -> str:
        """Extrae nombre de usuario de forma segura."""
        if not user_data:
            return 'Unassigned'
        return user_data.get('displayName', user_data.get('name', 'N/A'))
    
    # Implementaciones de widgets con consultas JQL personalizadas
    
    def _render_jql_widget(self, issues: List[Dict], config: Dict):
        """Renderiza widget basado en consulta JQL personalizada."""
        jql_query = config.get('jql_query', '')
        max_results = config.get('max_results', 50)
        show_metrics = config.get('show_metrics', False)
        show_age = config.get('show_age', False)
        highlight_urgent = config.get('highlight_urgent', False)
        
        if not jql_query:
            st.info("Consulta JQL no configurada")
            return
        
        # Ejecutar consulta JQL específica
        if st.session_state.client:
            try:
                with st.spinner("Ejecutando consulta JQL..."):
                    result = st.session_state.client.search_issues(
                        jql=jql_query,
                        max_results=max_results
                    )
                
                if result.get('success', False):
                    jql_issues = result.get('issues', [])
                    
                    if show_metrics:
                        self._render_jql_metrics(jql_issues)
                    
                    if jql_issues:
                        self._render_jql_table(jql_issues, show_age, highlight_urgent)
                    else:
                        st.info("✅ No se encontraron issues que coincidan con la consulta")
                else:
                    st.error(f"❌ Error en consulta JQL: {result.get('error', 'Error desconocido')}")
            except Exception as e:
                st.error(f"❌ Error ejecutando JQL: {str(e)}")
        else:
            st.error("❌ Cliente Jira no disponible")
    
    def _render_jql_metrics(self, issues: List[Dict]):
        """Renderiza métricas para issues de consulta JQL."""
        total = len(issues)
        unassigned = len([i for i in issues if not i.get('fields', {}).get('assignee')])
        
        # Calcular alta prioridad manejando campos None
        high_priority = 0
        for issue in issues:
            priority = issue.get('fields', {}).get('priority') or {}
            priority_name = priority.get('name', '')
            if priority_name in ['Alto', 'High', 'Crítico', 'Highest', 'Critical', 'Urgent']:
                high_priority += 1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📋 Total", total)
        with col2:
            st.metric("👤 Sin Asignar", unassigned)
        with col3:
            st.metric("⚡ Alta Prioridad", high_priority)
    
    def _render_jql_table(self, issues: List[Dict], show_age: bool = False, highlight_urgent: bool = False):
        """Renderiza tabla de issues de consulta JQL."""
        data = []
        
        for issue in issues:
            fields = issue.get('fields', {})
            
            # Manejar campos que pueden ser None de forma segura
            status = fields.get('status') or {}
            priority = fields.get('priority') or {}
            assignee = fields.get('assignee') or {}
            
            # Calcular edad si se solicita
            age_days = 0
            if show_age:
                created_str = fields.get('created')
                if created_str:
                    # Usar función utilitaria para calcular edad de forma segura
                    age_days = calculate_age_days(created_str)
            
            # Determinar urgencia
            urgent = False
            if highlight_urgent:
                priority_name = priority.get('name', '')
                age_weeks = age_days / 7 if age_days > 0 else 0
                urgent = (priority_name in ['Crítico', 'Critical', 'Highest'] or age_weeks > 12)
            
            row_data = {
                'Key': issue.get('key', 'N/A'),
                'Summary': self._truncate_text(fields.get('summary', 'N/A'), 50),
                'Status': status.get('name', 'N/A'),
                'Priority': priority.get('name', 'N/A'),
                'Assignee': self._get_user_name(assignee),
                'Created': self._format_date(fields.get('created')),
                'Updated': self._format_date(fields.get('updated'))
            }
            
            if show_age:
                row_data['Edad (días)'] = age_days
            
            if highlight_urgent and urgent:
                row_data['🚨'] = '⚠️ URGENTE'
            
            data.append(row_data)
        
        if data:
            df = pd.DataFrame(data)
            
            # Aplicar estilo si hay issues urgentes
            if highlight_urgent and any('🚨' in str(row) for row in data):
                st.warning("⚠️ Se encontraron issues que requieren atención urgente")
            
            # Configurar altura basada en número de resultados
            height = min(400, max(200, len(data) * 35 + 50))
            st.dataframe(df, use_container_width=True, height=height)
        else:
            st.info("No hay datos para mostrar")
    
    def _render_configurable_jql_widget(self, issues: List[Dict], config: Dict):
        """Renderiza widget JQL configurable."""
        st.markdown("#### 🔧 Widget JQL Configurable")
        
        # Formulario de configuración
        with st.expander("⚙️ Configurar Consulta JQL", expanded=False):
            current_jql = st.session_state.get('custom_widget_jql', config.get('jql_query', ''))
            
            new_jql = st.text_area(
                "Consulta JQL",
                value=current_jql,
                placeholder="Introduce tu consulta JQL personalizada...",
                help="Ejemplo: project = 'MI_PROYECTO' AND assignee is EMPTY"
            )
            
            max_results = st.number_input(
                "Máximo resultados",
                min_value=1,
                max_value=200,
                value=config.get('max_results', 50)
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Actualizar Consulta"):
                    st.session_state.custom_widget_jql = new_jql
                    st.session_state.custom_widget_max_results = max_results
                    st.rerun()
            
            with col2:
                if st.button("❌ Limpiar"):
                    st.session_state.custom_widget_jql = ""
                    st.rerun()
        
        # Ejecutar consulta actual
        current_jql = st.session_state.get('custom_widget_jql', '')
        current_max_results = st.session_state.get('custom_widget_max_results', 50)
        
        if current_jql:
            # Configuración temporal para el widget JQL
            temp_config = {
                'jql_query': current_jql,
                'max_results': current_max_results,
                'show_metrics': True,
                'highlight_urgent': True
            }
            self._render_jql_widget(issues, temp_config)
        else:
            st.info("💡 Configura una consulta JQL arriba para ver resultados")
            
            # Mostrar ejemplos
            st.markdown("**Ejemplos de consultas JQL:**")
            examples = [
                "assignee is EMPTY AND priority in (High, Highest)",
                "project = 'MI_PROYECTO' AND status != Done",
                "created >= -4w AND assignee = currentUser()",
                "duedate < now() AND status not in (Resolved, Closed)"
            ]
            
            for i, example in enumerate(examples, 1):
                if st.button(f"📋 Usar ejemplo {i}: {example[:40]}...", key=f"example_{i}"):
                    st.session_state.custom_widget_jql = example
                    st.rerun()


# Instancia global del registro
widget_registry = WidgetRegistry()