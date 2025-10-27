#!/usr/bin/env python3
"""
Script de debug para verificar la conexión con Jira.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Configurar path
sys.path.append(str(Path(__file__).parent / "src"))

# Cargar variables de entorno
load_dotenv()

from src.jira_client import JiraClient

def test_jira_connection():
    """Prueba la conexión con Jira."""
    print("🔍 Verificando configuración...")
    
    base_url = os.getenv('JIRA_BASE_URL')
    email = os.getenv('JIRA_EMAIL')
    token = os.getenv('JIRA_TOKEN')
    
    print(f"Base URL: {base_url}")
    print(f"Email: {email}")
    print(f"Token: {'✅ Configurado' if token else '❌ No configurado'}")
    
    if not all([base_url, email, token]):
        print("❌ Configuración incompleta")
        return False
    
    print("\n🚀 Creando cliente Jira...")
    try:
        client = JiraClient(
            base_url=base_url,
            email=email,
            token=token
        )
        print("✅ Cliente creado exitosamente")
        
        print("\n🔗 Probando conexión...")
        result = client.test_connection()
        if result:
            print("✅ Conexión exitosa")
            
            print("\n🔍 Probando consulta simple...")
            result = client.search_issues("assignee = currentUser()", max_results=5)
            if result.get('success', False):
                issues = result.get('issues', [])
                if issues:
                    print(f"✅ Consulta exitosa: {len(issues)} issues encontrados")
                    for i, issue in enumerate(issues[:3], 1):
                        print(f"  {i}. {issue['key']}: {issue['fields']['summary'][:50]}...")
                else:
                    print("⚠️ No se encontraron issues")
            else:
                print(f"❌ Error en consulta: {result.get('error', 'Error desconocido')}")
                return False
            
            return True
        else:
            print("❌ Error en la conexión")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_jira_connection()
    print(f"\n{'🎉 Todo OK' if success else '❌ Hay problemas'}")