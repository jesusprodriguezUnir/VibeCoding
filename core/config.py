#!/usr/bin/env python3
"""
Configuración centralizada para la aplicación.
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class JiraConfig:
    """Configuración para conexión con Jira."""
    base_url: str
    email: str
    token: str
    api_version: str = "3"
    timeout: int = 30
    max_results_default: int = 100


@dataclass
class AppConfig:
    """Configuración general de la aplicación."""
    app_title: str = "Visualizador de Asignaciones Jira"
    app_icon: str = "📊"
    page_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.page_config is None:
            self.page_config = {
                "page_title": self.app_title,
                "page_icon": self.app_icon,
                "layout": "wide",
                "initial_sidebar_state": "expanded"
            }


class Config:
    """Configuración centralizada."""
    
    # Campos por defecto para consultas JQL
    DEFAULT_FIELDS = [
        'key', 'summary', 'status', 'priority', 'assignee', 
        'reporter', 'created', 'updated', 'project', 'issuetype',
        'duedate', 'labels', 'components', 'description'
    ]
    
    # Consultas JQL predefinidas
    PREDEFINED_QUERIES = {
        "Mis Issues": "assignee = currentUser() ORDER BY updated DESC",
        "En Progreso": "assignee = currentUser() AND status IN ('EN CURSO', 'In Progress', 'ESCALADO') ORDER BY updated DESC",
        "Pendientes": "assignee = currentUser() AND status IN ('NUEVA', 'To Do', 'ANÁLISIS') ORDER BY updated DESC",
        "Completados": "assignee = currentUser() AND status IN ('CERRADA', 'Done', 'RESUELTA') ORDER BY updated DESC",
        "Alta Prioridad": "assignee = currentUser() AND priority IN ('High', 'Highest', 'Alto', 'Crítico') ORDER BY updated DESC",
        "Actualizados Hoy": "assignee = currentUser() AND updated >= -1d ORDER BY updated DESC",
        "Actualizados Esta Semana": "assignee = currentUser() AND updated >= -1w ORDER BY updated DESC",
        "Con Fecha Vencida": "assignee = currentUser() AND duedate < now() AND status NOT IN ('CERRADA', 'Done', 'RESUELTA') ORDER BY duedate ASC"
    }
    
    # Colores para estados
    STATUS_COLORS = {
        'NUEVA': '#ff6b6b',
        'EN CURSO': '#4ecdc4',
        'ESCALADO': '#45b7d1',
        'ANÁLISIS': '#96ceb4',
        'BLOQUEADA': '#ffeaa7',
        'RESUELTA': '#6c5ce7',
        'CERRADA': '#a29bfe',
        'DESESTIMADA': '#fd79a8'
    }
    
    # Colores para prioridades
    PRIORITY_COLORS = {
        'Crítico': '#e17055',
        'Alto': '#f39c12',
        'Medio': '#f1c40f',
        'Bajo': '#27ae60',
        'Más bajo': '#95a5a6'
    }
    
    # Configuración de gráficos
    CHART_CONFIG = {
        'height': 400,
        'use_container_width': True
    }
    
    @classmethod
    def get_jira_config(cls) -> JiraConfig:
        """Obtiene configuración de Jira desde variables de entorno."""
        base_url = os.getenv('JIRA_BASE_URL')
        email = os.getenv('JIRA_EMAIL')
        token = os.getenv('JIRA_TOKEN')
        
        if not all([base_url, email, token]):
            raise ValueError(
                "Faltan variables de entorno de Jira. "
                "Configura JIRA_BASE_URL, JIRA_EMAIL y JIRA_TOKEN"
            )
        
        return JiraConfig(
            base_url=base_url,
            email=email,
            token=token
        )
    
    @classmethod
    def get_app_config(cls) -> AppConfig:
        """Obtiene configuración de la aplicación."""
        return AppConfig()
