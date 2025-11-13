# 🚀 Configuración Supabase (RECOMENDADO - MÁS FÁCIL)

## ✅ Ventajas de Supabase vs Google Sheets:
- 🆓 **100% Gratis** (500MB de base de datos)
- ⚡ **Más rápido** que Google Sheets
- 🔒 **Más seguro**
- 📊 **Sin límites de almacenamiento en Drive**
- 🎯 **Configuración más simple**

---

## 📝 PASOS PARA CONFIGURAR SUPABASE:

### 1️⃣ Crear cuenta en Supabase (2 minutos)

1. Ve a: https://supabase.com
2. Click "Start your project"
3. Inicia sesión con GitHub (recomendado) o email
4. Es **GRATIS** - no necesitas tarjeta de crédito

### 2️⃣ Crear nuevo proyecto (1 minuto)

1. Click "New project"
2. **Organization:** Selecciona o crea una
3. **Name:** `vpd-pyganflor`
4. **Database Password:** Crea una contraseña segura (guárdala)
5. **Region:** `South America (São Paulo)` (más cercano a Colombia)
6. Click "Create new project"
7. ⏳ Espera 1-2 minutos mientras se crea

### 3️⃣ Crear tabla para datos VPD (2 minutos)

1. En el panel lateral, click "**SQL Editor**"
2. Copia y pega este código SQL:

```sql
CREATE TABLE vpd_historico (
  id BIGSERIAL PRIMARY KEY,
  timestamp TEXT NOT NULL,
  fecha TEXT NOT NULL,
  hora TEXT NOT NULL,
  dia_semana TEXT NOT NULL,
  temperatura NUMERIC NOT NULL,
  humedad INTEGER NOT NULL,
  vpd NUMERIC NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para búsquedas rápidas por timestamp
CREATE INDEX idx_vpd_timestamp ON vpd_historico(timestamp DESC);

-- Política de seguridad (permitir todo desde service_role)
ALTER TABLE vpd_historico ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all for service_role" 
ON vpd_historico 
FOR ALL 
USING (true);
```

3. Click "**Run**" (▶️)
4. Deberías ver: "Success. No rows returned"

### 4️⃣ Obtener credenciales (1 minuto)

1. En el panel lateral, click "**Project Settings**" (⚙️)
2. Click "**API**"
3. Encontrarás dos valores importantes:

**Project URL:**
```
https://tu-proyecto.supabase.co
```

**anon public key:**
```
eyJhbG... (un texto largo)
```

### 5️⃣ Configurar en Streamlit Cloud (1 minuto)

1. Ve a tu app en https://share.streamlit.io
2. Settings → Secrets
3. **AGREGA ESTAS LÍNEAS AL PRINCIPIO** (antes de las otras):

```toml
# Supabase (Base de datos)
supabase_url = "https://TU-PROYECTO.supabase.co"
supabase_key = "TU-ANON-PUBLIC-KEY-AQUI"

# API de WeatherLink (ya las tienes)
[api]
API_KEY = "ljhgrfizwlad3hose74hycpa0jn1t4rz"
API_SECRET = "t9yutftlg7eddypqv9kocdpmtu9mwyhy"
STATION_ID = "167591"
```

4. Click "Save"
5. ¡Listo! La app se reiniciará automáticamente

---

## ✅ RESULTADO:

- ✅ Datos guardados automáticamente cada 15 minutos
- ✅ Persistencia permanente (no se pierden al reiniciar)
- ✅ Acceso rápido a histórico de 7 días
- ✅ Sin problemas de cuota de Drive
- ✅ Funciona en PC y móvil

---

## 🔍 Ver tus datos

Puedes ver los datos guardados en:
- Supabase → Table Editor → vpd_historico

---

## 💡 TIPS:

- **Límites gratuitos:** 500MB de datos (suficiente para años de registros cada 15 min)
- **Backups:** Supabase hace backups automáticos
- **Exportar:** Puedes exportar los datos a CSV desde el Table Editor
