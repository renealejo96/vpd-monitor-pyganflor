# 🔄 Guía de Actualización Rápida - App Mejorada

## 📋 Tu Situación:
- ✅ App anterior ya funcionando en Hostinger Ubuntu
- ✅ Solo necesitas actualizar con las mejoras nuevas
- ✅ Código ya está en GitHub

---

## 🚀 Paso 1: Subir Código Mejorado a GitHub

### Desde tu PC (PowerShell en D:\FINAL_VPD):

```powershell
# Verificar estado
git status

# Agregar todos los archivos modificados
git add .

# Hacer commit con las mejoras
git commit -m "Mejoras 2026: Filtros de fecha ilimitados, exportación completa, interfaz mejorada"

# Subir a GitHub
git push origin main
```

Si Git te pide credenciales, usa tu token de GitHub.

---

## 🔄 Paso 2: Actualizar Servidor Ubuntu en Hostinger

### Conectar al Servidor:

```bash
ssh root@tu-servidor-hostinger.com
# O el usuario que uses
```

### Actualizar el Código:

```bash
# 1. Ir a tu directorio de la app
cd /ruta/de/tu/app
# Ejemplo común: cd /home/vpd-app o cd /var/www/vpd-app

# 2. Hacer backup del .env actual (IMPORTANTE)
cp .env .env.backup

# 3. Detener la aplicación
# Si usas Docker:
docker-compose down

# Si usas systemd:
sudo systemctl stop vpd-app

# Si usas screen/tmux:
# Presiona Ctrl+C en la sesión

# 4. Actualizar código desde GitHub
git pull origin main

# 5. Actualizar Supabase (IMPORTANTE - nueva columna y índices)
# Ve a https://supabase.com → SQL Editor → Ejecuta:
```

**SQL para ejecutar en Supabase:**
```sql
-- Agregar columna finca si no existe (para las mejoras)
ALTER TABLE vpd_historico ADD COLUMN IF NOT EXISTS finca TEXT NOT NULL DEFAULT 'PYGANFLOR';

-- Índices para mejor rendimiento con filtros de fecha
CREATE INDEX IF NOT EXISTS idx_vpd_finca ON vpd_historico(finca);
CREATE INDEX IF NOT EXISTS idx_vpd_finca_fecha ON vpd_historico(finca, fecha DESC);
CREATE INDEX IF NOT EXISTS idx_vpd_timestamp ON vpd_historico(timestamp DESC);

-- Actualizar registros antiguos sin finca
UPDATE vpd_historico SET finca = 'PYGANFLOR' WHERE finca IS NULL OR finca = '';
```

```bash
# 6. Actualizar dependencias (por si acaso)
# Si usas Docker:
docker-compose build

# Si tienes venv:
source venv/bin/activate
pip install -r requirements.txt --upgrade
deactivate

# 7. Reiniciar la aplicación
# Si usas Docker:
docker-compose up -d

# Si usas systemd:
sudo systemctl start vpd-app

# Si usas screen:
screen -S vpd
streamlit run app_vpd.py --server.port=8501 --server.address=0.0.0.0
# Luego Ctrl+A + D para salir
```

---

## ✅ Paso 3: Verificar que Funciona

### Verificar Logs:

```bash
# Con Docker:
docker-compose logs -f

# Con systemd:
sudo journalctl -u vpd-app -f

# Con screen:
screen -r vpd
```

**Deberías ver:** Mensajes de inicio sin errores.

### Probar en el Navegador:

```
http://tu-dominio.com
```

**Verificar:**
1. ✅ App carga correctamente
2. ✅ Tab "Gráfica Histórica" tiene nuevos filtros de fecha
3. ✅ Tab "Tabla de Datos" tiene filtros y opciones de exportación
4. ✅ Interfaz se ve mejorada (colores, sombras, diseño)
5. ✅ Botones "Descargar Excel" y "Descargar CSV" funcionan

### Probar Nuevas Funcionalidades:

