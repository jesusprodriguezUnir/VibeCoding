#!/usr/bin/env python3
"""
Cliente para interactuar con la API de Jira.
"""

import os
import logging
import requests
from typing import Dict, List, Optional, Any
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv


class JiraAPIError(Exception):
    """Excepción personalizada para errores de la API de Jira."""
    pass


class JiraClient:
    """Cliente para interactuar con la API de Jira."""
    
    def __init__(self, base_url: str = None, email: str = None, token: str = None):
        """Inicializa el cliente de Jira.
        
        Args:
            base_url: URL base de Jira (opcional, se puede cargar de .env)
            email: Email del usuario (opcional, se puede cargar de .env)
            token: Token de API (opcional, se puede cargar de .env)
        """
        # Cargar variables de entorno si no se proporcionan parámetros
        if not all([base_url, email, token]):
            load_dotenv()
            
        self.base_url = base_url or os.getenv('JIRA_BASE_URL')
        self.email = email or os.getenv('JIRA_EMAIL')
        self.token = token or os.getenv('JIRA_TOKEN')
        
        if not all([self.base_url, self.email, self.token]):
            raise ValueError(
                "Faltan credenciales de Jira. Configura las variables de entorno:\n"
                "JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN"
            )
        
        self.api_url = f"{self.base_url}/rest/api/3"
        self.auth = HTTPBasicAuth(self.email, self.token)
        self.session = self._create_session()
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
    
    def _create_session(self) -> requests.Session:
        """Crea una sesión de requests configurada."""
        session = requests.Session()
        session.auth = self.auth
        session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        return session
    
    def test_connection(self) -> Dict[str, Any]:
        """Prueba la conexión con Jira.
        
        Returns:
            Dict con información del usuario o error
        """
        try:
            response = self.session.get(f"{self.api_url}/myself", timeout=10)
            response.raise_for_status()
            
            user_info = response.json()
            return {
                'success': True,
                'user': user_info,
                'message': f"Conectado como: {user_info.get('displayName')} ({user_info.get('emailAddress')})"
            }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error de conexión: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Error de conexión: {e}"
            }
    
    def search_issues(self, 
                     jql: str, 
                     max_results: int = 100, 
                     fields: List[str] = None,
                     start_at: int = 0) -> Dict[str, Any]:
        """Busca issues usando JQL.
        
        Args:
            jql: Consulta JQL
            max_results: Número máximo de resultados
            fields: Campos a incluir en la respuesta
            start_at: Índice de inicio para paginación
            
        Returns:
            Dict con issues encontrados o error
        """
        if fields is None:
            fields = [
                'key', 'summary', 'status', 'priority', 'assignee', 
                'reporter', 'created', 'updated', 'project', 'issuetype',
                'duedate', 'labels', 'components'
            ]
        
        params = {
            'jql': jql,
            'maxResults': max_results,
            'startAt': start_at,
            'fields': ','.join(fields)
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/search/jql", 
                params=params, 
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'issues': data.get('issues', []),
                'total': data.get('total', 0),
                'start_at': data.get('startAt', 0),
                'max_results': data.get('maxResults', 0)
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error en búsqueda JQL '{jql}': {e}")
            return {
                'success': False,
                'error': str(e),
                'issues': []
            }
    
    def get_my_issues(self, 
                     status_filter: str = None, 
                     project_filter: str = None,
                     max_results: int = 100) -> Dict[str, Any]:
        """Obtiene issues asignados al usuario actual.
        
        Args:
            status_filter: Filtro por estado
            project_filter: Filtro por proyecto
            max_results: Número máximo de resultados
            
        Returns:
            Dict con issues encontrados
        """
        jql_parts = ["assignee = currentUser()"]
        
        if status_filter:
            jql_parts.append(f'status = "{status_filter}"')
        
        if project_filter:
            jql_parts.append(f'project = "{project_filter}"')
        
        jql = " AND ".join(jql_parts) + " ORDER BY updated DESC"
        
        self.logger.info(f"Ejecutando JQL: {jql}")
        return self.search_issues(jql, max_results)
    
    def get_recent_issues(self, days: int = 7, max_results: int = 100) -> Dict[str, Any]:
        """Obtiene issues actualizados recientemente.
        
        Args:
            days: Número de días hacia atrás
            max_results: Número máximo de resultados
            
        Returns:
            Dict con issues encontrados
        """
        jql = f"assignee = currentUser() AND updated >= -{days}d ORDER BY updated DESC"
        
        self.logger.info(f"Ejecutando JQL: {jql}")
        return self.search_issues(jql, max_results)
    
    def get_issues_by_jql(self, jql: str, max_results: int = 100) -> Dict[str, Any]:
        """Obtiene issues usando JQL personalizado.
        
        Args:
            jql: Consulta JQL personalizada
            max_results: Número máximo de resultados
            
        Returns:
            Dict con issues encontrados
        """
        self.logger.info(f"Ejecutando JQL personalizado: {jql}")
        return self.search_issues(jql, max_results)
    
    def get_projects(self) -> Dict[str, Any]:
        """Obtiene lista de proyectos disponibles.
        
        Returns:
            Dict con proyectos disponibles
        """
        try:
            response = self.session.get(f"{self.api_url}/project", timeout=10)
            response.raise_for_status()
            
            projects = response.json()
            return {
                'success': True,
                'projects': projects
            }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error obteniendo proyectos: {e}")
            return {
                'success': False,
                'error': str(e),
                'projects': []
            }
