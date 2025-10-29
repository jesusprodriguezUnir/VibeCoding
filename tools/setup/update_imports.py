#!/usr/bin/env python3
"""
Script para actualizar importaciones después de la reestructuración.
"""
import os
import re
from pathlib import Path

# Diccionario de mapeo de importaciones
IMPORT_MAPPINGS = {
    'from ': 'from ',
    'from jira_client': 'from core.jira_client',
    'from config': 'from core.config',
    'from app_state': 'from core.app_state',
    'from data_processor': 'from core.data_processor',
    'from utils': 'from shared.utils',
    'from data_fetcher': 'from shared.data_fetcher',
    'from ui.layout': 'from shared.ui.layout',
    'from ui.sidebar': 'from shared.ui.sidebar',
    'from ui.ui_utils': 'from shared.ui.ui_utils',
    'from ui.dashboard': 'from features.dashboards.standard',
    'from ui.dashboard_custom': 'from features.dashboards.custom',
    'from ui.widgets': 'from features.dashboards.widgets',
    'from ui.jql_queries': 'from features.jql.queries',
    'from ui.analysis': 'from features.analysis.reports',
    'from ui.issues': 'from features.issues.viewer',
    
    # Importaciones relativas que necesitan ajustarse
    'from core.jira_client': 'from core.jira_client',
    'from core.config': 'from core.config',
    'from core.data_processor': 'from core.data_processor',
    'from shared.utils': 'from shared.utils',
    'from shared.ui.ui_utils': 'from shared.ui.ui_utils',
    'from features.jql.queries': 'from features.jql.queries',
}

def update_imports_in_file(file_path):
    """Actualiza las importaciones en un archivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Aplicar mapeos de importaciones
        for old_import, new_import in IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # Si hubo cambios, escribir el archivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Actualizado: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal."""
    base_dir = Path(".")
    
    # Directorios a procesar
    dirs_to_process = [
        "core", "features", "shared", "tools", "tests"
    ]
    
    # Extensiones de archivo a procesar
    extensions = [".py"]
    
    total_files = 0
    updated_files = 0
    
    for dir_name in dirs_to_process:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            for ext in extensions:
                for file_path in dir_path.rglob(f"*{ext}"):
                    total_files += 1
                    if update_imports_in_file(file_path):
                        updated_files += 1
    
    print(f"\n📊 Resumen:")
    print(f"   Archivos procesados: {total_files}")
    print(f"   Archivos actualizados: {updated_files}")
    print(f"   Sin cambios: {total_files - updated_files}")

if __name__ == "__main__":
    main()