#!/usr/bin/env python3
"""
Configuración y fixtures para tests.
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Agregar core al path
sys.path.append(str(Path(__file__).parent.parent))

from core.jira_client import JiraClient
from core.data_processor import JiraDataProcessor
from core.config import Config


@pytest.fixture
def mock_jira_response():
    """Fixture con respuesta mock de Jira."""
    return {
        'issues': [
            {
                'key': 'TEST-123',
                'fields': {
                    'summary': 'Test issue summary',
                    'status': {'name': 'En Progreso'},
                    'priority': {'name': 'Alto'},
                    'assignee': {'displayName': 'Test User'},
                    'reporter': {'displayName': 'Test Reporter'},
                    'project': {'key': 'TEST'},
                    'issuetype': {'name': 'Bug'},
                    'created': '2023-01-01T10:00:00.000Z',
                    'updated': '2023-01-02T15:30:00.000Z',
                    'duedate': '2023-01-10',
                    'labels': ['urgent', 'backend'],
                    'components': []
                }
            },
            {
                'key': 'TEST-124',
                'fields': {
                    'summary': 'Another test issue',
                    'status': {'name': 'Cerrada'},
                    'priority': {'name': 'Bajo'},
                    'assignee': {'displayName': 'Test User'},
                    'reporter': {'displayName': 'Test Reporter'},
                    'project': {'key': 'TEST'},
                    'issuetype': {'name': 'Task'},
                    'created': '2023-01-01T09:00:00.000Z',
                    'updated': '2023-01-03T12:00:00.000Z',
                    'duedate': None,
                    'labels': [],
                    'components': []
                }
            }
        ],
        'total': 2,
        'startAt': 0,
        'maxResults': 50
    }


@pytest.fixture
def mock_user_response():
    """Fixture con respuesta de usuario mock."""
    return {
        'displayName': 'Test User',
        'emailAddress': 'test@example.com',
        'accountId': '12345'
    }


@pytest.fixture
def sample_issues(mock_jira_response):
    """Fixture con issues de ejemplo."""
    return mock_jira_response['issues']


@pytest.fixture
def jira_client_mock():
    """Fixture con JiraClient mockeado."""
    with patch.dict('os.environ', {
        'JIRA_BASE_URL': 'https://test.atlassian.net',
        'JIRA_EMAIL': 'test@example.com',
        'JIRA_TOKEN': 'test_token'
    }):
        yield JiraClient


@pytest.fixture
def data_processor():
    """Fixture con procesador de datos."""
    return JiraDataProcessor()


@pytest.fixture
def temp_file(tmp_path):
    """Fixture para archivos temporales."""
    return tmp_path / "test_export.csv"
