#!/usr/bin/env python3
"""
Script de verificación y ejecución de VibeCoding
Verifica todos los requisitos y ejecuta la aplicación de forma segura.
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

def print_step(step, message):
    """Imprime un paso de la verificación"""
    print(f"[{step}] {message}")

def check_python_version():
    """Verifica la versión de Python"""
    print_step("1/7", "Verificando versión de Python...")
    if sys.version_info < (3, 9):
        print("❌ Error: Se requiere Python 3.9 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_virtual_env():
    """Verifica si estamos en un entorno virtual"""
    print_step("2/7", "Verificando entorno virtual...")
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("❌ Error: No se encontró el entorno virtual .venv")
        print("   Ejecuta: python -m venv .venv")
        return False
    
    # Verificar si estamos ejecutando desde el entorno virtual
    if sys.prefix == sys.base_prefix:
        print("⚠️  Advertencia: No estás en el entorno virtual")
        print("   Ejecuta: .venv\\Scripts\\Activate.ps1 (Windows)")
        return False
    
    print("✅ Entorno virtual activo")
    return True

def check_dependencies():
    """Verifica las dependencias principales"""
    print_step("3/7", "Verificando dependencias...")
    required_modules = [
        ('streamlit', 'Streamlit'),
        ('pandas', 'Pandas'),
        ('plotly', 'Plotly'),
        ('requests', 'Requests')
    ]
    
    missing = []
    for module, name in required_modules:
        if importlib.util.find_spec(module) is None:
            missing.append(name)
    
    if missing:
        print(f"❌ Error: Faltan dependencias: {', '.join(missing)}")
        print("   Ejecuta: pip install -r requirements.txt")
        return False
    
    print("✅ Dependencias instaladas")
    return True

def check_config():
    """Verifica la configuración de Jira"""
    print_step("4/7", "Verificando configuración...")
    try:
        # Intentar importar y verificar config
        sys.path.insert(0, str(Path.cwd()))
        from core.config import Config
        Config.get_jira_config()  # Verificar que la config es válida
        print("✅ Configuración de Jira válida")
        return True
    except Exception as e:
        print(f"❌ Error de configuración: {e}")
        print("   Configura tus credenciales en .env o .streamlit/secrets.toml")
        return False

def check_streamlit():
    """Verifica que Streamlit esté disponible"""
    print_step("5/7", "Verificando Streamlit...")
    try:
        result = subprocess.run([sys.executable, "-m", "streamlit", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ {version}")
            return True
        else:
            print("❌ Error: Streamlit no responde")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando Streamlit: {e}")
        return False

def check_port(port=8508):
    """Verifica si el puerto está disponible"""
    print_step("6/7", f"Verificando puerto {port}...")
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            print(f"✅ Puerto {port} disponible")
            return port
    except OSError:
        print(f"⚠️  Puerto {port} ocupado, probando {port + 1}...")
        return check_port(port + 1) if port < 8520 else None

def run_application(port):
    """Ejecuta la aplicación"""
    print_step("7/7", f"Iniciando aplicación en puerto {port}...")
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(port),
            "--server.headless", "false"
        ]
        
        print(f"📱 Ejecutando: {' '.join(cmd)}")
        print(f"🌐 URL: http://localhost:{port}")
        print("🛑 Presiona Ctrl+C para detener")
        print("-" * 50)
        
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n⏹️  Aplicación detenida por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando aplicación: {e}")

def main():
    """Función principal"""
    print("🚀 VibeCoding - Verificación y Arranque")
    print("=" * 50)
    
    # Verificaciones
    checks = [
        check_python_version(),
        check_virtual_env(),
        check_dependencies(),
        check_config(),
        check_streamlit()
    ]
    
    # Verificar puerto
    port = check_port()
    if port is None:
        print("❌ Error: No se encontró puerto disponible")
        return False
    
    # Si todas las verificaciones pasan
    if all(checks):
        print("\n🎉 Todas las verificaciones pasaron!")
        print("-" * 50)
        run_application(port)
    else:
        print("\n❌ Algunas verificaciones fallaron")
        print("🔧 Revisa los errores anteriores y corrige los problemas")
        return False

if __name__ == "__main__":
    main()