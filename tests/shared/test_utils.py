#!/usr/bin/env python3
"""
Tests para utilidades.
"""

import pytest
from unittest.mock import patch, mock_open
from pathlib import Path
import logging
import os

from utils import (
    setup_logging, validate_env_file, format_number, 
    truncate_text, safe_get, create_example_env
)


class TestUtils:
    """Tests para utilidades."""
    
    def test_format_number(self):
        """Test formateo de números."""
        assert format_number(1000) == "1,000"
        assert format_number(1234567) == "1,234,567"
        assert format_number(100) == "100"
        assert format_number(0) == "0"
    
    def test_truncate_text(self):
        """Test truncado de texto."""
        # Texto corto
        result = truncate_text("Hola", 10)
        assert result == "Hola"
        
        # Texto largo
        result = truncate_text("Este es un texto muy largo", 10)
        assert len(result) == 10
        assert result.endswith("...")
        
        # Texto None
        result = truncate_text(None, 10)
        assert result is None
        
        # Sufijo personalizado
        result = truncate_text("Texto largo", 5, "!!")
        assert result.endswith("!!")
    
    def test_safe_get(self):
        """Test obtención segura de valores."""
        data = {
            'level1': {
                'level2': {
                    'value': 'found'
                }
            }
        }
        
        # Acceso exitoso
        result = safe_get(data, 'level1', 'level2', 'value')
        assert result == 'found'
        
        # Clave inexistente
        result = safe_get(data, 'level1', 'missing', 'value')
        assert result is None
        
        # Con valor por defecto
        result = safe_get(data, 'missing', default='default')
        assert result == 'default'
        
        # Diccionario None
        result = safe_get(None, 'key')
        assert result is None
    
    @patch('pathlib.Path.exists')
    @patch.dict('os.environ', {})
    def test_validate_env_file_missing_file(self, mock_exists):
        """Test validación con archivo .env faltante."""
        mock_exists.return_value = False
        
        result = validate_env_file()
        
        assert result['valid'] is False
        assert 'no encontrado' in result['message']
        assert result['missing_file'] is True
    
    @patch('pathlib.Path.exists')
    @patch.dict('os.environ', {
        'JIRA_BASE_URL': 'https://test.atlassian.net',
        'JIRA_EMAIL': 'test@example.com',
        'JIRA_TOKEN': 'test_token'
    })
    def test_validate_env_file_valid(self, mock_exists):
        """Test validación exitosa."""
        mock_exists.return_value = True
        
        result = validate_env_file()
        
        assert result['valid'] is True
        assert 'válida' in result['message']
    
    @patch('pathlib.Path.exists')  
    def test_validate_env_file_missing_vars(self, mock_exists):
        """Test validación con variables faltantes."""
        mock_exists.return_value = True
        
        # Usar patch.dict para limpiar completamente el entorno y solo dejar JIRA_BASE_URL
        with patch.dict('os.environ', {
            'JIRA_BASE_URL': 'https://test.atlassian.net'
        }, clear=True):
            # Mockear load_dotenv para que no cargue nada del archivo .env real
            with patch('dotenv.load_dotenv') as mock_load_dotenv:
                mock_load_dotenv.return_value = None
                result = validate_env_file()
        
        assert result['valid'] is False
        assert 'faltantes' in result['message']
        assert 'missing_vars' in result
        assert 'JIRA_EMAIL' in result['missing_vars']
        assert 'JIRA_TOKEN' in result['missing_vars']
    
    @patch('builtins.open', new_callable=mock_open)
    def test_create_example_env_success(self, mock_file):
        """Test creación exitosa de archivo .env.example."""
        result = create_example_env()
        
        assert result is True
        mock_file.assert_called_once_with('.env.example', 'w', encoding='utf-8')
        
        # Verificar que se escribió contenido
        handle = mock_file()
        handle.write.assert_called()
        
        # Verificar que el contenido incluye variables esperadas
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        assert 'JIRA_BASE_URL' in written_content
        assert 'JIRA_EMAIL' in written_content
        assert 'JIRA_TOKEN' in written_content
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_create_example_env_failure(self, mock_file):
        """Test fallo en creación de archivo."""
        result = create_example_env()
        
        assert result is False
    
    @patch('pathlib.Path.mkdir')
    def test_setup_logging(self, mock_mkdir):
        """Test configuración de logging."""
        logger = setup_logging("DEBUG")
        
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.DEBUG
        
        # Verificar que se creó directorio de logs
        mock_mkdir.assert_called_once_with(exist_ok=True)
        
        # Verificar que se agregaron handlers
        assert len(logger.handlers) >= 2  # file + console
