#!/usr/bin/env python3
"""
Tests para configuración.
"""

import pytest
from unittest.mock import patch

from src.config import Config, JiraConfig, AppConfig


class TestJiraConfig:
    """Tests para JiraConfig."""
    
    def test_jira_config_creation(self):
        """Test creación de configuración Jira."""
        config = JiraConfig(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            token="test_token"
        )
        
        assert config.base_url == "https://test.atlassian.net"
        assert config.email == "test@example.com"
        assert config.token == "test_token"
        assert config.api_version == "3"  # valor por defecto
        assert config.timeout == 30  # valor por defecto


class TestAppConfig:
    """Tests para AppConfig."""
    
    def test_app_config_creation(self):
        """Test creación de configuración de app."""
        config = AppConfig()
        
        assert config.app_title == "Visualizador de Asignaciones Jira"
        assert config.app_icon == "📊"
        assert config.page_config is not None
        assert config.page_config["layout"] == "wide"


class TestConfig:
    """Tests para Config."""
    
    def test_default_fields(self):
        """Test campos por defecto."""
        fields = Config.DEFAULT_FIELDS
        
        assert 'key' in fields
        assert 'summary' in fields
        assert 'status' in fields
        assert 'assignee' in fields
    
    def test_predefined_queries(self):
        """Test consultas predefinidas."""
        queries = Config.PREDEFINED_QUERIES
        
        assert 'Mis Issues' in queries
        assert 'En Progreso' in queries
        assert 'Alta Prioridad' in queries
        
        # Verificar que las consultas contienen JQL válido
        for query_name, jql in queries.items():
            assert 'assignee = currentUser()' in jql
            assert 'ORDER BY' in jql
    
    def test_status_colors(self):
        """Test colores de estados."""
        colors = Config.STATUS_COLORS
        
        assert 'NUEVA' in colors
        assert 'EN CURSO' in colors
        assert 'CERRADA' in colors
        
        # Verificar que son códigos de color válidos
        for color in colors.values():
            assert color.startswith('#')
            assert len(color) == 7  # #RRGGBB
    
    def test_priority_colors(self):
        """Test colores de prioridades."""
        colors = Config.PRIORITY_COLORS
        
        assert 'Crítico' in colors
        assert 'Alto' in colors
        assert 'Bajo' in colors
        
        # Verificar que son códigos de color válidos
        for color in colors.values():
            assert color.startswith('#')
    
    @patch.dict('os.environ', {
        'JIRA_BASE_URL': 'https://test.atlassian.net',
        'JIRA_EMAIL': 'test@example.com',
        'JIRA_TOKEN': 'test_token'
    })
    def test_get_jira_config_success(self):
        """Test obtención exitosa de configuración Jira."""
        config = Config.get_jira_config()
        
        assert isinstance(config, JiraConfig)
        assert config.base_url == 'https://test.atlassian.net'
        assert config.email == 'test@example.com'
        assert config.token == 'test_token'
    
    def test_get_jira_config_missing_vars(self):
        """Test fallo por variables faltantes."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Faltan variables de entorno"):
                Config.get_jira_config()
    
    def test_get_app_config(self):
        """Test obtención de configuración de app."""
        config = Config.get_app_config()
        
        assert isinstance(config, AppConfig)
        assert config.app_title == "Visualizador de Asignaciones Jira"
    
    def test_chart_config(self):
        """Test configuración de gráficos."""
        chart_config = Config.CHART_CONFIG
        
        assert 'height' in chart_config
        assert 'use_container_width' in chart_config
        assert chart_config['height'] == 400
        assert chart_config['use_container_width'] is True
