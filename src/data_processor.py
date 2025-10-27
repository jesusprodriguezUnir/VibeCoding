#!/usr/bin/env python3
"""
Procesador y formateador de datos de Jira.
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter
import logging


class JiraDataProcessor:
    """Procesador para datos de Jira."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def format_issues_for_display(self, issues: List[Dict]) -> pd.DataFrame:
        """Formatea issues para mostrar en tabla.
        
        Args:
            issues: Lista de issues de Jira
            
        Returns:
            DataFrame con datos formateados
        """
        if not issues:
            return pd.DataFrame()
        
        formatted_data = []
        
        for issue in issues:
            fields = issue.get('fields', {})
            
            formatted_issue = {
                'Key': issue.get('key', 'N/A'),
                'Summary': self._truncate_text(fields.get('summary', 'N/A'), 80),
                'Status': fields.get('status', {}).get('name', 'N/A'),
                'Priority': fields.get('priority', {}).get('name', 'N/A'),
                'Assignee': self._get_user_name(fields.get('assignee')),
                'Reporter': self._get_user_name(fields.get('reporter')),
                'Project': fields.get('project', {}).get('key', 'N/A'),
                'Issue Type': fields.get('issuetype', {}).get('name', 'N/A'),
                'Created': self._format_date(fields.get('created')),
                'Updated': self._format_date(fields.get('updated')),
                'Due Date': self._format_date(fields.get('duedate')),
                'Labels': self._format_labels(fields.get('labels', []))
            }
            
            formatted_data.append(formatted_issue)
        
        return pd.DataFrame(formatted_data)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Trunca texto si es muy largo."""
        if not text or len(text) <= max_length:
            return text
        return text[:max_length] + '...'
    
    def _get_user_name(self, user_data: Dict) -> str:
        """Extrae nombre de usuario de forma segura."""
        if not user_data:
            return 'Unassigned'
        return user_data.get('displayName', 'N/A')
    
    def _format_date(self, date_str: str) -> str:
        """Formatea fecha de Jira."""
        if not date_str:
            return 'N/A'
        
        try:
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            
            return dt.strftime('%Y-%m-%d %H:%M')
        except Exception:
            return date_str
    
    def _format_labels(self, labels: List[str]) -> str:
        """Formatea labels."""
        return ', '.join(labels) if labels else 'None'
    
    def get_status_summary(self, issues: List[Dict]) -> Dict[str, int]:
        """Obtiene resumen por estado.
        
        Args:
            issues: Lista de issues
            
        Returns:
            Dict con conteo por estado
        """
        statuses = []
        for issue in issues:
            status = issue.get('fields', {}).get('status', {}).get('name', 'Unknown')
            statuses.append(status)
        
        return dict(Counter(statuses))
    
    def get_priority_summary(self, issues: List[Dict]) -> Dict[str, int]:
        """Obtiene resumen por prioridad.
        
        Args:
            issues: Lista de issues
            
        Returns:
            Dict con conteo por prioridad
        """
        priorities = []
        for issue in issues:
            priority = issue.get('fields', {}).get('priority', {}).get('name', 'Unknown')
            priorities.append(priority)
        
        return dict(Counter(priorities))
    
    def get_project_summary(self, issues: List[Dict]) -> Dict[str, int]:
        """Obtiene resumen por proyecto.
        
        Args:
            issues: Lista de issues
            
        Returns:
            Dict con conteo por proyecto
        """
        projects = []
        for issue in issues:
            project = issue.get('fields', {}).get('project', {}).get('key', 'Unknown')
            projects.append(project)
        
        return dict(Counter(projects))
    
    def get_timeline_data(self, issues: List[Dict], days: int = 30) -> Dict[str, List]:
        """Obtiene datos para timeline de actualizaciones.
        
        Args:
            issues: Lista de issues
            days: Número de días a incluir
            
        Returns:
            Dict con datos de timeline
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        timeline_data = {}
        
        for issue in issues:
            updated_str = issue.get('fields', {}).get('updated')
            if not updated_str:
                continue
                
            try:
                updated_date = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
                if start_date <= updated_date <= end_date:
                    date_key = updated_date.strftime('%Y-%m-%d')
                    if date_key not in timeline_data:
                        timeline_data[date_key] = 0
                    timeline_data[date_key] += 1
            except Exception:
                continue
        
        # Llenar días faltantes con 0
        current_date = start_date
        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            if date_key not in timeline_data:
                timeline_data[date_key] = 0
            current_date += timedelta(days=1)
        
        # Ordenar por fecha
        sorted_dates = sorted(timeline_data.keys())
        return {
            'dates': sorted_dates,
            'counts': [timeline_data[date] for date in sorted_dates]
        }
    
    def export_to_csv(self, issues: List[Dict], filename: str) -> bool:
        """Exporta issues a CSV.
        
        Args:
            issues: Lista de issues
            filename: Nombre del archivo
            
        Returns:
            True si fue exitoso, False si hubo error
        """
        try:
            df = self.format_issues_for_display(issues)
            if df.empty:
                self.logger.warning("No hay datos para exportar")
                return False
            
            df.to_csv(filename, index=False, encoding='utf-8')
            self.logger.info(f"Datos exportados a: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error exportando CSV: {e}")
            return False
    
    def export_to_json(self, issues: List[Dict], filename: str) -> bool:
        """Exporta issues a JSON.
        
        Args:
            issues: Lista de issues
            filename: Nombre del archivo
            
        Returns:
            True si fue exitoso, False si hubo error
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(issues, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Datos exportados a: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error exportando JSON: {e}")
            return False
