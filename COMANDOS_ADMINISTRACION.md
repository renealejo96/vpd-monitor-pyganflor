# 📝 Comandos Útiles para Administrar VPD Monitor en Hostinger

## 🐳 Con Docker

### Comandos Básicos

```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Ver últimas 100 líneas de logs
docker-compose logs --tail=100

# Reiniciar aplicación
docker-compose restart

# Detener aplicación
docker-compose down

# Iniciar aplicación
docker-compose up -d

# Reconstruir y reiniciar (después de cambios)
docker-compose down
docker-compose build
docker-compose up -d
```

### Monitoreo

```bash
# Ver uso de recursos del contenedor
docker stats vpd_app

# Entrar al contenedor (shell interactivo)
docker-compose exec vpd_app bash

# Ver procesos dentro del contenedor
docker-compose exec vpd_app ps aux
```

### Limpieza

```bash
# Limpiar imágenes antiguas
docker system prune -a

# Limpiar solo contenedores detenidos
docker container prune

# Ver espacio usado por Docker
docker system df
```

---

## 📦 Con Systemd (Instalación Directa)

### Comandos Básicos

```bash
# Ver estado del servicio
systemctl status vpd-app

# Iniciar servicio
systemctl start vpd-app

# Detener servicio
systemctl stop vpd-app

# Reiniciar servicio
systemctl restart vpd-app

# Habilitar inicio automático
systemctl enable vpd-app

# Deshabilitar inicio automático
systemctl disable vpd-app
```

### Logs

```bash
# Ver logs en tiempo real
journalctl -u vpd-app -f

# Ver últimas 100 líneas
journalctl -u vpd-app -n 100

# Ver logs de la última hora
journalctl -u vpd-app --since "1 hour ago"

# Ver logs de hoy
journalctl -u vpd-app --since today

# Buscar errores
journalctl -u vpd-app | grep -i error
```

---

## 🌐 Nginx (Reverse Proxy)

### Comandos Básicos

```bash
# Verificar configuración
nginx -t

# Recargar configuración (sin downtime)
systemctl reload nginx

# Reiniciar Nginx
systemctl restart nginx

# Ver estado
systemctl status nginx

# Ver logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Editar Configuración

```bash
# Editar configuración de la app
nano /etc/nginx/sites-available/vpd-app

# Aplicar cambios
nginx -t && systemctl reload nginx
```

---

## 🔐 SSL con Certbot

### Obtener Certificado

```bash
# Primera vez
certbot --nginx -d tu-dominio.com

# Renovar manualmente
certbot renew

# Ver certificados
certbot certificates

# Renovación automática (ya configurada)
systemctl status certbot.timer
```

---

## 🔥 Firewall (UFW)

### Comandos Básicos

```bash
# Ver estado
ufw status

# Ver reglas numeradas
ufw status numbered

# Habilitar firewall
ufw enable

# Deshabilitar firewall
ufw disable

# Permitir puerto
ufw allow 8501/tcp

# Denegar puerto
ufw deny 8501/tcp

# Eliminar regla
ufw delete [número]
```

---

## 📊 Monitoreo del Sistema

### Recursos

```bash
# Ver uso de CPU/RAM en tiempo real
htop

# Uso de disco
df -h

# Espacio usado por directorio
du -sh /home/vpd-app

# Ver procesos de Python
ps aux | grep python
```

### Red

```bash
# Ver puertos abiertos
netstat -tuln | grep LISTEN

# O con ss
ss -tuln | grep LISTEN

# Ver conexiones activas
netstat -an | grep 8501

# Probar conectividad
curl http://localhost:8501
```

---

## 🗄️ Base de Datos (Supabase)

### Verificar Conexión

```bash
# Desde el servidor
curl https://tu-proyecto.supabase.co

# Probar API
curl -X GET 'https://tu-proyecto.supabase.co/rest/v1/vpd_historico?select=*&limit=1' \
  -H "apikey: TU_SUPABASE_KEY" \
  -H "Authorization: Bearer TU_SUPABASE_KEY"
```

---

## 📁 Archivos y Backups

### Backups

```bash
# Backup del código
tar czf vpd-app-backup-$(date +%Y%m%d).tar.gz /home/vpd-app

# Backup solo del .env
cp /home/vpd-app/.env ~/env-backup-$(date +%Y%m%d).env

# Restaurar backup
tar xzf vpd-app-backup-20260108.tar.gz -C /
```

### Permisos

```bash
# Ver permisos de .env
ls -la /home/vpd-app/.env

# Asegurar permisos correctos
chmod 600 /home/vpd-app/.env

# Cambiar propietario
chown root:root /home/vpd-app/.env
```

---

## 🔄 Actualizaciones

### Actualizar desde Git

```bash
cd /home/vpd-app

# Ver estado actual
git status

# Ver cambios remotos
git fetch
git log HEAD..origin/main --oneline

