# 🚀 Guía de Deployment en VPS de Hostinger

## 📋 Cambios Implementados

### ✅ Nuevas Funcionalidades:
1. **Sistema Multi-Finca**: Soporte para 3 fincas (Pyganflor, Urcuquí, Malchinguí)
2. **APScheduler**: Guardado automático cada 15 minutos sin necesidad de navegador abierto
3. **Resumen Comparativo**: Tabla con datos de todas las fincas
4. **Gráficos Comparativos**: Visualización de múltiples fincas en un solo gráfico
5. **Selector de Finca**: Cambio dinámico entre fincas
6. **UI Optimizada**: Eliminación de mensajes innecesarios

### 📦 Archivos Modificados:
- `app_vpd.py` - Aplicación principal con multi-finca y scheduler
- `requirements.txt` - Agregado APScheduler==3.10.4
- `.env.example` - Actualizado para 3 fincas
- `supabase_schema.sql` - Esquema actualizado con columna `finca`

## 🔧 Pasos para Actualizar el VPS

### 1️⃣ Conectarse al VPS
```bash
ssh usuario@tu-vps-hostinger.com
```

### 2️⃣ Navegar a la carpeta del proyecto
```bash
cd /ruta/donde/esta/el/proyecto
# Ejemplo: cd /home/usuario/vpd-monitor-pyganflor
```

### 3️⃣ Detener la aplicación actual
```bash
# Si está corriendo con systemd:
sudo systemctl stop vpd-app

# O si está corriendo en screen/tmux:
screen -r vpd  # y presionar Ctrl+C
```

### 4️⃣ Hacer backup de .env actual (IMPORTANTE)
```bash
cp .env .env.backup
```

### 5️⃣ Actualizar el código desde GitHub
```bash
git pull origin main
```

### 6️⃣ Actualizar .env con las nuevas variables
Edita el archivo `.env` y asegúrate de tener estas variables:

```bash
nano .env
```

**Contenido requerido:**
```env
# FINCA 1 - PYGANFLOR
FINCA1_API_KEY=ljhgrfizwlad3hose74hycpa0jn1t4rz
FINCA1_API_SECRET=t9yutftlg7eddypqv9kocdpmtu9mwyhy
FINCA1_STATION_ID=167591

# FINCA 2 - URCUQUÍ
FINCA2_API_KEY=hrd0nyzmwv5esftiktab7nsgazmi6zp8
FINCA2_API_SECRET=m5jyv0unsyzktbxdt1xnm9dqw4q4pwktI
FINCA2_STATION_ID=209314

# FINCA 3 - MALCHINGUÍ
FINCA3_API_KEY=mczqougmw56ggwopbodwsvy20oyn38sh
FINCA3_API_SECRET=frvgyvxki0vel9vbkeydnnvbhixyt5ji
FINCA3_STATION_ID=219603

# SUPABASE
SUPABASE_URL=tu_supabase_url_aqui
SUPABASE_KEY=tu_supabase_key_aqui
```

**Guardar y salir**: `Ctrl+X`, luego `Y`, luego `Enter`

### 7️⃣ Actualizar esquema de Supabase

**IMPORTANTE**: La tabla necesita una nueva columna `finca`

Opción A - Si tienes acceso a Supabase Dashboard:
1. Ve a https://supabase.com
2. Abre tu proyecto
3. Ve a SQL Editor
4. Ejecuta este comando:

```sql
-- Agregar columna finca si no existe
ALTER TABLE vpd_historico ADD COLUMN IF NOT EXISTS finca TEXT NOT NULL DEFAULT 'PYGANFLOR';

-- Crear índice para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_vpd_finca ON vpd_historico(finca);
CREATE INDEX IF NOT EXISTS idx_vpd_finca_timestamp ON vpd_historico(finca, timestamp DESC);

-- Actualizar registros antiguos sin finca
UPDATE vpd_historico SET finca = 'PYGANFLOR' WHERE finca IS NULL OR finca = '';
```

