#!/bin/bash

# 🔄 Script de Actualización Automática para VPD Monitor
# Ejecutar en tu servidor Ubuntu Hostinger
# Uso: bash actualizar_app.sh

set -e

echo ""
echo "============================================"
echo "  🔄 Actualización VPD Monitor 2026"
echo "============================================"
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Detectar ubicación de la app
if [ -f "app_vpd.py" ]; then
    print_success "Ubicación detectada: $(pwd)"
else
    print_error "No se encuentra app_vpd.py en este directorio"
    echo ""
    echo "Ubicaciones comunes:"
    echo "  - /home/vpd-app"
    echo "  - /var/www/vpd-app"
    echo "  - /root/vpd-app"
    echo ""
    read -p "Ingresa la ruta completa de tu app: " APP_PATH
    cd "$APP_PATH" || exit 1
fi

echo ""
print_info "Mejoras que se instalarán:"
echo "  ✨ Filtros de fecha ilimitados"
echo "  ✨ Exportación Excel con estadísticas"
echo "  ✨ Interfaz mejorada y profesional"
echo "  ✨ Mejor rendimiento en consultas"
echo ""

read -p "¿Continuar con la actualización? (s/n): " CONTINUAR
if [ "$CONTINUAR" != "s" ]; then
    print_warning "Actualización cancelada"
    exit 0
fi

echo ""
print_info "Iniciando actualización..."
echo ""

# 1. Backup del .env
print_info "1/7 Creando backup de .env..."
if [ -f ".env" ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    print_success "Backup creado"
else
    print_warning "No se encontró .env (continuando...)"
fi

# 2. Detener aplicación
print_info "2/7 Deteniendo aplicación..."
if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
    docker-compose down
    DEPLOY_METHOD="docker"
    print_success "Contenedor Docker detenido"
elif systemctl is-active --quiet vpd-app; then
    sudo systemctl stop vpd-app
    DEPLOY_METHOD="systemd"
    print_success "Servicio systemd detenido"
else
    print_warning "No se detectó método de deployment, asumiendo manual"
    DEPLOY_METHOD="manual"
fi

# 3. Actualizar código
print_info "3/7 Descargando código actualizado desde GitHub..."
git pull origin main
print_success "Código actualizado"

# 4. Actualizar dependencias
print_info "4/7 Actualizando dependencias..."
if [ "$DEPLOY_METHOD" = "docker" ]; then
    docker-compose build
    print_success "Imagen Docker reconstruida"
elif [ "$DEPLOY_METHOD" = "systemd" ] && [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt --upgrade -q
    deactivate
    print_success "Dependencias Python actualizadas"
else
    print_warning "Saltando actualización de dependencias"
fi

# 5. Recordatorio de Supabase
echo ""
print_warning "5/7 ⚠️  IMPORTANTE - Actualización de Supabase"
echo ""
echo "Debes ejecutar este SQL en Supabase (https://supabase.com):"
echo ""
echo "─────────────────────────────────────────────────────────"
cat << 'EOF'
-- Agregar columna finca
ALTER TABLE vpd_historico 
ADD COLUMN IF NOT EXISTS finca TEXT NOT NULL DEFAULT 'PYGANFLOR';

-- Índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_vpd_finca 
ON vpd_historico(finca);

CREATE INDEX IF NOT EXISTS idx_vpd_finca_fecha 
ON vpd_historico(finca, fecha DESC);

CREATE INDEX IF NOT EXISTS idx_vpd_timestamp 
ON vpd_historico(timestamp DESC);

-- Actualizar registros antiguos
UPDATE vpd_historico 
SET finca = 'PYGANFLOR' 
WHERE finca IS NULL OR finca = '';
EOF
echo "─────────────────────────────────────────────────────────"
echo ""
read -p "¿Ya ejecutaste este SQL en Supabase? (s/n): " SQL_DONE
if [ "$SQL_DONE" != "s" ]; then
    print_error "¡No olvides ejecutar el SQL antes de usar la app!"
    print_info "Ve a: https://supabase.com → Tu proyecto → SQL Editor"
fi

# 6. Reiniciar aplicación
print_info "6/7 Reiniciando aplicación..."
if [ "$DEPLOY_METHOD" = "docker" ]; then
    docker-compose up -d
    sleep 5
    if docker-compose ps | grep -q "Up"; then
        print_success "Contenedor Docker iniciado"
    else
        print_error "Error al iniciar contenedor. Ver logs: docker-compose logs"
        exit 1
    fi
elif [ "$DEPLOY_METHOD" = "systemd" ]; then
    sudo systemctl start vpd-app
    sleep 5
    if systemctl is-active --quiet vpd-app; then
        print_success "Servicio systemd iniciado"
    else
        print_error "Error al iniciar servicio. Ver logs: journalctl -u vpd-app -n 50"
        exit 1
    fi
fi

# 7. Verificación final
print_info "7/7 Verificando instalación..."

# Verificar puerto
if netstat -tuln 2>/dev/null | grep -q ":8501" || ss -tuln 2>/dev/null | grep -q ":8501"; then
    print_success "Puerto 8501 está escuchando"
else
    print_warning "El puerto 8501 no parece estar activo"
fi

# Obtener IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "tu-servidor")

echo ""
echo "============================================"
print_success "  ✅ ACTUALIZACIÓN COMPLETADA"
echo "============================================"
echo ""
print_info "Accede a tu aplicación:"
echo ""
echo "  🌐 http://$SERVER_IP:8501"
echo "  🌐 http://tu-dominio.com (si configuraste)"
echo ""
print_info "Verifica las nuevas funcionalidades:"
echo "  1. Filtros de fecha en 'Gráfica Histórica'"
echo "  2. Exportación completa en 'Tabla de Datos'"
echo "  3. Descarga Excel con 2 hojas (Datos + Estadísticas)"
echo ""
print_info "Ver logs:"
if [ "$DEPLOY_METHOD" = "docker" ]; then
    echo "  docker-compose logs -f"
elif [ "$DEPLOY_METHOD" = "systemd" ]; then
    echo "  journalctl -u vpd-app -f"
fi
echo ""
print_success "¡Disfruta de tu app mejorada! 🎉"
echo ""
