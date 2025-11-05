#!/bin/bash
echo "🚀 DESPLEGANDO VPD MONITOR - PYGANFLOR"
echo "====================================="

echo ""
echo "📦 Verificando dependencias..."
pip install -r requirements.txt

echo ""
echo "🧪 Probando aplicación localmente..."
echo "Iniciando servidor Streamlit..."
echo ""
echo "🌐 La aplicación estará disponible en: http://localhost:8501"
echo "📱 Para acceso desde móvil usar: http://[tu-ip]:8501"
echo ""
echo "⏹️  Para detener: Ctrl+C"
echo ""

streamlit run app_vpd.py --server.port 8501 --server.address 0.0.0.0