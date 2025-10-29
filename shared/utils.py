#!/usr/bin/env python3
"""
Utilidades comunes para la aplicación.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configura el sistema de logging.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Logger configurado
    """
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configurar handler para archivo
    file_handler = logging.FileHandler(
        log_dir / f"jira_app_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler.setFormatter(formatter)
    
    # Configurar handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configurar logger raíz
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def validate_env_file() -> Dict[str, Any]:
    """Valida que el archivo .env existe y tiene las variables necesarias.
    
    Returns:
        Dict con resultado de validación
    """
    from dotenv import load_dotenv
    
    env_file = Path(".env")
    
    if not env_file.exists():
        return {
            'valid': False,
            'message': 'Archivo .env no encontrado. Ejecuta: cp .env.example .env y configura tus credenciales.',
            'missing_file': True
        }
    
    # Cargar explícitamente el archivo .env
    load_dotenv(env_file)
    
    # Verificar variables requeridas
    required_vars = ['JIRA_BASE_URL', 'JIRA_EMAIL', 'JIRA_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        return {
            'valid': False,
            'message': f'Variables de entorno faltantes: {", ".join(missing_vars)}',
            'missing_vars': missing_vars
        }
    
    return {
        'valid': True,
        'message': 'Configuración válida'
    }


def format_number(num: int) -> str:
    """Formatea números con separadores de miles.
    
    Args:
        num: Número a formatear
        
    Returns:
        Número formateado como string
    """
    return f"{num:,}"


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Trunca texto si excede la longitud máxima.
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca
        
    Returns:
        Texto truncado
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def safe_get(dictionary: Dict, *keys, default=None) -> Any:
    """Obtiene valor de diccionario anidado de forma segura.
    
    Args:
        dictionary: Diccionario fuente
        *keys: Claves para navegar
        default: Valor por defecto si no se encuentra
        
    Returns:
        Valor encontrado o default
    """
    for key in keys:
        if isinstance(dictionary, dict) and key in dictionary:
            dictionary = dictionary[key]
        else:
            return default
    return dictionary


def create_example_env() -> bool:
    """Crea archivo .env.example si no existe.
    
    Returns:
        True si se creó exitosamente
    """
    example_content = '''# Configuración de Jira - NO SUBIR A GITHUB
# Copia este archivo a .env y completa con tus datos reales

JIRA_BASE_URL=https://tu-instancia.atlassian.net
JIRA_EMAIL=tu-email@empresa.com
JIRA_TOKEN=tu_token_aqui

# Ejemplos:
# JIRA_BASE_URL=https://miempresa.atlassian.net
# JIRA_EMAIL=juan.perez@miempresa.com
# JIRA_TOKEN=ATATT3xFfGF0T4JQR7x...
'''
    
    try:
        with open('.env.example', 'w', encoding='utf-8') as f:
            f.write(example_content)
        return True
    except Exception:
        return False
