#!/usr/bin/env python3
"""
Script de diagnóstico para Jira
"""

import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

base_url = os.getenv('JIRA_BASE_URL')
email = os.getenv('JIRA_EMAIL')
token = os.getenv('JIRA_TOKEN')

print(f"URL Base: {base_url}")
print(f"Email: {email}")
print(f"Token: {token[:10]}...{token[-10:] if len(token) > 20 else token}")

auth = HTTPBasicAuth(email, token)

# Probar diferentes endpoints
endpoints = [
    "/rest/api/2/myself",
    "/rest/api/3/myself", 
    "/rest/api/2/search?jql=assignee=currentUser()&maxResults=1",
    "/rest/api/3/search?jql=assignee=currentUser()&maxResults=1",
    "/rest/api/2/project",
    "/rest/api/3/project"
]

for endpoint in endpoints:
    try:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 Probando: {url}")
        response = requests.get(url, auth=auth, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'issues' in data:
                print(f"   Issues encontrados: {len(data['issues'])}")
            elif 'displayName' in data:
                print(f"   Usuario: {data['displayName']}")
            elif isinstance(data, list):
                print(f"   Elementos: {len(data)}")
            else:
                print(f"   Respuesta válida: {list(data.keys())[:5]}")
        else:
            print(f"   Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   Excepción: {str(e)}")