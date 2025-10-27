# Makefile para el proyecto Jira Visualizer

.PHONY: help install test lint format run clean setup

# Variables
PYTHON := python
PIP := pip
STREAMLIT := streamlit

help:
	@echo "Comandos disponibles:"
	@echo "  setup     - Configuración inicial del proyecto"
	@echo "  install   - Instalar dependencias"
	@echo "  test      - Ejecutar tests"
	@echo "  test-cov  - Ejecutar tests con cobertura"
	@echo "  lint      - Verificar código con linters"
	@echo "  format    - Formatear código"
	@echo "  run       - Ejecutar aplicación Streamlit"
	@echo "  run-cli   - Ejecutar versión CLI"
	@echo "  clean     - Limpiar archivos temporales"
	@echo "  docs      - Generar documentación"

setup:
	@echo "Configurando proyecto..."
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Creando archivo .env de ejemplo..."
	$(PYTHON) -c "from src.utils import create_example_env; create_example_env()"
	@echo "Setup completado. Configura tu archivo .env antes de continuar."

install:
	@echo "Instalando dependencias..."
	$(PIP) install -r requirements.txt

test:
	@echo "Ejecutando tests..."
	$(PYTHON) -m pytest

test-cov:
	@echo "Ejecutando tests con cobertura..."
	$(PYTHON) -m pytest --cov=src --cov-report=html --cov-report=term

test-unit:
	@echo "Ejecutando solo tests unitarios..."
	$(PYTHON) -m pytest -m "unit or not integration"

test-integration:
	@echo "Ejecutando tests de integración..."
	$(PYTHON) -m pytest -m integration

lint:
	@echo "Verificando código..."
	$(PYTHON) -m flake8 src/ tests/
	$(PYTHON) -m mypy src/

format:
	@echo "Formateando código..."
	$(PYTHON) -m black src/ tests/ *.py

run:
	@echo "Iniciando aplicación Streamlit..."
	$(STREAMLIT) run app.py

run-cli:
	@echo "Ejecutando versión CLI..."
	$(PYTHON) jira_viewer.py --all

clean:
	@echo "Limpiando archivos temporales..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf logs/

check: lint test
	@echo "Todas las verificaciones completadas."

docs:
	@echo "La documentación está en los archivos .md del proyecto"

dev-install:
	@echo "Instalando dependencias de desarrollo..."
	$(PIP) install -e .
	$(PIP) install -r requirements.txt
