# 🔧 Troubleshooting - Solución de Problemas

## ❌ Problema: ModuleNotFoundError: No module named 'plotly'

### 🎯 **Descripción del Error**
```
ModuleNotFoundError: No module named 'plotly'
```

### 🔍 **Causa**
Streamlit se está ejecutando desde un entorno virtual incorrecto que no tiene las dependencias instaladas.

### ✅ **Solución Rápida**

#### Método 1: Usar Scripts de Inicio (Recomendado)
```bash
# PowerShell
.\start_app.ps1

# CMD
start_app.bat
```

#### Método 2: Manual
```bash
# 1. Detener cualquier Streamlit en ejecución
taskkill /F /IM streamlit.exe

# 2. Activar entorno virtual correcto
C:\Temp\VibeCoding\.venv\Scripts\Activate.ps1

# 3. Iniciar con ruta completa
C:\Temp\VibeCoding\.venv\Scripts\streamlit.exe run app.py
```

### 🔍 **Verificación**
```bash
# Verificar entorno correcto
C:\Temp\VibeCoding\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"

# Verificar dependencias
C:\Temp\VibeCoding\.venv\Scripts\pip.exe list | findstr "plotly streamlit pandas"
```

---

## ❌ Problema: Variables de entorno faltantes

### 🎯 **Descripción del Error**
```
Variables de entorno faltantes: JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN
```

### ✅ **Solución**
```bash
# Verificar archivo .env existe
if (Test-Path ".env") { "✅ .env existe" } else { "❌ .env no encontrado" }

# Ejecutar verificación
python verify_setup.py
```

---

## ❌ Problema: Conexión Jira fallida

### 🎯 **Descripción del Error**
```
❌ Error de conexión: 401 Unauthorized
```

### ✅ **Solución**
1. **Verificar credenciales** en `.env`
2. **Regenerar token** en [Atlassian](https://id.atlassian.com/manage-profile/security/api-tokens)
3. **Verificar URL** base de Jira

```bash
# Diagnóstico completo
python diagnose_system.py
```

---

## 📋 **Comandos de Diagnóstico Útiles**

### 🔍 **Verificación Completa**
```bash
# Estado del sistema
python verify_setup.py

# Diagnóstico detallado  
python diagnose_system.py

# Test de conexión Jira
python jira_viewer.py --test
```

### 🧪 **Tests**
```bash
# Tests rápidos
pytest tests/test_config.py -v

# Tests completos
pytest --cov=src

# Test específico de conexión
pytest tests/test_jira_client.py::test_connection -v
```

### 🔧 **Entorno Virtual**
```bash
# Ver entorno activo
python -c "import sys; print(sys.executable)"

# Ver dependencias instaladas
pip list

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

---

## 🆘 **Problemas Comunes**

### 1. **Puerto 8501 ocupado**
```bash
# Ver qué usa el puerto
netstat -ano | findstr :8501

# Matar proceso si es necesario
taskkill /F /PID <numero_pid>
```

### 2. **Permisos de ejecución PowerShell**
```bash
# Permitir scripts temporalmente
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. **Cache de Streamlit corrupto**
```bash
# Limpiar cache
C:\Temp\VibeCoding\.venv\Scripts\streamlit.exe cache clear
```

---

## 🔄 **Reinstalación Completa**

Si nada funciona, reinstalación limpia:

```bash
# 1. Eliminar entorno virtual
Remove-Item -Recurse -Force .venv

# 2. Crear nuevo entorno
python -m venv .venv

# 3. Activar entorno
.venv\Scripts\Activate.ps1

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Verificar instalación
python verify_setup.py

# 6. Iniciar aplicación
.\start_app.ps1
```

---

## 📞 **Contacto**

Si persisten los problemas:
- ✅ Ejecutar `python diagnose_system.py`
- ✅ Copiar output completo
- ✅ Incluir archivo `.env` (SIN tokens reales)
- ✅ Especificar sistema operativo y versión Python