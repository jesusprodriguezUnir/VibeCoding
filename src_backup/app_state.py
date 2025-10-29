"""
Gestión del estado de la aplicación.
"""
import streamlit as st
from .jira_client import JiraClient
from .data_processor import JiraDataProcessor
from .config import Config


def init_session_state():
    """Inicializa el estado de sesión de Streamlit."""
    if 'cached_issues' not in st.session_state:
        st.session_state.cached_issues = []
    elif not isinstance(st.session_state.cached_issues, list):
        # Corregir si por alguna razón no es una lista
        st.session_state.cached_issues = []
    
    if 'data_processor' not in st.session_state:
        st.session_state.data_processor = None
    
    if 'client' not in st.session_state:
        st.session_state.client = None
    
    if 'jira_token' not in st.session_state:
        st.session_state.jira_token = ''
    
    if 'base_url' not in st.session_state:
        st.session_state.base_url = ''


def check_configuration() -> bool:
    """
    Verifica la configuración necesaria.
    
    Returns:
        bool: True si la configuración es válida, False en caso contrario.
    """
    try:
        # Cargar variables de entorno explícitamente
        from dotenv import load_dotenv
        load_dotenv()
        
        import os
        base_url = os.getenv('JIRA_BASE_URL')
        email = os.getenv('JIRA_EMAIL')
        jira_token = os.getenv('JIRA_TOKEN')
        
        # Verificar configuración mínima
        if not base_url:
            st.error("❌ URL de Jira no configurada en .env (JIRA_BASE_URL)")
            return False
        
        if not email:
            st.error("❌ Email de usuario no configurado en .env (JIRA_EMAIL)")
            return False
        
        if not jira_token:
            st.error("❌ Token de Jira no configurado en .env (JIRA_TOKEN)")
            return False
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error verificando configuración: {str(e)}")
        return False


def create_jira_client() -> bool:
    """
    Crea y configura el cliente de Jira.
    
    Returns:
        bool: True si el cliente se creó exitosamente, False en caso contrario.
    """
    try:
        if not check_configuration():
            return False
        
        # Cargar variables de entorno explícitamente
        from dotenv import load_dotenv
        load_dotenv()
        
        import os
        base_url = os.getenv('JIRA_BASE_URL')
        email = os.getenv('JIRA_EMAIL')
        jira_token = os.getenv('JIRA_TOKEN')
        
        if not st.session_state.client:
            st.session_state.client = JiraClient(
                base_url=base_url,
                email=email,
                token=jira_token
            )
            st.session_state.base_url = base_url
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error creando cliente Jira: {str(e)}")
        return False


def clear_cache():
    """Limpia el caché de datos."""
    st.session_state.cached_issues = []
    st.session_state.data_processor = None
    st.success("🗑️ Caché limpiado exitosamente")