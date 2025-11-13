# 📊 Configuración Google Sheets para Producción

## 🔑 Paso 1: Crear Service Account en Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita las APIs:
   - Google Sheets API
   - Google Drive API
4. Ve a "Credenciales" → "Crear credenciales" → "Cuenta de servicio"
5. Completa el formulario y crea la cuenta
6. Click en la cuenta creada → "Keys" → "Add Key" → "Create new key" → JSON
7. Descarga el archivo JSON

## 🔧 Paso 2: Configurar Secrets en Streamlit Cloud

1. Ve a tu app en [share.streamlit.io](https://share.streamlit.io)
2. Click "Settings" → "Secrets"
3. Agrega el contenido del archivo JSON descargado:

```toml
[gcp_service_account]
type = "service_account"
project_id = "tu-project-id"
private_key_id = "tu-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\ntu-private-key\n-----END PRIVATE KEY-----\n"
client_email = "tu-service-account@tu-project.iam.gserviceaccount.com"
client_id = "tu-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "tu-cert-url"
```

4. Mantén también las credenciales de la API:

```toml
[api]
API_KEY = "ljhgrfizwlad3hose74hycpa0jn1t4rz"
API_SECRET = "t9yutftlg7eddypqv9kocdpmtu9mwyhy"
STATION_ID = "167591"
```

## 📝 Paso 3: La app creará automáticamente la hoja

- La primera vez que se ejecute en producción, creará automáticamente la hoja "VPD_PYGANFLOR_HISTORICO"
- Los datos se guardarán automáticamente cada 15 minutos
- Se mantienen los últimos 7 días de registros

## 🧪 Desarrollo Local

En desarrollo local (sin configurar Google Sheets):
- Los datos se guardan en `vpd_historico.json`
- Funciona exactamente igual pero con archivo local
- No se pierden datos al reiniciar

## ✅ Ventajas

- ✅ Almacenamiento persistente en producción
- ✅ Gratis (dentro de límites de Google Sheets)
- ✅ Accesible desde cualquier lugar
- ✅ Puedes ver/editar datos directamente en Google Sheets
- ✅ Respaldo automático de Google
