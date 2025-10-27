#!/usr/bin/env python3
"""
Script de diagnóstico para verificar configuración del sistema.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_environment():
    """Verifica la configuración del entorno."""
    print("🔍 DIAGNÓSTICO DEL SISTEMA")
    print("=" * 50)
    
    # 1. Verificar directorio actual
    current_dir = Path.cwd()
    print(f"📁 Directorio actual: {current_dir}")
    
    # 2. Verificar archivo .env
    env_file = current_dir / ".env"
    print(f"📄 Archivo .env existe: {env_file.exists()}")
    
    if env_file.exists():
        print(f"📄 Ruta .env: {env_file}")
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                print(f"📄 Líneas en .env: {len(lines)}")
                
                # Verificar variables específicas
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        if '=' in line:
                            key = line.split('=')[0].strip()
                            value = line.split('=', 1)[1].strip()
                            masked_value = value[:10] + "..." + value[-10:] if len(value) > 20 else value
                            print(f"   {key} = {masked_value}")
        except Exception as e:
            print(f"❌ Error leyendo .env: {e}")
    
    # 3. Cargar variables explícitamente
    print("\\n🔄 Cargando variables de entorno...")
    load_dotenv(env_file)
    
    # 4. Verificar variables después de cargar
    required_vars = ['JIRA_BASE_URL', 'JIRA_EMAIL', 'JIRA_TOKEN']
    print("\\n🔐 Variables de entorno después de load_dotenv():")
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked_value = value[:10] + "..." + value[-10:] if len(value) > 20 else value
            print(f"   ✅ {var} = {masked_value}")
        else:
            print(f"   ❌ {var} = None")
    
    # 5. Verificar path de Python
    print(f"\\n🐍 Python executable: {sys.executable}")
    print(f"🐍 Python version: {sys.version}")
    
    # 6. Verificar módulos importados
    print("\\n📦 Verificando módulos:")
    try:
        import requests
        print(f"   ✅ requests: {requests.__version__}")
    except ImportError:
        print("   ❌ requests: No instalado")
    
    try:
        import streamlit
        print(f"   ✅ streamlit: {streamlit.__version__}")
    except ImportError:
        print("   ❌ streamlit: No instalado")
    
    try:
        print("   ✅ python-dotenv: Disponible")
    except ImportError:
        print("   ❌ python-dotenv: No instalado")
    
    # 7. Probar carga de configuración
    print("\\n🧪 Probando carga de configuración...")
    try:
        sys.path.append(str(current_dir / "src"))
        from src.config import Config
        
        config = Config.get_jira_config()
        print(f"   ✅ Config cargada: {config.base_url}")
        
    except Exception as e:
        print(f"   ❌ Error cargando config: {e}")
    
    # 8. Probar conexión Jira
    print("\\n🔗 Probando conexión Jira...")
    try:
        from src.jira_client import JiraClient
        
        client = JiraClient()
        result = client.test_connection()
        
        if result['success']:
            print(f"   ✅ Conexión exitosa: {result['message']}")
        else:
            print(f"   ❌ Error conexión: {result['message']}")
            
    except Exception as e:
        print(f"   ❌ Error creando cliente: {e}")
    
    print("\\n" + "=" * 50)
    print("🏁 DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    check_environment()