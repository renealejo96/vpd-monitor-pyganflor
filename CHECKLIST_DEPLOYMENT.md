# ✅ Checklist de Deployment - Hostinger VPS

## 📋 Pre-Deployment

### En tu PC Local:

- [ ] Código actualizado y funcionando localmente
- [ ] Archivo `.env` configurado con credenciales reales
- [ ] Dependencias en `requirements.txt` actualizadas
- [ ] Supabase funcionando y tabla `vpd_historico` actualizada
- [ ] Commit y push a GitHub (si usas Git)

### Verificar Supabase:

- [ ] Proyecto creado en https://supabase.com
- [ ] Tabla `vpd_historico` existe
- [ ] Columna `finca` agregada (para multi-finca)
- [ ] Índices creados para mejor rendimiento
- [ ] URL y API Key copiadas

---

## 🖥️ En el Servidor Hostinger

### 1. Acceso Inicial

- [ ] Conectado al VPS vía SSH
```bash
ssh root@tu-servidor-hostinger.com
```

- [ ] Usuario root o con privilegios sudo

### 2. Sistema Actualizado

- [ ] Sistema operativo actualizado
```bash
apt update && apt upgrade -y
```

- [ ] Reiniciado si fue necesario
```bash
reboot  # Si instaló kernel nuevo
```

### 3. Instalación de Dependencias

#### Opción Docker:
- [ ] Docker instalado
- [ ] Docker Compose instalado
- [ ] Docker funcionando

```bash
docker --version
docker-compose --version
```

#### Opción Directa:
- [ ] Python 3.11 instalado
- [ ] pip instalado
- [ ] venv creado

```bash
python3.11 --version
```

### 4. Código en el Servidor

- [ ] Directorio `/home/vpd-app` creado
- [ ] Código subido (Git o SCP)
- [ ] Archivo `.env` creado y configurado
- [ ] Permisos correctos en `.env` (600)

```bash
ls -la /home/vpd-app/.env
chmod 600 /home/vpd-app/.env
```

### 5. Base de Datos Supabase

- [ ] Ejecutado script SQL para columna `finca`
```sql
ALTER TABLE vpd_historico ADD COLUMN IF NOT EXISTS finca TEXT NOT NULL DEFAULT 'PYGANFLOR';
CREATE INDEX IF NOT EXISTS idx_vpd_finca_fecha ON vpd_historico(finca, fecha DESC);
```

- [ ] Verificado que la tabla tiene datos o está lista

---

## 🚀 Deployment

### Con Docker:

- [ ] Archivo `docker-compose.yml` presente
- [ ] `Dockerfile` presente
- [ ] Imagen construida: `docker-compose build`
- [ ] Contenedor lanzado: `docker-compose up -d`
- [ ] Contenedor corriendo: `docker-compose ps`
- [ ] Sin errores en logs: `docker-compose logs`

### Con Systemd:

- [ ] Entorno virtual creado
- [ ] Dependencias instaladas: `pip install -r requirements.txt`
- [ ] Servicio systemd creado en `/etc/systemd/system/vpd-app.service`
- [ ] Servicio habilitado: `systemctl enable vpd-app`
- [ ] Servicio iniciado: `systemctl start vpd-app`
- [ ] Servicio corriendo: `systemctl status vpd-app`
- [ ] Sin errores en logs: `journalctl -u vpd-app -f`

---

## 🌐 Acceso Web

### Puerto Directo (8501):

- [ ] Puerto 8501 abierto en firewall
```bash
ufw allow 8501/tcp
ufw status
```

- [ ] App accesible en: `http://IP_VPS:8501`

### Con Nginx (Recomendado):

- [ ] Nginx instalado
- [ ] Configuración creada en `/etc/nginx/sites-available/vpd-app`
- [ ] Symlink creado en `/etc/nginx/sites-enabled/`
- [ ] Configuración verificada: `nginx -t`
- [ ] Nginx reiniciado: `systemctl restart nginx`
- [ ] App accesible en: `http://tu-dominio.com`

### Con SSL/HTTPS (Opcional):

- [ ] Certbot instalado
- [ ] Certificado SSL obtenido: `certbot --nginx -d tu-dominio.com`
- [ ] App accesible en: `https://tu-dominio.com`
- [ ] Auto-renovación configurada

---

## ✅ Verificaciones Post-Deployment

### 1. App Funcional

- [ ] Página carga correctamente
- [ ] No hay errores en consola del navegador (F12)
- [ ] Selector de fincas muestra 3 opciones
- [ ] Dashboard carga datos en tiempo real

### 2. Nuevas Funcionalidades

