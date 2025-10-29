#!/usr/bin/env python3
"""
Script para probar específicamente el endpoint de búsqueda de Jira.
"""

import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
import json

load_dotenv()

base_url = os.getenv('JIRA_BASE_URL')
email = os.getenv('JIRA_EMAIL')
token = os.getenv('JIRA_TOKEN')

auth = HTTPBasicAuth(email, token)

print(f"🔍 Probando endpoint de búsqueda en: {base_url}")

# Probar diferentes variaciones del endpoint de búsqueda
test_configs = [
    {
        "name": "API v2 - GET con parámetros simples",
        "url": f"{base_url}/rest/api/2/search",
        "method": "GET",
        "params": {
            "jql": "assignee = currentUser()",
            "maxResults": 5
        }
    },
    {
        "name": "API v3 - GET con parámetros simples", 
        "url": f"{base_url}/rest/api/3/search",
        "method": "GET",
        "params": {
            "jql": "assignee = currentUser()",
            "maxResults": 5
        }
    },
    {
        "name": "API v2 - POST con JSON",
        "url": f"{base_url}/rest/api/2/search",
        "method": "POST",
        "json": {
            "jql": "assignee = currentUser()",
            "maxResults": 5,
            "fields": ["key", "summary", "status"]
        }
    }
]

for config in test_configs:
    print(f"\n🧪 {config['name']}")
    try:
        if config['method'] == 'GET':
            response = requests.get(
                config['url'], 
                auth=auth, 
                params=config.get('params'),
                timeout=10
            )
        else:
            response = requests.post(
                config['url'],
                auth=auth,
                json=config.get('json'),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
        
        print(f"   Estado: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            issues = data.get('issues', [])
            print(f"   ✅ Éxito: {len(issues)} issues encontrados")
            if issues:
                print(f"   Primer issue: {issues[0]['key']} - {issues[0]['fields']['summary'][:50]}...")
        else:
            print(f"   ❌ Error {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")

print("\n🔍 Pruebas de búsqueda completas")