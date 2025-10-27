#!/usr/bin/env python3
"""
Tests para JiraDataProcessor.
"""

import pytest
import pandas as pd
from datetime import datetime
import json
from pathlib import Path

from src.data_processor import JiraDataProcessor


class TestJiraDataProcessor:
    """Tests para la clase JiraDataProcessor."""
    
    def test_format_issues_for_display_empty(self, data_processor):
        """Test formateo con lista vacía."""
        result = data_processor.format_issues_for_display([])
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_format_issues_for_display_with_data(self, data_processor, sample_issues):
        """Test formateo con datos."""
        result = data_processor.format_issues_for_display(sample_issues)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'Key' in result.columns
        assert 'Summary' in result.columns
        assert 'Status' in result.columns
        
        # Verificar datos específicos
        first_row = result.iloc[0]
        assert first_row['Key'] == 'TEST-123'
        assert first_row['Status'] == 'En Progreso'
        assert first_row['Priority'] == 'Alto'
    
    def test_truncate_text(self, data_processor):
        """Test truncado de texto."""
        # Texto corto - no debería truncarse
        short_text = "Texto corto"
        result = data_processor._truncate_text(short_text, 50)
        assert result == short_text
        
        # Texto largo - debería truncarse
        long_text = "Este es un texto muy largo que debería ser truncado"
        result = data_processor._truncate_text(long_text, 20)
        assert len(result) == 23  # 20 + len('...')
        assert result.endswith('...')
    
    def test_get_user_name(self, data_processor):
        """Test extracción de nombre de usuario."""
        # Usuario válido
        user_data = {'displayName': 'John Doe'}
        result = data_processor._get_user_name(user_data)
        assert result == 'John Doe'
        
        # Usuario None
        result = data_processor._get_user_name(None)
        assert result == 'Unassigned'
        
        # Usuario sin displayName
        user_data = {'email': 'test@example.com'}
        result = data_processor._get_user_name(user_data)
        assert result == 'N/A'
    
    def test_format_date(self, data_processor):
        """Test formateo de fechas."""
        # Fecha con timezone
        date_str = '2023-01-01T10:00:00.000Z'
        result = data_processor._format_date(date_str)
        assert '2023-01-01' in result
        
        # Fecha solo con fecha
        date_str = '2023-01-01'
        result = data_processor._format_date(date_str)
        assert '2023-01-01' in result
        
        # Fecha None
        result = data_processor._format_date(None)
        assert result == 'N/A'
        
        # Fecha inválida
        result = data_processor._format_date('invalid_date')
        assert result == 'invalid_date'
    
    def test_format_labels(self, data_processor):
        """Test formateo de labels."""
        # Lista con labels
        labels = ['urgent', 'backend', 'bug']
        result = data_processor._format_labels(labels)
        assert result == 'urgent, backend, bug'
        
        # Lista vacía
        result = data_processor._format_labels([])
        assert result == 'None'
        
        # None
        result = data_processor._format_labels(None)
        assert result == 'None'
    
    def test_get_status_summary(self, data_processor, sample_issues):
        """Test resumen por estado."""
        result = data_processor.get_status_summary(sample_issues)
        
        assert isinstance(result, dict)
        assert 'En Progreso' in result
        assert 'Cerrada' in result
        assert result['En Progreso'] == 1
        assert result['Cerrada'] == 1
    
    def test_get_priority_summary(self, data_processor, sample_issues):
        """Test resumen por prioridad."""
        result = data_processor.get_priority_summary(sample_issues)
        
        assert isinstance(result, dict)
        assert 'Alto' in result
        assert 'Bajo' in result
        assert result['Alto'] == 1
        assert result['Bajo'] == 1
    
    def test_get_project_summary(self, data_processor, sample_issues):
        """Test resumen por proyecto."""
        result = data_processor.get_project_summary(sample_issues)
        
        assert isinstance(result, dict)
        assert 'TEST' in result
        assert result['TEST'] == 2
    
    def test_get_timeline_data(self, data_processor, sample_issues):
        """Test datos de timeline."""
        result = data_processor.get_timeline_data(sample_issues, days=7)
        
        assert isinstance(result, dict)
        assert 'dates' in result
        assert 'counts' in result
        assert len(result['dates']) == len(result['counts'])
        assert len(result['dates']) == 8  # 7 días + 1
    
    def test_export_to_csv(self, data_processor, sample_issues, temp_file):
        """Test exportación a CSV."""
        result = data_processor.export_to_csv(sample_issues, str(temp_file))
        
        assert result is True
        assert temp_file.exists()
        
        # Verificar contenido
        df = pd.read_csv(temp_file)
        assert len(df) == 2
        assert 'Key' in df.columns
    
    def test_export_to_csv_empty(self, data_processor, temp_file):
        """Test exportación CSV con datos vacíos."""
        result = data_processor.export_to_csv([], str(temp_file))
        
        assert result is False
        assert not temp_file.exists()
    
    def test_export_to_json(self, data_processor, sample_issues, tmp_path):
        """Test exportación a JSON."""
        json_file = tmp_path / "test.json"
        result = data_processor.export_to_json(sample_issues, str(json_file))
        
        assert result is True
        assert json_file.exists()
        
        # Verificar contenido
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert len(data) == 2
        assert data[0]['key'] == 'TEST-123'
    
    def test_export_to_json_empty(self, data_processor, tmp_path):
        """Test exportación JSON con datos vacíos."""
        json_file = tmp_path / "test.json"
        result = data_processor.export_to_json([], str(json_file))
        
        assert result is True  # JSON vacío es válido
        assert json_file.exists()
