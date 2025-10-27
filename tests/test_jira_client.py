#!/usr/bin/env python3
"""
Tests para JiraClient.
"""

import pytest
import responses
from unittest.mock import patch, Mock
import requests

from src.jira_client import JiraClient, JiraAPIError


class TestJiraClient:
    """Tests para la clase JiraClient."""
    
    def test_init_with_params(self):
        """Test inicialización con parámetros."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            token="test_token"
        )
        
        assert client.base_url == "https://test.atlassian.net"
        assert client.email == "test@example.com"
        assert client.token == "test_token"
        assert client.api_url == "https://test.atlassian.net/rest/api/3"
    
    def test_init_without_env_vars(self):
        """Test que falla sin variables de entorno."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Faltan credenciales"):
                JiraClient()
    
    @patch.dict('os.environ', {
        'JIRA_BASE_URL': 'https://test.atlassian.net',
        'JIRA_EMAIL': 'test@example.com',
        'JIRA_TOKEN': 'test_token'
    })
    def test_init_with_env_vars(self):
        """Test inicialización con variables de entorno."""
        client = JiraClient()
        
        assert client.base_url == "https://test.atlassian.net"
        assert client.email == "test@example.com"
        assert client.token == "test_token"
    
    @responses.activate
    def test_test_connection_success(self, jira_client_mock, mock_user_response):
        """Test conexión exitosa."""
        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/myself",
            json=mock_user_response,
            status=200
        )
        
        client = jira_client_mock(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            token="test_token"
        )
        
        result = client.test_connection()
        
        assert result['success'] is True
        assert 'Test User' in result['message']
        assert result['user'] == mock_user_response
    
    @responses.activate
    def test_test_connection_failure(self, jira_client_mock):
        """Test fallo de conexión."""
        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/myself",
            json={'error': 'Unauthorized'},
            status=401
        )
        
        client = jira_client_mock(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            token="test_token"
        )
        
        result = client.test_connection()
        
        assert result['success'] is False
        assert 'error' in result
    
    @responses.activate
    def test_search_issues_success(self, jira_client_mock, mock_jira_response):
        """Test búsqueda exitosa de issues."""
        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search/jql",
            json=mock_jira_response,
            status=200
        )
        
        client = jira_client_mock(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            token="test_token"
        )
        
        result = client.search_issues("assignee = currentUser()")
        
        assert result['success'] is True
        assert len(result['issues']) == 2
        assert result['total'] == 2
    
    @responses.activate
    def test_search_issues_failure(self, jira_client_mock):
        """Test fallo en búsqueda de issues."""
        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search/jql",
            json={'error': 'Bad Request'},
            status=400
        )
        
        client = jira_client_mock(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            token="test_token"
        )
        
        result = client.search_issues("invalid jql")
        
        assert result['success'] is False
        assert result['issues'] == []
    
    def test_get_my_issues_jql_construction(self, jira_client_mock):
        """Test construcción correcta de JQL."""
        client = jira_client_mock(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            token="test_token"
        )
        
        with patch.object(client, 'search_issues') as mock_search:
            client.get_my_issues(status_filter="In Progress", project_filter="TEST")
            
            # Verificar que se llamó con el JQL correcto
            expected_jql = 'assignee = currentUser() AND status = "In Progress" AND project = "TEST" ORDER BY updated DESC'
            mock_search.assert_called_once_with(expected_jql, 100)
    
    def test_get_recent_issues_jql_construction(self, jira_client_mock):
        """Test construcción JQL para issues recientes."""
        client = jira_client_mock(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            token="test_token"
        )
        
        with patch.object(client, 'search_issues') as mock_search:
            client.get_recent_issues(days=7)
            
            expected_jql = "assignee = currentUser() AND updated >= -7d ORDER BY updated DESC"
            mock_search.assert_called_once_with(expected_jql, 100)
