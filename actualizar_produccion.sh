#!/bin/bash

# 🔄 Script de Actualización para VPD Monitor
# Ejecutar cuando quieras actualizar la app en producción

set -e

echo "============================================"
echo "  🔄 Actualización VPD Monitor"
echo "============================================"
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Hacer backup del .env
print_info "Creando backup de .env..."
if [ -f ".env" ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    print_success "Backup creado"
else
    print_warning "No se encontró .env"
fi

# Actualizar código desde Git
print_info "Actualizando código desde Git..."
if [ -d ".git" ]; then
    git pull origin main
    print_success "Código actualizado"
else
    print_warning "No es un repositorio Git, saltando actualización de código"
fi

# Detectar método de deployment
if [ -f "docker-compose.yml" ] && command -v docker-compose &> /dev/null; then
    print_info "Detectado deployment con Docker"
    
    # Detener contenedor
    print_info "Deteniendo contenedor..."
    docker-compose down
    
    # Reconstruir imagen
    print_info "Reconstruyendo imagen..."
    docker-compose build
    
    # Reiniciar
    print_info "Reiniciando contenedor..."
    docker-compose up -d
    
    # Esperar
    sleep 5
    
    # Verificar
    if docker-compose ps | grep -q "Up"; then
        print_success "¡Actualización exitosa!"
    else
        print_warning "Revisa los logs con: docker-compose logs -f"
    fi
    
elif systemctl is-active --quiet vpd-app; then
    print_info "Detectado deployment con Systemd"
    
    # Detener servicio
    print_info "Deteniendo servicio..."
    systemctl stop vpd-app
    
    # Actualizar dependencias
    print_info "Actualizando dependencias..."
    if [ -d "venv" ]; then
        source venv/bin/activate
        pip install -r requirements.txt --upgrade
        deactivate
    fi
    
    # Reiniciar servicio
    print_info "Reiniciando servicio..."
    systemctl start vpd-app
    
    # Esperar
    sleep 5
    
    # Verificar
    if systemctl is-active --quiet vpd-app; then
        print_success "¡Actualización exitosa!"
    else
        print_warning "Revisa los logs con: journalctl -u vpd-app -f"
    fi
else
    print_warning "No se detectó método de deployment conocido"
    print_info "Actualiza manualmente según tu configuración"
fi

echo ""
print_success "🎉 Actualización completada"
echo ""
print_info "Mejoras incluidas:"
echo "  ✅ Filtros de fecha ilimitados"
echo "  ✅ Exportación completa en Excel"
echo "  ✅ Estadísticas automáticas"
echo "  ✅ Interfaz mejorada"
echo ""
