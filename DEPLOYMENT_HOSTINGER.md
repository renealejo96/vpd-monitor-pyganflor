# 🚀 Deployment en Hostinger VPS - Con Mejoras 2026

## 📋 ¿Qué hay de nuevo?

Tu aplicación ahora incluye:
- ✅ **Filtros de fecha ilimitados** - Ver cualquier período histórico
- ✅ **Exportación completa** - Excel con estadísticas automáticas
- ✅ **Interfaz mejorada** - Diseño profesional y atractivo
- ✅ **Multi-finca** - Soporte para 3 fincas simultáneas
- ✅ **Auto-guardado** - Cada 15 minutos automático

---

## 🎯 Opciones de Deployment en Hostinger

### Opción 1: Docker (Recomendado) 🐳
✅ Más fácil de mantener
✅ Consistente en cualquier servidor
✅ Aislado del sistema
✅ Actualizaciones simples

### Opción 2: Instalación Directa 📦
✅ Menor uso de recursos
✅ Control total
❌ Más manual

---

## 🐳 OPCIÓN 1: Deployment con Docker

### Paso 1: Conectar a tu VPS Hostinger

```bash
ssh root@tu-servidor-hostinger.com
# O con el usuario que te proporciona Hostinger
```

### Paso 2: Instalar Docker (si no lo tienes)

```bash
# Actualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install docker-compose -y

# Verificar instalación
docker --version
docker-compose --version
```

### Paso 3: Subir tu proyecto al servidor

**Opción A - Con Git (Recomendado):**

```bash
# En tu VPS
cd /home
git clone https://github.com/tu-usuario/tu-repositorio.git vpd-app
cd vpd-app
```

**Opción B - Con SFTP/SCP:**

```bash
# Desde tu PC local (PowerShell)
scp -r D:\FINAL_VPD root@tu-servidor:/home/vpd-app
```

### Paso 4: Configurar Variables de Entorno

```bash
cd /home/vpd-app

# Crear archivo .env
nano .env
```

**Copia este contenido (actualiza con tus valores):**

```env
# FINCA 1 - PYGANFLOR
FINCA1_API_KEY=tu_api_key_aqui
FINCA1_API_SECRET=tu_api_secret_aqui
FINCA1_STATION_ID=167591

# FINCA 2 - URCUQUÍ
FINCA2_API_KEY=tu_api_key_aqui
FINCA2_API_SECRET=tu_api_secret_aqui
FINCA2_STATION_ID=209314

# FINCA 3 - MALCHINGUÍ
FINCA3_API_KEY=tu_api_key_aqui
FINCA3_API_SECRET=tu_api_secret_aqui
FINCA3_STATION_ID=219603

# SUPABASE (Base de datos en la nube)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_supabase_anon_key_aqui
```

Guardar: `Ctrl+X` → `Y` → `Enter`

### Paso 5: Actualizar Supabase (Base de Datos)

**Importante:** Asegúrate de que tu tabla Supabase tenga la columna `finca`

1. Ve a https://supabase.com
2. Abre tu proyecto
3. Ve a **SQL Editor**
4. Ejecuta:

```sql
-- Agregar columna finca para las nuevas mejoras
ALTER TABLE vpd_historico ADD COLUMN IF NOT EXISTS finca TEXT NOT NULL DEFAULT 'PYGANFLOR';

-- Índices para mejor rendimiento (especialmente con los nuevos filtros de fecha)
CREATE INDEX IF NOT EXISTS idx_vpd_finca ON vpd_historico(finca);
CREATE INDEX IF NOT EXISTS idx_vpd_finca_fecha ON vpd_historico(finca, fecha DESC);
CREATE INDEX IF NOT EXISTS idx_vpd_timestamp ON vpd_historico(timestamp DESC);

-- Actualizar registros antiguos
UPDATE vpd_historico SET finca = 'PYGANFLOR' WHERE finca IS NULL OR finca = '';
```

### Paso 6: Construir y Lanzar con Docker