**Filtros de Fecha:**
- Ve a "📈 Gráfica Histórica"
- Despliega "🔍 Filtros y Opciones de Visualización"
- Selecciona "Últimos 30 días"
- La gráfica debe actualizarse

**Exportación:**
- Ve a "📋 Tabla de Datos"
- Selecciona "Todo el historial"
- Click "📊 Descargar Excel"
- Abre el archivo → Debe tener 2 hojas (Datos + Estadísticas)

---

## 🚨 Si Algo No Funciona

### Error: "column finca does not exist"

**Solución:** Ejecuta el SQL en Supabase (Paso 2.5)

### Error: Módulos faltantes

```bash
# Con Docker:
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Con venv:
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
deactivate
sudo systemctl restart vpd-app
```

### Los filtros no muestran datos

**Verifica en Supabase:**
- Tabla tiene datos
- Columna `finca` existe
- Índices fueron creados

### Ver errores específicos:

```bash
# Docker:
docker-compose logs | grep -i error

# Systemd:
sudo journalctl -u vpd-app | grep -i error
```

---

## 📊 Verificar Auto-guardado (Scheduler)

Espera 15 minutos y verifica logs:

```bash
# Deberías ver cada 15 min:
============================================================
🔄 Guardado automático iniciado: 2026-01-08 15:30:00
============================================================
📍 Procesando finca: Pyganflor...
   ✅ Datos guardados: T=18.5°C, HR=75%, VPD=0.53 kPa
============================================================
✅ Guardado automático completado
============================================================
```

---

## 🎯 Comandos de Un Vistazo

```bash
# ACTUALIZAR (desde tu servidor)
cd /ruta/de/tu/app
cp .env .env.backup
docker-compose down  # o: sudo systemctl stop vpd-app
git pull origin main
docker-compose build
docker-compose up -d  # o: sudo systemctl start vpd-app

# VERIFICAR
docker-compose logs -f  # o: sudo journalctl -u vpd-app -f

# REINICIAR SI ES NECESARIO
docker-compose restart  # o: sudo systemctl restart vpd-app
```

---

## 📝 Checklist Rápido

### En tu PC:
- [ ] `git add .`
- [ ] `git commit -m "Mejoras 2026"`
- [ ] `git push origin main`

### En Supabase:
- [ ] Ejecutar SQL para agregar columna `finca`
- [ ] Ejecutar SQL para crear índices

### En Servidor Ubuntu:
- [ ] Conectar SSH
- [ ] Backup de `.env`
- [ ] Detener app
- [ ] `git pull origin main`
- [ ] Reconstruir/actualizar dependencias
- [ ] Reiniciar app
- [ ] Verificar logs (sin errores)

### Verificación Final:
- [ ] App carga en navegador
- [ ] Filtros de fecha funcionan
- [ ] Exportación Excel funciona
- [ ] Excel tiene 2 hojas
- [ ] Auto-guardado funcionando (ver logs cada 15 min)

---

## 🎉 ¡Listo!

Una vez completados todos los pasos, tu app actualizada estará en producción con:

✅ **Filtros de fecha ilimitados** - Consulta cualquier período
✅ **Exportación completa** - Todo el historial en Excel
✅ **Estadísticas automáticas** - Hoja extra en Excel con cálculos
✅ **Interfaz mejorada** - Diseño más profesional y atractivo
✅ **Mejor rendimiento** - Índices en base de datos

---

## 💡 Tip Extra

Si quieres automatizar futuras actualizaciones, crea este script en tu servidor:

```bash
nano ~/actualizar_vpd.sh
```

**Contenido:**
```bash
#!/bin/bash
cd /ruta/de/tu/app
cp .env .env.backup
docker-compose down
git pull origin main
docker-compose build
docker-compose up -d
echo "✅ Actualización completada"
docker-compose logs --tail=20
```

**Uso futuro:**
```bash
chmod +x ~/actualizar_vpd.sh
~/actualizar_vpd.sh
```

---

**¿Necesitas ayuda con algún paso específico?** ¡Pregunta!
