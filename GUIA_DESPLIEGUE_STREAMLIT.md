# 🚀 Guía de Despliegue - Streamlit Cloud

## VibeCoding - Visualizador de Asignaciones Jira

### 📋 Requisitos Previos

1. **Repositorio en GitHub**: Tu código debe estar en un repositorio público de GitHub
2. **Credenciales Jira**: Necesitas tus credenciales de API de Jira
3. **Cuenta Streamlit**: Crear cuenta gratuita en [share.streamlit.io](https://share.streamlit.io)

---

## 🔑 Paso 1: Preparar Credenciales Jira

### Obtener Token de API de Jira:

1. Ve a tu perfil de Jira: `https://tu-instancia.atlassian.net/jira/people/search`
2. Haz clic en tu avatar → **Account Settings**
3. En la pestaña **Security** → **API tokens** → **Create API token**
4. Guarda el token generado (solo se muestra una vez)

### Información que necesitarás:
- **Base URL**: `https://tu-instancia.atlassian.net`
- **Email**: Tu email de cuenta Jira
- **Token**: El token API generado

---

## 🌐 Paso 2: Desplegar en Streamlit Cloud

### 2.1 Conectar Repositorio

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** con GitHub
3. Haz clic en **"New app"**
4. Selecciona tu repositorio: `jesusprodriguezUnir/VibeCoding`
5. **Branch**: `main` (o tu rama principal)
6. **Main file path**: `app.py`
7. **App URL**: Elige un nombre único (ej: `vibecoding-jira-dashboard`)

### 2.2 Configurar Secrets

1. **ANTES** de hacer clic en "Deploy", ve a **"Advanced settings"**
2. En la sección **"Secrets"**, pega exactamente esto:

```toml
[jira]
base_url = "https://tu-instancia.atlassian.net"
email = "tu-email@ejemplo.com"
token = "tu-api-token-aqui"
```

3. **Reemplaza** con tus valores reales:
   - `tu-instancia` → nombre de tu instancia Jira
   - `tu-email@ejemplo.com` → tu email de Jira
   - `tu-api-token-aqui` → el token que generaste

### 2.3 Desplegar

1. Haz clic en **"Deploy!"**
2. Espera 2-3 minutos mientras se instala
3. Tu app estará disponible en: `https://[nombre-elegido].streamlit.app`

---

## ✅ Paso 3: Verificar Funcionamiento

### Pruebas básicas:

1. **Conexión Jira**: La app debe mostrar el estado de conexión
2. **Carga de datos**: Debe poder cargar tus issues de Jira
3. **Visualizaciones**: Los gráficos deben renderizarse correctamente

### Si hay problemas:

1. Ve a **"Manage app"** en Streamlit Cloud
2. Revisa los **logs** en la pestaña **"Logs"**
3. Verifica que los secrets estén configurados correctamente

---

## 🔧 Paso 4: Configuración Avanzada (Opcional)

### Actualizar la app:

- Los cambios en GitHub se despliegan automáticamente
- Puedes forzar un redeploy desde "Manage app" → "Reboot app"

### Configurar dominio personalizado:

- Disponible en planes de pago de Streamlit Cloud
- Ve a "Manage app" → "Settings" → "General"

### Optimizaciones:

- Los datos se cachean automáticamente por 1 hora
- La app se "duerme" después de inactividad (gratuito)
- Se "despierta" automáticamente al acceder

---

## 🛠️ Solución de Problemas

### Error de autenticación Jira:
```
Verifica que tu token API esté correcto y tenga permisos
```
**Solución**: Regenera el token API en Jira y actualiza secrets

### App no carga:
```
ModuleNotFoundError: No module named 'xxx'
```
**Solución**: Verifica que todas las dependencias estén en `requirements.txt`

### Datos no se cargan:
```
Error 400/401 de Jira API
```
**Solución**: Verifica URL, email y token en secrets

### Rendimiento lento:
```
La app tarda mucho en cargar
```
**Solución**: Reduce el número de issues cargadas o mejora queries JQL

---

## 📱 URLs Importantes

- **Tu App**: `https://[nombre-elegido].streamlit.app`
- **Gestión**: [share.streamlit.io](https://share.streamlit.io) → Manage app
- **Logs**: Desde "Manage app" → Logs
- **Código**: [GitHub VibeCoding](https://github.com/jesusprodriguezUnir/VibeCoding)

---

## 🎯 Ejemplo de Configuración Completa

### Secrets en Streamlit Cloud:
```toml
[jira]
base_url = "https://miempresa.atlassian.net"
email = "juan.perez@miempresa.com"
token = "ATATT3xFfGF0T4JVjdmjXGWxNzNIFedCdOQIxjT4E_EJEMPLO"
```

### URL final:
```
https://vibecoding-dashboard.streamlit.app
```

---

## 🎉 ¡Listo!

Tu aplicación VibeCoding ya está desplegada y lista para usar. Comparte la URL con tu equipo para que puedan visualizar las asignaciones de Jira en tiempo real.

### Próximos pasos:
- Personaliza las consultas JQL en `core/config.py`
- Agrega nuevos widgets en `features/dashboards/`
- Configura alertas para issues críticos
- Implementa reportes automáticos

**¿Problemas?** Revisa los logs en Streamlit Cloud o contacta soporte.