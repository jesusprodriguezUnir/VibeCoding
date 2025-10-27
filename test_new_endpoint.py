#!/usr/bin/env python3
"""
Probar el nuevo endpoint de JQL
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

auth = HTTPBasicAuth(email, token)

# Probar el nuevo endpoint
url = f"{base_url}/rest/api/3/search/jql"
params = {
    'jql': 'assignee = currentUser()',
    'maxResults': 5,
    'fields': 'key,summary,status,assignee'
}

try:
    print(f"🔍 Probando: {url}")
    print(f"Parámetros: {params}")
    
    response = requests.get(url, auth=auth, params=params, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Issues encontrados: {len(data.get('issues', []))}")
        
        for issue in data.get('issues', [])[:3]:
            print(f"  - {issue['key']}: {issue['fields']['summary'][:60]}...")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Excepción: {str(e)}")