Opción B - Recrear la tabla desde cero (si prefieres empezar limpio):
```sql
-- Ver el archivo supabase_schema.sql en el repositorio
-- Copiar y ejecutar su contenido completo
```

### 8️⃣ Actualizar dependencias de Python
```bash
# Activar entorno virtual si usas uno
source venv/bin/activate  # o el nombre de tu venv

# Instalar nuevas dependencias
pip install -r requirements.txt
```

### 9️⃣ Reiniciar la aplicación

**Opción A - Con systemd (recomendado para producción):**
```bash
sudo systemctl start vpd-app
sudo systemctl status vpd-app
```

**Opción B - Con screen (para pruebas):**
```bash
screen -S vpd
streamlit run app_vpd.py --server.port=8501 --server.address=0.0.0.0
# Presionar Ctrl+A luego D para detach
```

**Opción C - Con nohup:**
```bash
nohup streamlit run app_vpd.py --server.port=8501 --server.address=0.0.0.0 &
```

### 🔟 Verificar que el scheduler está funcionando

Revisa los logs para ver los mensajes de guardado automático:

```bash
# Si usas systemd:
sudo journalctl -u vpd-app -f

# Si usas screen:
screen -r vpd

# Si usas nohup:
tail -f nohup.out
```

**Deberías ver cada 15 minutos:**
```
============================================================
🔄 Guardado automático iniciado: 2025-12-23 15:30:00
============================================================

📍 Procesando finca: Pyganflor...
   ✅ Datos guardados: T=16.5°C, HR=92%, VPD=0.13 kPa

📍 Procesando finca: Florsani Urcuquí...
   ✅ Datos guardados: T=15.8°C, HR=94%, VPD=0.10 kPa

📍 Procesando finca: Malchinguí...
   ✅ Datos guardados: T=17.2°C, HR=89%, VPD=0.19 kPa

============================================================
✅ Guardado automático completado
============================================================
```

## ✅ Verificación Final

1. **Verificar que la app carga**: Abre `http://tu-vps-ip:8501` en el navegador
2. **Verificar selector de fincas**: Deberías ver 3 opciones (Pyganflor, Florsani Urcuquí, Malchinguí)
3. **Verificar datos en tiempo real**: Presiona "Cargar Dashboard" y verifica que se muestran los datos
4. **Verificar resumen de fincas**: Expande "Ver Resumen Fincas" en la parte superior
5. **Verificar gráficos comparativos**: En tab "Gráfica Histórica" activa "Comparar todas las fincas"
6. **Verificar guardado automático**: Espera 15 minutos y revisa que se guardan datos en Supabase

## 🚨 Troubleshooting

### Error: ModuleNotFoundError: No module named 'apscheduler'
```bash
pip install APScheduler==3.10.4
```

### Error: column "finca" does not exist
```bash
# Ejecutar en Supabase SQL Editor:
ALTER TABLE vpd_historico ADD COLUMN finca TEXT NOT NULL DEFAULT 'PYGANFLOR';
```

### Error: No se muestran las 3 fincas
- Verificar que el archivo `.env` tenga las 3 configuraciones completas
- Verificar que los `STATION_ID` sean diferentes de 0

### El scheduler no guarda datos
- Verificar que la aplicación esté corriendo continuamente (no se haya cerrado)
- Revisar los logs para ver mensajes de error
- Verificar conectividad a Supabase desde el VPS

## 📞 Soporte

Si encuentras algún problema:
1. Revisa los logs de la aplicación
2. Verifica que todas las variables de entorno estén configuradas
3. Verifica que Supabase esté accesible desde el VPS
4. Contacta al equipo de desarrollo con el error específico

## 🎉 Listo!

Tu aplicación ahora:
- ✅ Soporta 3 fincas simultáneas
- ✅ Guarda datos automáticamente cada 15 minutos
- ✅ No requiere navegador abierto para guardar datos
- ✅ Permite comparar datos entre fincas
- ✅ Tiene una interfaz optimizada y limpia
