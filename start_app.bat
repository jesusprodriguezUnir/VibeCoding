@echo off
echo 🚀 Iniciando Jira Viewer...
cd /d "C:\Temp\VibeCoding"
echo 🔧 Activando entorno virtual...
call C:\Temp\VibeCoding\.venv\Scripts\activate.bat
echo 🌐 Iniciando aplicación en http://localhost:8501
echo 📋 Presiona Ctrl+C para detener
C:\Temp\VibeCoding\.venv\Scripts\streamlit.exe run app.py