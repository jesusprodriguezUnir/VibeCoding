#!/usr/bin/env python3
"""
Jira Assignments Viewer
Visualiza las asignaciones de Jira de forma segura usando tokens de API.
"""

import os
import sys
import json
import argparse
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from tabulate import tabulate
from dotenv import load_dotenv
import urllib.parse

# Cargar variables de entorno
load_dotenv()

class JiraClient:
    """Cliente para interactuar con la API de Jira."""
    
    def __init__(self):
        self.base_url = os.getenv('JIRA_BASE_URL')
        self.email = os.getenv('JIRA_EMAIL')
        self.token = os.getenv('JIRA_TOKEN')
        
        if not all([self.base_url, self.email, self.token]):
            raise ValueError(
                "Faltan variables de entorno. Asegúrate de configurar:\n"
                "JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN en tu archivo .env"
            )
        
        self.api_url = f"{self.base_url}/rest/api/3"
        self.auth = (self.email, self.token)
        self.session = requests.Session()
        self.session.auth = self.auth
    
    def test_connection(self) -> bool:
        """Prueba la conexión con Jira."""
        try:
            response = self.session.get(f"{self.api_url}/myself")
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ Conectado como: {user_info.get('displayName')} ({user_info.get('emailAddress')})")
                return True
            else:
                print(f"❌ Error de conexión: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error de conexión: {str(e)}")
            return False
    
    def search_issues(self, jql: str, max_results: int = 100, fields: List[str] = None) -> List[Dict]:
        """Busca issues usando JQL."""
        if fields is None:
            fields = [
                'key', 'summary', 'status', 'priority', 'assignee', 
                'reporter', 'created', 'updated', 'project', 'issuetype',
                'duedate', 'labels', 'components'
            ]
        
        params = {
            'jql': jql,
            'maxResults': max_results,
            'fields': ','.join(fields),
            'expand': 'changelog'
        }
        
        try:
            response = self.session.get(f"{self.api_url}/search/jql", params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('issues', [])
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en búsqueda: {str(e)}")
            return []
    
    def get_my_issues(self, status_filter: str = None, project_filter: str = None) -> List[Dict]:
        """Obtiene los issues asignados al usuario actual."""
        jql_parts = ["assignee = currentUser()"]
        
        if status_filter:
            jql_parts.append(f'status = "{status_filter}"')
        
        if project_filter:
            jql_parts.append(f'project = "{project_filter}"')
        
        jql = " AND ".join(jql_parts) + " ORDER BY updated DESC"
        
        print(f"🔍 Ejecutando JQL: {jql}")
        return self.search_issues(jql)
    
    def get_recent_issues(self, days: int = 7) -> List[Dict]:
        """Obtiene issues actualizados recientemente."""
        jql = f"assignee = currentUser() AND updated >= -{days}d ORDER BY updated DESC"
        print(f"🔍 Ejecutando JQL: {jql}")
        return self.search_issues(jql)
    
    def get_issues_by_jql(self, jql: str) -> List[Dict]:
        """Obtiene issues usando JQL personalizado."""
        print(f"🔍 Ejecutando JQL: {jql}")
        return self.search_issues(jql)

class IssueFormatter:
    """Formateador para mostrar issues de diferentes maneras."""
    
    @staticmethod
    def format_issue_data(issues: List[Dict]) -> List[Dict]:
        """Formatea los datos de issues para mostrar."""
        formatted_issues = []
        
        for issue in issues:
            fields = issue.get('fields', {})
            
            # Extraer datos de forma segura
            formatted_issue = {
                'Key': issue.get('key', 'N/A'),
                'Summary': fields.get('summary', 'N/A')[:80] + ('...' if len(fields.get('summary', '')) > 80 else ''),
                'Status': fields.get('status', {}).get('name', 'N/A'),
                'Priority': fields.get('priority', {}).get('name', 'N/A'),
                'Assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                'Reporter': fields.get('reporter', {}).get('displayName', 'N/A') if fields.get('reporter') else 'N/A',
                'Project': fields.get('project', {}).get('key', 'N/A'),
                'Issue Type': fields.get('issuetype', {}).get('name', 'N/A'),
                'Created': IssueFormatter._format_date(fields.get('created')),
                'Updated': IssueFormatter._format_date(fields.get('updated')),
                'Due Date': IssueFormatter._format_date(fields.get('duedate')),
                'Labels': ', '.join(fields.get('labels', [])) if fields.get('labels') else 'None',
            }
            
            formatted_issues.append(formatted_issue)
        
        return formatted_issues
    
    @staticmethod
    def _format_date(date_str: str) -> str:
        """Formatea fecha de Jira."""
        if not date_str:
            return 'N/A'
        
        try:
            # Jira devuelve fechas en formato ISO
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            
            return dt.strftime('%Y-%m-%d %H:%M')
        except:
            return date_str
    
    @staticmethod
    def print_table(issues: List[Dict], format_style: str = 'grid'):
        """Imprime issues en formato tabla."""
        if not issues:
            print("📭 No se encontraron issues.")
            return
        
        formatted_data = IssueFormatter.format_issue_data(issues)
        df = pd.DataFrame(formatted_data)
        
        print(f"\n📊 Encontrados {len(issues)} issues:")
        print("=" * 100)
        print(tabulate(df, headers='keys', tablefmt=format_style, showindex=False))
    
    @staticmethod
    def export_to_csv(issues: List[Dict], filename: str):
        """Exporta issues a CSV."""
        if not issues:
            print("📭 No hay datos para exportar.")
            return
        
        formatted_data = IssueFormatter.format_issue_data(issues)
        df = pd.DataFrame(formatted_data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"💾 Datos exportados a: {filename}")
    
    @staticmethod
    def export_to_json(issues: List[Dict], filename: str):
        """Exporta issues a JSON."""
        if not issues:
            print("📭 No hay datos para exportar.")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(issues, f, indent=2, ensure_ascii=False, default=str)
        print(f"💾 Datos exportados a: {filename}")

def create_sample_env():
    """Crea un archivo .env de ejemplo."""
    sample_content = """# Configuración de Jira - NO SUBIR A GITHUB
JIRA_BASE_URL=https://tu-instancia.atlassian.net
JIRA_EMAIL=tu-email@empresa.com
JIRA_TOKEN=tu_token_aqui

# Ejemplo:
# JIRA_BASE_URL=https://miempresa.atlassian.net
# JIRA_EMAIL=juan.perez@miempresa.com
# JIRA_TOKEN=ATATT3xFfGF0T4JQR7x...
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    print("📝 Archivo .env.example creado. Cópialo a .env y completa tus credenciales.")

def main():
    parser = argparse.ArgumentParser(description='Visualizador de Asignaciones de Jira')
    
    # Opciones principales
    parser.add_argument('--all', action='store_true', help='Mostrar todos mis issues')
    parser.add_argument('--status', type=str, help='Filtrar por estado')
    parser.add_argument('--project', type=str, help='Filtrar por proyecto')
    parser.add_argument('--recent', action='store_true', help='Issues actualizados recientemente')
    parser.add_argument('--days', type=int, default=7, help='Días para filtro reciente (default: 7)')
    parser.add_argument('--jql', type=str, help='JQL personalizado')
    
    # Opciones de formato y exportación
    parser.add_argument('--export', choices=['csv', 'json'], help='Exportar datos')
    parser.add_argument('--output', type=str, help='Nombre del archivo de salida')
    parser.add_argument('--format', choices=['grid', 'simple', 'plain'], default='grid', help='Formato de tabla')
    
    # Utilidades
    parser.add_argument('--test', action='store_true', help='Probar conexión')
    parser.add_argument('--setup', action='store_true', help='Crear archivo .env de ejemplo')
    
    args = parser.parse_args()
    
    # Comando de setup
    if args.setup:
        create_sample_env()
        return
    
    try:
        # Inicializar cliente
        jira_client = JiraClient()
        
        # Comando de test
        if args.test:
            jira_client.test_connection()
            return
        
        # Si no hay argumentos, mostrar ayuda
        if not any([args.all, args.recent, args.jql, args.status, args.project]):
            parser.print_help()
            return
        
        # Probar conexión primero
        if not jira_client.test_connection():
            return
        
        # Ejecutar búsqueda según parámetros
        issues = []
        
        if args.jql:
            issues = jira_client.get_issues_by_jql(args.jql)
        elif args.recent:
            issues = jira_client.get_recent_issues(args.days)
        else:
            issues = jira_client.get_my_issues(args.status, args.project)
        
        # Mostrar resultados
        if args.export:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if args.output:
                filename = args.output
            else:
                extension = 'csv' if args.export == 'csv' else 'json'
                filename = f'jira_issues_{timestamp}.{extension}'
            
            if args.export == 'csv':
                IssueFormatter.export_to_csv(issues, filename)
            else:
                IssueFormatter.export_to_json(issues, filename)
        else:
            IssueFormatter.print_table(issues, args.format)
        
    except ValueError as e:
        print(f"❌ Error de configuración: {e}")
        print("\n💡 Ejecuta: python jira_viewer.py --setup para crear un archivo de configuración.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()