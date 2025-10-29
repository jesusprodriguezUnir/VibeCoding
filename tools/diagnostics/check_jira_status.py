#!/usr/bin/env python3
"""
Script para verificar el estado de la instancia de Jira.
"""

import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv('JIRA_BASE_URL')
email = os.getenv('JIRA_EMAIL')
token = os.getenv('JIRA_TOKEN')

print(f"🔍 Verificando instancia: {base_url}")

# Probar acceso básico
try:
    print("\n1. Probando acceso básico al dominio...")
    response = requests.get(base_url, timeout=10)
    print(f"   Estado: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("   ✅ Dominio accesible")
    else:
        print(f"   ❌ Error {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Error de conexión: {e}")

# Probar endpoints de API
auth = HTTPBasicAuth(email, token)
endpoints = [
    "/rest/api/2/myself",
    "/rest/api/3/myself", 
    "/rest/api/2/serverInfo",
    "/rest/api/3/serverInfo"
]

for endpoint in endpoints:
    try:
        print(f"\n2. Probando {endpoint}...")
        response = requests.get(f"{base_url}{endpoint}", auth=auth, timeout=10)
        print(f"   Estado: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Endpoint funcionando")
            if 'myself' in endpoint:
                data = response.json()
                print(f"   Usuario: {data.get('displayName')} ({data.get('emailAddress')})")
        else:
            print(f"   ❌ Error {response.status_code}: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n🔍 Verificación completa")