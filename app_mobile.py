import streamlit as st
import requests
import math
from datetime import datetime, timezone, timedelta

# 📱 VERSIÓN MÓVIL ULTRA-SIMPLE - VPD PYGANFLOR
st.set_page_config(
    page_title="VPD PYGANFLOR", 
    page_icon="🌱",
    layout="centered"
)

# 🎨 CSS MÍNIMO PARA MÓVIL
st.markdown("""
<style>
    .stApp {
        background-color: white !important;
        color: black !important;
    }
    
    .metric-card {
        background-color: #f0f8f0;
        border: 3px solid #28a745;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        text-align: center;
    }
    
    .metric-title {
        color: #000;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .metric-value {
        color: #000;
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .status-ok { background-color: #d4edda; border-color: #28a745; }
    .status-warning { background-color: #fff3cd; border-color: #ffc107; }
    .status-danger { background-color: #f8d7da; border-color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# 🔐 Credenciales
API_KEY = "ljhgrfizwlad3hose74hycpa0jn1t4rz"
API_SECRET = "t9yutftlg7eddypqv9kocdpmtu9mwyhy"
STATION_ID = 167591

# 📊 Funciones básicas
def obtener_datos_estacion():
    try:
        url = f"https://api.weatherlink.com/v2/current/{STATION_ID}"
        headers = {"X-Api-Secret": API_SECRET}
        params = {"api-key": API_KEY}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for sensor in data.get('sensors', []):
                if sensor.get('sensor_type') == 53:
                    sensor_data = sensor.get('data', [{}])[0]
                    temp_f = sensor_data.get('temp')
                    humidity = sensor_data.get('hum')
                    
                    if temp_f is not None and humidity is not None:
                        temp_c = (temp_f - 32) * 5/9
                        return round(temp_c, 1), humidity
        
        return None, None
    except:
        return None, None

def calcular_vpd(temp, hr):
    try:
        svp = 0.6108 * math.exp((17.27 * temp) / (temp + 237.3))
        avp = (hr / 100) * svp
        vpd = svp - avp
        return round(vpd, 2)
    except:
        return 0

def clasificar_vpd(vpd):
    if 0.4 <= vpd <= 1.2:
        return "IDEAL", "status-ok"
    elif vpd < 0.4:
        return "BAJO", "status-warning"
    else:
        return "ALTO", "status-danger"

# 🌿 INTERFAZ PRINCIPAL
st.markdown("""
<div style="background-color: #28a745; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px;">
    <h1 style="margin: 0; color: white;">🌿 VPD PYGANFLOR</h1>
    <p style="margin: 10px 0 0 0; color: white;">Monitor de agricultura</p>
</div>
""", unsafe_allow_html=True)

# Test de visibilidad
st.success("✅ APLICACIÓN CARGADA CORRECTAMENTE")
st.info("📱 Versión optimizada para móviles")

# Botón principal
if st.button("🔍 OBTENER DATOS VPD", type="primary", use_container_width=True):
    # Hora de Colombia (UTC-5)
    colombia_tz = timezone(timedelta(hours=-5))
    hora_actual = datetime.now(colombia_tz).strftime("%d/%m/%Y %H:%M:%S")
    
    with st.spinner("🔄 Conectando con estación..."):
        temp, hr = obtener_datos_estacion()
    
    if temp is not None and hr is not None:
        vpd = calcular_vpd(temp, hr)
        estado, clase_css = clasificar_vpd(vpd)
        
        st.success("✅ Datos obtenidos correctamente")
        st.info(f"🕐 {hora_actual}")
        
        # Mostrar datos principales
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🌡️ TEMPERATURA</div>
            <div class="metric-value">{temp}°C</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">💧 HUMEDAD</div>
            <div class="metric-value">{hr}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card {clase_css}">
            <div class="metric-title">📈 VPD</div>
            <div class="metric-value">{vpd} kPa</div>
            <div style="color: #000; font-weight: bold; margin-top: 10px;">{estado}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Información adicional
        if estado == "IDEAL":
            st.balloons()
            st.success("🎯 Condiciones perfectas para el cultivo")
        elif estado == "BAJO":
            st.warning("⚠️ VPD bajo - Considerar reducir humedad")
        else:
            st.error("🚨 VPD alto - Aumentar humedad o reducir temperatura")
            
        # Tabla resumen
        st.markdown("### 📋 Resumen")
        st.markdown(f"""
        | Parámetro | Valor | Estado |
        |-----------|-------|--------|
        | Temperatura | {temp}°C | Normal |
        | Humedad | {hr}% | Normal |
        | VPD | {vpd} kPa | {estado} |
        """)
        
    else:
        st.error("❌ Error al obtener datos de la estación")
        st.info("🔄 Intenta nuevamente en unos segundos")

# Información adicional
st.markdown("---")
st.markdown("""
### 📖 Información VPD
- **Zona Ideal:** 0.4 - 1.2 kPa
- **VPD Bajo:** < 0.4 kPa (demasiada humedad)
- **VPD Alto:** > 1.2 kPa (muy seco)

### 🌱 PYGANFLOR
Monitoreo en tiempo real para agricultura de precisión
""")