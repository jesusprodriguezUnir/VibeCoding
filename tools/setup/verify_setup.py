#!/usr/bin/env python3
"""
Script simple para verificar que la aplicación funciona correctamente.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def main():
    print("🚀 VERIFICACIÓN RÁPIDA DEL SISTEMA")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Verificar variables
    base_url = os.getenv('JIRA_BASE_URL')
    email = os.getenv('JIRA_EMAIL')
    token = os.getenv('JIRA_TOKEN')
    
    if not all([base_url, email, token]):
        print("❌ Variables de entorno faltantes!")
        print("📋 Solución:")
        print("1. Verificar que existe .env en el directorio actual")
        print("2. Verificar que .env contiene las 3 variables")
        print("3. Reiniciar la terminal/aplicación")
        return False
    
    print(f"✅ Variables cargadas correctamente")
    print(f"   JIRA_BASE_URL: {base_url}")
    print(f"   JIRA_EMAIL: {email}")
    print(f"   JIRA_TOKEN: {token[:10]}...{token[-10:]}")
    
    # Agregar src al path
    sys.path.append(str(Path(__file__).parent / "src"))
    
    try:
        from jira_client import JiraClient
        
        print("\\n🔗 Probando conexión...")
        client = JiraClient()
        result = client.test_connection()
        
        if result['success']:
            print(f"✅ {result['message']}")
            
            # Probar obtener algunos issues
            print("\\n📋 Probando obtener issues...")
            issues_result = client.get_my_issues(max_results=5)
            
            if issues_result['success']:
                print(f"✅ {len(issues_result['issues'])} issues obtenidos")
                
                if issues_result['issues']:
                    first_issue = issues_result['issues'][0]
                    print(f"   Ejemplo: {first_issue['key']} - {first_issue['fields']['summary'][:50]}...")
                
                return True
            else:
                print(f"❌ Error obteniendo issues: {issues_result.get('error')}")
                return False
        else:
            print(f"❌ {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\\n🎉 TODO FUNCIONA CORRECTAMENTE!")
        print("💡 Puedes ejecutar: streamlit run app.py")
    else:
        print("\\n🔧 Revisa la configuración y vuelve a intentar")