```bash
# Construir la imagen Docker
docker-compose build

# Lanzar en segundo plano
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f
```

### Paso 7: Configurar Acceso Público

**Opción A - Puerto directo (8501):**

```bash
# Abrir puerto en firewall
ufw allow 8501/tcp

# Acceder desde navegador
http://tu-ip-vps:8501
```

**Opción B - Con Nginx Reverse Proxy (Recomendado):**

```bash
# Instalar Nginx
apt install nginx -y

# Crear configuración
nano /etc/nginx/sites-available/vpd-app
```

**Contenido del archivo:**

```nginx
server {
    listen 80;
    server_name tu-dominio.com;  # O tu IP

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

```bash
# Activar configuración
ln -s /etc/nginx/sites-available/vpd-app /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Ahora accede desde:
http://tu-dominio.com
# o
http://tu-ip-vps
```

**Opción C - Con SSL (HTTPS):**

```bash
# Instalar Certbot
apt install certbot python3-certbot-nginx -y

# Obtener certificado SSL
certbot --nginx -d tu-dominio.com

# Ahora tendrás acceso seguro:
https://tu-dominio.com
```

---

## 📦 OPCIÓN 2: Instalación Directa (Sin Docker)

### Paso 1: Conectar al VPS

```bash
ssh root@tu-servidor-hostinger.com
```

### Paso 2: Instalar Python y Dependencias

```bash
# Actualizar sistema
apt update && apt upgrade -y

# Instalar Python 3.11
apt install python3.11 python3.11-venv python3-pip -y

# Verificar versión
python3.11 --version
```

### Paso 3: Preparar Proyecto

```bash
# Crear directorio
mkdir -p /home/vpd-app
cd /home/vpd-app

# Opción A: Clonar desde Git
git clone https://github.com/tu-usuario/tu-repo.git .

# Opción B: Subir archivos con SCP (desde tu PC)
# scp -r D:\FINAL_VPD/* root@tu-servidor:/home/vpd-app/
```

### Paso 4: Crear Entorno Virtual

```bash
cd /home/vpd-app

# Crear entorno virtual
python3.11 -m venv venv

# Activar entorno
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 5: Configurar .env

```bash
nano .env
```

(Copia el mismo contenido del .env de la Opción 1)

### Paso 6: Crear Servicio Systemd

```bash
nano /etc/systemd/system/vpd-app.service
```

**Contenido:**

```ini
[Unit]
Description=VPD Monitor Streamlit App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/vpd-app
Environment="PATH=/home/vpd-app/venv/bin"
ExecStart=/home/vpd-app/venv/bin/streamlit run app_vpd.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Paso 7: Iniciar Servicio

```bash
# Recargar systemd
systemctl daemon-reload

# Habilitar inicio automático
systemctl enable vpd-app

# Iniciar servicio
systemctl start vpd-app

# Verificar estado
systemctl status vpd-app

# Ver logs en tiempo real
journalctl -u vpd-app -f
```

### Paso 8: Configurar Nginx (Igual que Opción 1)

(Seguir los pasos de Nginx de la Opción 1)

---

## ✅ Verificación Post-Deployment

### 1. Verificar que la App Carga

```bash
# Probar localmente desde el VPS
curl http://localhost:8501

# Ver logs
docker-compose logs -f  # Si usas Docker
# O
journalctl -u vpd-app -f  # Si es instalación directa
```

### 2. Acceder desde el Navegador

```
http://tu-ip-vps:8501
# O si configuraste Nginx:
http://tu-dominio.com
```

### 3. Verificar Nuevas Funcionalidades

✅ **Filtros de Fecha:**
- Ve a "📈 Gráfica Histórica"
- Abre "🔍 Filtros y Opciones"
- Prueba seleccionar "Últimos 30 días"
- Prueba fechas personalizadas

✅ **Exportación:**
- Ve a "📋 Tabla de Datos"
- Selecciona "Todo el historial"
- Click "📊 Descargar Excel"
- Verifica que descarga

✅ **Guardado Automático:**
```bash
# Ver logs del scheduler (cada 15 min)
docker-compose logs -f | grep "Guardado automático"
# O
journalctl -u vpd-app -f | grep "Guardado automático"
```

### 4. Verificar Supabase

1. Ve a https://supabase.com
2. Abre **Table Editor** → `vpd_historico`
3. Deberías ver:
   - Columna `finca` con valores
   - Nuevos registros cada 15 minutos

---

## 🔄 Actualizaciones Futuras

### Con Docker:

```bash
cd /home/vpd-app