#### Filtros de Fecha:
- [ ] Tab "Gráfica Histórica" tiene filtros
- [ ] Opciones rápidas funcionan (24h, 7d, 30d)
- [ ] Fechas personalizadas funcionan
- [ ] Gráfica se actualiza con el filtro

#### Exportación:
- [ ] Tab "Tabla de Datos" tiene botones de descarga
- [ ] Botón CSV funciona
- [ ] Botón Excel funciona
- [ ] Archivo Excel tiene 2 hojas (Datos + Estadísticas)

#### Interfaz:
- [ ] Diseño mejorado se ve correctamente
- [ ] Colores y sombras aplicadas
- [ ] Métricas visibles
- [ ] Responsive (funciona en móvil)

### 3. Auto-Guardado

- [ ] Scheduler iniciado (ver logs)
- [ ] Cada 15 minutos se guarda automáticamente
- [ ] Mensajes de guardado en logs:

```bash
# Deberías ver cada 15 min:
============================================================
🔄 Guardado automático iniciado: 2026-01-08 15:30:00
============================================================
📍 Procesando finca: Pyganflor...
   ✅ Datos guardados: T=18.5°C, HR=75%, VPD=0.53 kPa
...
```

- [ ] Datos aparecen en Supabase

### 4. Multi-Finca

- [ ] Selector muestra las 3 fincas
- [ ] Cada finca muestra sus datos correctos
- [ ] Comparación de fincas funciona
- [ ] Datos se guardan con campo `finca` correcto

---

## 🔐 Seguridad

- [ ] Firewall configurado (UFW)
- [ ] Solo puertos necesarios abiertos (22, 80, 443, 8501)
- [ ] Archivo `.env` con permisos 600
- [ ] Fail2Ban instalado (opcional)
- [ ] Claves SSH configuradas (opcional)

---

## 📊 Monitoreo

- [ ] Logs accesibles y claros
- [ ] Comando de verificación funciona
- [ ] Aliases creados (opcional)
- [ ] Notificaciones configuradas (opcional)

---

## 📁 Backups

- [ ] Backup inicial del `.env` creado
- [ ] Plan de backups automáticos considerado
- [ ] Ubicación de backups definida

---

## 📞 Documentación

- [ ] `DEPLOYMENT_HOSTINGER.md` revisado
- [ ] `COMANDOS_ADMINISTRACION.md` guardado
- [ ] Credenciales guardadas en lugar seguro
- [ ] IP del servidor anotada
- [ ] URLs de acceso documentadas

---

## 🎯 Prueba Final Completa

### 1. Acceso y Navegación
```
✅ Abrir: http://tu-dominio.com
✅ Cargar dashboard
✅ Cambiar entre fincas
```

### 2. Visualización
```
✅ Tab "VPD Actual" funciona
✅ Tab "Gráfica Histórica" funciona
✅ Tab "Tabla de Datos" funciona
```

### 3. Filtros de Fecha
```
✅ Seleccionar "Últimos 30 días"
✅ Ver gráfica actualizada
✅ Seleccionar fechas personalizadas
✅ Ver datos filtrados
```

### 4. Exportación
```
✅ Click "Descargar CSV"
✅ Archivo descarga correctamente
✅ Click "Descargar Excel"
✅ Excel tiene 2 hojas
✅ Hoja "Estadísticas" contiene cálculos
```

### 5. Auto-guardado
```
✅ Esperar 15 minutos
✅ Ver logs: nuevo guardado automático
✅ Verificar en Supabase: nuevo registro
```

### 6. Reinicio
```
✅ Reiniciar servidor: reboot
✅ App inicia automáticamente
✅ Todo funciona después de reinicio
```

---

## ✅ DEPLOYMENT COMPLETADO

Si todos los ítems están marcados ✅, tu deployment fue exitoso!

### Información de Acceso:

```
🌐 URL: http://___________________
🔐 Usuario SSH: ___________________
📊 Supabase URL: https://___________________
```

### Comandos Rápidos:

```bash
# Ver estado
docker-compose ps  # O: systemctl status vpd-app

# Ver logs
docker-compose logs -f  # O: journalctl -u vpd-app -f

# Reiniciar
docker-compose restart  # O: systemctl restart vpd-app
```

---

## 🚨 Si Algo No Funciona

1. **Revisar logs** para ver errores específicos
2. **Verificar .env** tiene las credenciales correctas
3. **Verificar Supabase** está accesible
4. **Consultar** `DEPLOYMENT_HOSTINGER.md` sección Troubleshooting
5. **Revisar** `COMANDOS_ADMINISTRACION.md` para comandos útiles

---

**¡Felicidades! 🎉 Tu app VPD mejorada está en producción!**
