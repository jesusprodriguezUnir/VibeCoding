"""
Utilidades comunes para los componentes UI.
"""
import streamlit as st
from typing import List, Dict, Any, Optional


def get_safe_issues() -> Optional[List[Dict[str, Any]]]:
    """
    Obtiene los issues del session state de manera segura.
    
    Returns:
        Lista de issues si existe y es válida, None en caso contrario.
    """
    cached_issues = st.session_state.get('cached_issues')
    
    if cached_issues and isinstance(cached_issues, list):
        return cached_issues
    
    return None


def validate_issues_data() -> bool:
    """
    Valida que haya datos de issues válidos.
    
    Returns:
        True si hay datos válidos, False en caso contrario.
    """
    issues = get_safe_issues()
    return issues is not None and len(issues) > 0


def get_issues_count() -> int:
    """
    Obtiene el número de issues de manera segura.
    
    Returns:
        Número de issues o 0 si no hay datos válidos.
    """
    issues = get_safe_issues()
    return len(issues) if issues else 0