# Hacer backup del .env
cp .env .env.backup

# Actualizar código
git pull origin main

# Reconstruir y reiniciar
docker-compose down
docker-compose build
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### Sin Docker:

```bash
# Detener servicio
systemctl stop vpd-app

# Actualizar código
cd /home/vpd-app
git pull origin main

# Actualizar dependencias
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Reiniciar
systemctl start vpd-app
journalctl -u vpd-app -f
```

---

## 🚨 Troubleshooting

### Error: Puerto 8501 ya en uso

```bash
# Encontrar proceso usando el puerto
lsof -i :8501

# Matar proceso
kill -9 <PID>

# O reiniciar Docker
docker-compose restart
```

### Error: No se conecta a Supabase

```bash
# Verificar variables de entorno
cat .env | grep SUPABASE

# Probar conexión desde el VPS
curl https://tu-proyecto.supabase.co
```

### Error: Exportación Excel no funciona

```bash
# Verificar que openpyxl está instalado
pip list | grep openpyxl

# Si no está:
pip install openpyxl
```

### Los Filtros de Fecha No Muestran Datos

1. Verifica que hay datos en Supabase para ese rango
2. Revisa logs de errores:
```bash
docker-compose logs | grep -i error
# O
journalctl -u vpd-app | grep -i error
```

### Memoria Insuficiente

Si tu VPS tiene poca RAM (< 1GB):

```bash
# Crear swap file
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Hacer permanente
echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
```

---

## 🔐 Seguridad Adicional

### 1. Firewall Básico

```bash
# Instalar UFW
apt install ufw -y

# Configurar reglas
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# Activar
ufw enable
ufw status
```

### 2. Fail2Ban (Protección contra ataques)

```bash
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban
```

### 3. Actualizar .env con Permisos Seguros

```bash
chmod 600 /home/vpd-app/.env
```

---

## 📊 Monitoreo

### Ver Uso de Recursos

```bash
# Uso de Docker
docker stats

# Uso general del sistema
htop
```

### Verificar Logs Regularmente

```bash
# Últimas 100 líneas
docker-compose logs --tail=100

# O con systemd
journalctl -u vpd-app --since "1 hour ago"
```

---

## 🎉 ¡Listo para Producción!

Tu aplicación VPD ahora está en producción con:

✅ **Filtros ilimitados** - Consulta cualquier período histórico
✅ **Exportación completa** - Descarga todos tus datos en Excel
✅ **Estadísticas automáticas** - Reportes profesionales
✅ **Interfaz mejorada** - Diseño moderno y atractivo
✅ **Multi-finca** - 3 fincas simultáneas
✅ **Auto-guardado** - Cada 15 minutos
✅ **Acceso 24/7** - Disponible desde cualquier lugar
✅ **SSL (opcional)** - Conexión segura HTTPS

---

## 📞 Soporte

**Documentación adicional:**
- `MEJORAS_REALIZADAS.md` - Detalle de mejoras
- `GUIA_VISUAL.md` - Tutorial de uso
- `README_MEJORAS.md` - Guía rápida

**Comandos útiles:**

```bash
# Reiniciar app
docker-compose restart
# O
systemctl restart vpd-app

# Ver estado
docker-compose ps
# O
systemctl status vpd-app

# Backup de datos
docker-compose exec vpd_app tar czf /tmp/backup.tar.gz /app/vpd_historico.json
```

---

**¡Tu monitor VPD mejorado está listo para producción! 🚀**
