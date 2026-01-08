# 🚀 INSTRUCCIONES FINALES - Actualizar en Servidor Ubuntu

## ✅ Parte 1: COMPLETADA
El código ya está en GitHub con todas las mejoras.

---

## 🔄 Parte 2: Actualizar tu Servidor Ubuntu en Hostinger

### Opción A: Script Automático (RECOMENDADO) ⚡

Conéctate a tu servidor y ejecuta:

```bash
# 1. Conectar al servidor
ssh root@tu-servidor-hostinger.com

# 2. Ir a tu directorio de la app
cd /home/vpd-app
# O la ruta donde tengas tu app: cd /var/www/vpd-app

# 3. Descargar el script de actualización
curl -O https://raw.githubusercontent.com/renealejo96/vpd-monitor-pyganflor/main/actualizar_app.sh

# 4. Dar permisos de ejecución
chmod +x actualizar_app.sh

# 5. Ejecutar actualización
./actualizar_app.sh
```

El script hará:
- ✅ Backup automático de tu .env
- ✅ Detener la app
- ✅ Actualizar código desde GitHub
- ✅ Reconstruir/actualizar dependencias
- ✅ Reiniciar la app
- ✅ Verificar que todo funcione

**IMPORTANTE:** El script te recordará ejecutar SQL en Supabase (ver abajo).

---

### Opción B: Manual (paso a paso) 🔧

Si prefieres hacerlo manual:

```bash
# 1. Conectar
ssh root@tu-servidor-hostinger.com

# 2. Ir al directorio de la app
cd /ruta/de/tu/app

# 3. Backup del .env
cp .env .env.backup

# 4. Detener app
# Si usas Docker:
docker-compose down

# Si usas systemd:
sudo systemctl stop vpd-app

# Si usas screen:
# (Presiona Ctrl+C en la sesión)

# 5. Actualizar código
git pull origin main

# 6. Reconstruir/Actualizar
# Si usas Docker:
docker-compose build
docker-compose up -d

# Si usas systemd + venv:
source venv/bin/activate
pip install -r requirements.txt --upgrade
deactivate
sudo systemctl start vpd-app

# 7. Ver logs
docker-compose logs -f
# o
sudo journalctl -u vpd-app -f
```

---

## 📊 Actualizar Base de Datos Supabase (OBLIGATORIO)

**Antes de usar la app actualizada**, ejecuta este SQL en Supabase:

1. Ve a https://supabase.com
2. Abre tu proyecto
3. Ve a **SQL Editor**
4. Copia y ejecuta esto:

```sql
-- Agregar columna finca (para las nuevas funcionalidades)
ALTER TABLE vpd_historico 
ADD COLUMN IF NOT EXISTS finca TEXT NOT NULL DEFAULT 'PYGANFLOR';

-- Índices para mejor rendimiento con filtros de fecha
CREATE INDEX IF NOT EXISTS idx_vpd_finca 
ON vpd_historico(finca);

CREATE INDEX IF NOT EXISTS idx_vpd_finca_fecha 
ON vpd_historico(finca, fecha DESC);

CREATE INDEX IF NOT EXISTS idx_vpd_timestamp 
ON vpd_historico(timestamp DESC);

-- Actualizar registros antiguos sin finca
UPDATE vpd_historico 
SET finca = 'PYGANFLOR' 
WHERE finca IS NULL OR finca = '';
```

5. Click **RUN** o presiona `Ctrl+Enter`
6. Deberías ver: "Success. No rows returned"

---

## ✅ Verificación Final

### 1. Verificar que la app está corriendo:

```bash
# Ver logs
docker-compose logs -f
# o
sudo journalctl -u vpd-app -f

# Deberías ver mensajes de inicio sin errores
```

### 2. Abrir en el navegador:

```
http://tu-dominio.com
```

### 3. Probar las nuevas funcionalidades:

**a) Filtros de Fecha:**
- Ve a "📈 Gráfica Histórica"
- Haz click en "🔍 Filtros y Opciones de Visualización"
- Selecciona "Últimos 30 días"
- La gráfica debe actualizarse con datos de 30 días

**b) Exportación Completa:**
- Ve a "📋 Tabla de Datos"
- Abre "🔍 Filtros de Búsqueda"
- Selecciona "Todo el historial"
- Click "📊 Descargar Excel"
- Abre el archivo descargado
- Debe tener 2 hojas:
  - **Hoja 1:** VPD Histórico (todos los datos)
  - **Hoja 2:** Estadísticas (promedios, min, max)

**c) Interfaz Mejorada:**
- Observa el nuevo diseño con colores profesionales
- Tarjetas con sombras
- Métricas destacadas

**d) Auto-guardado:**
```bash
# Espera 15 minutos y verifica logs:
docker-compose logs | grep "Guardado automático"

# Deberías ver:
# ============================================================
# 🔄 Guardado automático iniciado: 2026-01-08 15:30:00
# ✅ Datos guardados: T=18.5°C, HR=75%, VPD=0.53 kPa
# ============================================================
```

---

## 🎉 ¡Todo Listo!

Tu aplicación ahora tiene:

✅ **Filtros de fecha ilimitados** - Consulta cualquier período histórico
✅ **Exportación completa** - Todo tu historial en Excel con estadísticas
✅ **Interfaz profesional** - Diseño moderno y atractivo
✅ **Mejor rendimiento** - Índices optimizados en la base de datos
✅ **Multi-finca** - Soporte para 3 fincas
✅ **Auto-guardado** - Cada 15 minutos automático

---

## 🚨 Si Tienes Problemas

### Error: "column finca does not exist"
➜ Ejecuta el SQL en Supabase (ver arriba)

### App no inicia:
```bash
# Ver errores específicos
docker-compose logs | grep -i error
# o
sudo journalctl -u vpd-app | grep -i error
```

### Los filtros no muestran datos:
- Verifica que ejecutaste el SQL en Supabase
- Verifica que hay datos en la tabla para ese período
- Revisa los logs de la app

### Exportación no funciona:
```bash
# Verificar que openpyxl está instalado
docker-compose exec vpd_app pip list | grep openpyxl
# o
source venv/bin/activate && pip list | grep openpyxl
```

---

## 📞 Comandos Útiles

```bash
# Ver estado
docker-compose ps
# o
sudo systemctl status vpd-app

# Ver logs en tiempo real
docker-compose logs -f
# o
sudo journalctl -u vpd-app -f

# Reiniciar app
docker-compose restart
# o
sudo systemctl restart vpd-app

# Ver uso de recursos
docker stats
# o
htop
```

---

## 📚 Documentación Adicional

En GitHub ahora tienes estos archivos de ayuda:

- **ACTUALIZACION_RAPIDA.md** - Esta guía
- **MEJORAS_REALIZADAS.md** - Detalle completo de mejoras
- **GUIA_VISUAL.md** - Tutorial visual de uso
- **COMANDOS_ADMINISTRACION.md** - Referencia de comandos
- **DEPLOYMENT_HOSTINGER.md** - Guía completa de deployment

---

**¡Todo está listo para actualizar! 🚀**

**Siguiente paso:** Conectarte a tu servidor y ejecutar el script de actualización.
