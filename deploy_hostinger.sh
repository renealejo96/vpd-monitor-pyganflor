#!/bin/bash

# 🚀 Script de Deployment Rápido para Hostinger VPS
# Ejecutar en tu servidor Hostinger

set -e  # Detener si hay algún error

echo "============================================"
echo "  🚀 Deployment VPD Monitor - Hostinger"
echo "============================================"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Verificar que estamos en el directorio correcto
print_info "Verificando directorio..."
if [ ! -f "app_vpd.py" ]; then
    print_error "No se encuentra app_vpd.py. Asegúrate de estar en el directorio correcto."
    exit 1
fi
print_success "Directorio correcto"

# 2. Verificar que existe .env
print_info "Verificando archivo .env..."
if [ ! -f ".env" ]; then
    print_error "No se encuentra archivo .env"
    print_info "Creando .env de ejemplo..."
    cat > .env << 'EOF'
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

# SUPABASE
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_supabase_anon_key_aqui
EOF
    print_warning "Archivo .env creado. ¡EDÍTALO con tus credenciales antes de continuar!"
    echo ""
    echo "Ejecuta: nano .env"
    echo "Luego vuelve a ejecutar este script"
    exit 1
fi
print_success "Archivo .env encontrado"

# 3. Preguntar método de deployment
echo ""
print_info "¿Qué método de deployment deseas usar?"
echo "1) Docker (Recomendado - Más fácil)"
echo "2) Instalación Directa (Systemd)"
echo ""
read -p "Selecciona (1 o 2): " deploy_method

if [ "$deploy_method" = "1" ]; then
    echo ""
    print_info "🐳 Deployment con Docker seleccionado"
    echo ""
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        print_warning "Docker no está instalado"
        read -p "¿Deseas instalar Docker ahora? (s/n): " install_docker
        
        if [ "$install_docker" = "s" ]; then
            print_info "Instalando Docker..."
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
            rm get-docker.sh
            print_success "Docker instalado"
        else
            print_error "Docker es necesario para este método"
            exit 1
        fi
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_info "Instalando Docker Compose..."
        apt-get update
        apt-get install -y docker-compose
        print_success "Docker Compose instalado"
    fi
    
    # Detener contenedor si existe
    print_info "Deteniendo contenedor anterior si existe..."
    docker-compose down 2>/dev/null || true
    
    # Construir imagen
    print_info "Construyendo imagen Docker..."
    docker-compose build
    print_success "Imagen construida"
    
    # Lanzar contenedor
    print_info "Lanzando contenedor..."
    docker-compose up -d
    print_success "Contenedor lanzado"
    
    # Esperar un momento
    sleep 5
    
    # Verificar estado
    print_info "Verificando estado del contenedor..."
    if docker-compose ps | grep -q "Up"; then
        print_success "¡Contenedor corriendo correctamente!"
    else
        print_error "Hubo un problema al iniciar el contenedor"
        print_info "Mostrando logs..."
        docker-compose logs --tail=50
        exit 1
    fi
    
    echo ""
    print_success "🎉 ¡Deployment exitoso con Docker!"
    echo ""
    print_info "Comandos útiles:"
    echo "  - Ver logs:      docker-compose logs -f"
    echo "  - Reiniciar:     docker-compose restart"
    echo "  - Detener:       docker-compose down"
    echo "  - Ver estado:    docker-compose ps"
    echo ""
    
elif [ "$deploy_method" = "2" ]; then
    echo ""
    print_info "📦 Instalación Directa seleccionada"
    echo ""
    
    # Verificar Python
    if ! command -v python3.11 &> /dev/null; then
        print_warning "Python 3.11 no encontrado"
        read -p "¿Deseas instalar Python 3.11? (s/n): " install_python
        
        if [ "$install_python" = "s" ]; then
            print_info "Instalando Python 3.11..."
            apt-get update
            apt-get install -y python3.11 python3.11-venv python3-pip
            print_success "Python 3.11 instalado"
        else
            print_error "Python 3.11 es necesario"
            exit 1
        fi
    fi
    
    # Crear entorno virtual
    print_info "Creando entorno virtual..."
    python3.11 -m venv venv
    print_success "Entorno virtual creado"
    
    # Activar e instalar dependencias
    print_info "Instalando dependencias..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Dependencias instaladas"
    
    # Crear servicio systemd
    print_info "Creando servicio systemd..."
    CURRENT_DIR=$(pwd)
    
    cat > /etc/systemd/system/vpd-app.service << EOF
[Unit]
Description=VPD Monitor Streamlit App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/streamlit run app_vpd.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    print_success "Servicio creado"
    
    # Recargar systemd
    systemctl daemon-reload
    
    # Habilitar e iniciar servicio
    print_info "Habilitando servicio..."
    systemctl enable vpd-app
    
    print_info "Iniciando servicio..."
    systemctl start vpd-app
    
    # Esperar un momento
    sleep 5
    
    # Verificar estado
    if systemctl is-active --quiet vpd-app; then
        print_success "¡Servicio corriendo correctamente!"
    else
        print_error "Hubo un problema al iniciar el servicio"
        print_info "Mostrando logs..."
        journalctl -u vpd-app -n 50 --no-pager
        exit 1
    fi
    
    echo ""
    print_success "🎉 ¡Deployment exitoso con Systemd!"
    echo ""
    print_info "Comandos útiles:"
    echo "  - Ver logs:      journalctl -u vpd-app -f"
    echo "  - Reiniciar:     systemctl restart vpd-app"
    echo "  - Detener:       systemctl stop vpd-app"
    echo "  - Ver estado:    systemctl status vpd-app"
    echo ""
    
else
    print_error "Opción inválida"
    exit 1
fi

# Verificar puerto
print_info "Verificando que el puerto 8501 esté abierto..."
if netstat -tuln | grep -q ":8501"; then
    print_success "Puerto 8501 está escuchando"
else
    print_warning "El puerto 8501 no parece estar escuchando"
fi

# Obtener IP del servidor
SERVER_IP=$(curl -s ifconfig.me)

echo ""
print_success "============================================"
print_success "  ✅ DEPLOYMENT COMPLETADO"
print_success "============================================"
echo ""
print_info "Accede a tu aplicación en:"
echo ""
echo "  🌐 http://$SERVER_IP:8501"
echo ""
print_warning "Nota: Si configuraste Nginx, usa tu dominio en su lugar"
echo ""
print_info "Próximos pasos opcionales:"
echo "  1. Configurar Nginx como reverse proxy"
echo "  2. Configurar SSL con Certbot (HTTPS)"
echo "  3. Configurar firewall (UFW)"
echo ""
print_info "Consulta DEPLOYMENT_HOSTINGER.md para más detalles"
echo ""