# Actualizar
git pull origin main
```

### Actualizar Dependencias Python

```bash
cd /home/vpd-app

# Con Docker
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Con venv
source venv/bin/activate
pip install -r requirements.txt --upgrade
deactivate
systemctl restart vpd-app
```

### Actualizar Sistema

```bash
# Actualizar paquetes del sistema
apt update
apt upgrade -y

# Actualizar Docker
apt update
apt install docker.io docker-compose

# Reiniciar servidor (cuando sea necesario)
reboot
```

---

## 🚨 Solución de Problemas

### App No Responde

```bash
# Verificar si está corriendo
docker-compose ps
# O
systemctl status vpd-app

# Ver logs de errores
docker-compose logs --tail=50 | grep -i error
# O
journalctl -u vpd-app -n 50 | grep -i error

# Reiniciar
docker-compose restart
# O
systemctl restart vpd-app
```

### Puerto Bloqueado

```bash
# Ver qué está usando el puerto 8501
lsof -i :8501

# Matar proceso
kill -9 <PID>

# Verificar firewall
ufw status | grep 8501
```

### Memoria Llena

```bash
# Ver uso de memoria
free -h

# Ver procesos que más usan memoria
ps aux --sort=-%mem | head -10

# Limpiar caché
sync; echo 3 > /proc/sys/vm/drop_caches

# Reiniciar app
docker-compose restart
# O
systemctl restart vpd-app
```

### Disco Lleno

```bash
# Ver uso de disco
df -h

# Encontrar archivos grandes
find / -type f -size +100M 2>/dev/null

# Limpiar logs viejos de Docker
docker system prune -a --volumes

# Limpiar logs del sistema
journalctl --vacuum-time=7d
```

---

## 📈 Verificar Nuevas Funcionalidades

### Probar Filtros de Fecha

```bash
# Ver logs cuando alguien usa los filtros
docker-compose logs -f | grep -i "fecha"
# O
journalctl -u vpd-app -f | grep -i "fecha"
```

### Verificar Exportaciones

```bash
# Ver si se generan exportaciones
# (Buscar actividad en logs)
docker-compose logs | grep -i "excel\|csv"
```

### Verificar Auto-guardado (cada 15 min)

```bash
# Ver mensajes del scheduler
docker-compose logs -f | grep "Guardado automático"
# O
journalctl -u vpd-app -f | grep "Guardado automático"

# Deberías ver algo como:
# ============================================================
# 🔄 Guardado automático iniciado: 2026-01-08 15:30:00
# ...
# ✅ Guardado automático completado
# ============================================================
```

---

## 📞 Información Rápida

### IPs y Puertos

```bash
# IP pública del servidor
curl ifconfig.me

# IP privada
hostname -I

# Puertos en uso
netstat -tuln | grep LISTEN
```

### Versiones

```bash
# Versión de Docker
docker --version

# Versión de Python
python3.11 --version

# Versión de Streamlit
pip show streamlit | grep Version
```

---

## 🎯 Comandos de Un Solo Uso

### Reinicio Completo (Reset Total)

```bash
# CON DOCKER
cd /home/vpd-app
docker-compose down
docker system prune -a
docker-compose build
docker-compose up -d

# CON SYSTEMD
systemctl stop vpd-app
cd /home/vpd-app
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
systemctl start vpd-app
```

### Verificación Completa del Sistema

```bash
#!/bin/bash
echo "=== VERIFICACIÓN COMPLETA ==="
echo ""
echo "1. App Status:"
docker-compose ps || systemctl status vpd-app
echo ""
echo "2. Puerto 8501:"
netstat -tuln | grep 8501
echo ""
echo "3. Firewall:"
ufw status | grep 8501
echo ""
echo "4. Memoria:"
free -h
echo ""
echo "5. Disco:"
df -h /
echo ""
echo "6. Últimos logs:"
docker-compose logs --tail=10 || journalctl -u vpd-app -n 10
```

Guarda este script como `verificar_sistema.sh` y ejecútalo cuando necesites.

---

## 💡 Tips de Productividad

### Crear Aliases

Agrega a `~/.bashrc`:

```bash
# Aliases para VPD Monitor
alias vpd-logs='docker-compose -f /home/vpd-app/docker-compose.yml logs -f'
alias vpd-restart='docker-compose -f /home/vpd-app/docker-compose.yml restart'
alias vpd-status='docker-compose -f /home/vpd-app/docker-compose.yml ps'

# O para Systemd
alias vpd-logs='journalctl -u vpd-app -f'
alias vpd-restart='systemctl restart vpd-app'
alias vpd-status='systemctl status vpd-app'
```

Luego ejecuta: `source ~/.bashrc`

Ahora puedes usar simplemente:
```bash
vpd-logs
vpd-restart
vpd-status
```

---

**¡Guarda este archivo como referencia rápida!** 📌
