import streamlit as st
import requests
import math
import time
import hashlib
import hmac
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
try:
    from google.oauth2.service_account import Credentials
    import gspread
    GSHEETS_AVAILABLE = True
except:
    GSHEETS_AVAILABLE = False

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except:
    SUPABASE_AVAILABLE = False

# � Configuración específica para móviles (especialmente iOS)
st.set_page_config(
    page_title="VPD Monitor PYGANFLOR", 
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Monitor VPD para agricultura - PYGANFLOR"
    }
)

# 🎨 CSS personalizado para mejor compatibilidad móvil
st.markdown("""
<style>
    /* FORZAR TEMA CLARO COMPLETO */
    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    .main {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    .block-container {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        padding-top: 1rem !important;
    }
    
    /* FORZAR VISIBILIDAD EN MÓVILES */
    .element-container {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    .stMarkdown {
        background-color: transparent !important;
        color: #000000 !important;
    }
    
    .stTitle {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    
    /* MÉTRICAS VISIBLES */
    .metric-container {
        background-color: #F8F9FA !important;
        border: 2px solid #28A745 !important;
        border-radius: 10px !important;
        padding: 15px !important;
        margin: 10px 0 !important;
    }
    
    .stMetric {
        background-color: #F8F9FA !important;
        border: 2px solid #DEE2E6 !important;
        border-radius: 8px !important;
        padding: 10px !important;
        color: #000000 !important;
    }
    
    .stMetric label {
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    .stMetric [data-testid="metric-value"] {
        color: #000000 !important;
        font-size: 24px !important;
        font-weight: bold !important;
    }
    
    /* SIDEBAR VISIBLE */
    .css-1d391kg {
        background-color: #F8F9FA !important;
    }
    
    /* PLOTLY CHART FONDO BLANCO */
    .stPlotlyChart {
        background-color: #FFFFFF !important;
    }
    
    /* OPTIMIZACIÓN ESPECÍFICA PARA MÓVILES */
    @media screen and (max-width: 768px) {
        .main .block-container {
            padding: 1rem !important;
            max-width: 100% !important;
        }
        
        .stTitle h1 {
            font-size: 1.5rem !important;
            color: #000000 !important;
            text-align: center !important;
            background-color: #FFFFFF !important;
            padding: 10px !important;
            border: 2px solid #28A745 !important;
            border-radius: 10px !important;
        }
        
        /* FORZAR VISIBILIDAD TOTAL EN MÓVIL */
        * {
            color: #000000 !important;
        }
        
        .stApp > div {
            background-color: #FFFFFF !important;
        }
    }
    
    /* WEBKIT ESPECÍFICO (SAFARI/CHROME MÓVIL) */
    @supports (-webkit-appearance: none) {
        .stApp {
            -webkit-appearance: none !important;
            background-color: #FFFFFF !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# 🔐 Credenciales de WeatherLink (Producción)
# En producción, usar st.secrets o variables de entorno
try:
    # Intentar obtener de Streamlit secrets (producción)
    API_KEY = st.secrets["api"]["API_KEY"]
    API_SECRET = st.secrets["api"]["API_SECRET"] 
    STATION_ID = int(st.secrets["api"]["STATION_ID"])
except:
    # Fallback para desarrollo local
    API_KEY = os.getenv("API_KEY", "ljhgrfizwlad3hose74hycpa0jn1t4rz")
    API_SECRET = os.getenv("API_SECRET", "t9yutftlg7eddypqv9kocdpmtu9mwyhy")
    STATION_ID = int(os.getenv("STATION_ID", "167591"))

# 📁 Configuración de almacenamiento
HISTORICO_FILE = "vpd_historico.json"
GSHEET_NAME = "VPD_PYGANFLOR_HISTORICO"

# 🔧 Detectar si estamos en producción (Streamlit Cloud)
def esta_en_produccion():
    """Detecta si la app está corriendo en Streamlit Cloud"""
    try:
        # Priorizar Supabase sobre Google Sheets
        if "supabase_url" in st.secrets and "supabase_key" in st.secrets:
            st.sidebar.success("🟢 Supabase detectado")
            return "supabase"
        elif "gcp_service_account" in st.secrets:
            st.sidebar.info("🔵 Google Sheets detectado")
            return "gsheets"
        st.sidebar.warning("🟡 Modo desarrollo (local JSON)")
        return False
    except Exception as e:
        st.sidebar.error(f"🔴 Error detectando entorno: {str(e)}")
        return False

# 📊 Funciones para Supabase (Producción - Recomendado)
def obtener_cliente_supabase():
    """Obtiene cliente de Supabase"""
    try:
        if not SUPABASE_AVAILABLE:
            return None
        
        if "supabase_url" not in st.secrets:
            return None
            
        if "supabase_key" not in st.secrets:
            return None
        
        url = st.secrets["supabase_url"]
        key = st.secrets["supabase_key"]
        
        return create_client(url, key)
    except Exception as e:
        return None

def cargar_historico_supabase():
    """Carga histórico desde Supabase"""
    try:
        client = obtener_cliente_supabase()
        if not client:
            return []
        
        # Obtener últimos 7 días de registros
        response = client.table('vpd_historico').select('*').order('id', desc=True).limit(672).execute()
        
        if not response.data:
            return []
        
        # Convertir tipos numéricos si vienen como strings
        datos = []
        for registro in response.data:
            datos.append({
                'timestamp': str(registro['timestamp']),
                'fecha': str(registro['fecha']),
                'hora': str(registro['hora']),
                'dia_semana': str(registro['dia_semana']),
                'temperatura': float(registro['temperatura']),
                'humedad': float(registro['humedad']),
                'vpd': float(registro['vpd'])
            })
        return datos
    except Exception as e:
        st.error(f"Error al cargar desde Supabase: {str(e)}")
        return []

def guardar_registro_supabase(registro):
    """Guarda un nuevo registro en Supabase"""
    try:
        client = obtener_cliente_supabase()
        if not client:
            st.error("❌ No se pudo conectar a Supabase. Verifica las credenciales.")
            return False
        
        # Insertar registro
        response = client.table('vpd_historico').insert(registro).execute()
        
        # Verificar que se insertó correctamente
        if response.data:
            return True
        else:
            return False
    except Exception as e:
        st.error(f"❌ Error al guardar en Supabase: {str(e)}")
        st.info("💡 Verifica que la tabla 'vpd_historico' exista y tenga las columnas correctas")
        return False

# 📊 Funciones para Google Sheets (Producción)
def obtener_cliente_gsheets():
    """Obtiene cliente autenticado de Google Sheets"""
    try:
        if not GSHEETS_AVAILABLE:
            return None
        
        # Credenciales desde secrets de Streamlit Cloud
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        return gspread.authorize(credentials)
    except:
        return None

def cargar_historico_gsheets():
    """Carga histórico desde Google Sheets"""
    try:
        client = obtener_cliente_gsheets()
        if not client:
            return []
        
        # Abrir o crear hoja
        try:
            sheet = client.open(GSHEET_NAME).sheet1
        except:
            # Crear nueva hoja si no existe
            spreadsheet = client.create(GSHEET_NAME)
            sheet = spreadsheet.sheet1
            # Agregar encabezados
            sheet.append_row(['timestamp', 'fecha', 'hora', 'dia_semana', 'temperatura', 'humedad', 'vpd'])
        
        # Obtener todos los registros
        records = sheet.get_all_records()
        return records
    except Exception as e:
        st.error(f"Error al cargar desde Google Sheets: {e}")
        return []

def guardar_registro_gsheets(registro):
    """Guarda un nuevo registro en Google Sheets"""
    try:
        client = obtener_cliente_gsheets()
        if not client:
            return False
        
        # Abrir hoja
        try:
            sheet = client.open(GSHEET_NAME).sheet1
        except:
            # Crear si no existe
            spreadsheet = client.create(GSHEET_NAME)
            sheet = spreadsheet.sheet1
            sheet.append_row(['timestamp', 'fecha', 'hora', 'dia_semana', 'temperatura', 'humedad', 'vpd'])
        
        # Agregar registro
        sheet.append_row([
            registro['timestamp'],
            registro['fecha'],
            registro['hora'],
            registro['dia_semana'],
            registro['temperatura'],
            registro['humedad'],
            registro['vpd']
        ])
        
        # Limpiar registros viejos (mantener últimos 672 = 7 días)
        all_values = sheet.get_all_values()
        if len(all_values) > 673:  # +1 por encabezado
            registros_a_eliminar = len(all_values) - 673
            sheet.delete_rows(2, registros_a_eliminar + 1)  # Desde fila 2 (después de encabezados)
        
        return True
    except Exception as e:
        st.error(f"Error al guardar en Google Sheets: {e}")
        return False

# 📊 Funciones locales JSON (Desarrollo)
def cargar_historico_json():
    """Carga el histórico de VPD desde el archivo JSON"""
    try:
        if Path(HISTORICO_FILE).exists():
            with open(HISTORICO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except:
        return []

def guardar_historico_json(datos):
    """Guarda el histórico de VPD en el archivo JSON"""
    try:
        with open(HISTORICO_FILE, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

# 🔄 Funciones híbridas (Auto-detectan producción/desarrollo)
def cargar_historico():
    """Carga histórico desde Supabase/Google Sheets (producción) o JSON (local)"""
    env = esta_en_produccion()
    if env == "supabase":
        return cargar_historico_supabase()
    elif env == "gsheets":
        return cargar_historico_gsheets()
    else:
        return cargar_historico_json()

def guardar_historico(datos):
    """Guarda histórico en formato local (JSON)"""
    # Solo se usa para desarrollo local
    if not esta_en_produccion():
        return guardar_historico_json(datos)

def agregar_lectura_historico(temp, hr, vpd):
    """Agrega una nueva lectura al histórico"""
    colombia_tz = timezone(timedelta(hours=-5))
    ahora = datetime.now(colombia_tz)
    
    # Crear nuevo registro
    nuevo_registro = {
        "timestamp": ahora.isoformat(),
        "fecha": ahora.strftime("%d/%m/%Y"),
        "hora": ahora.strftime("%H:%M:%S"),
        "dia_semana": ahora.strftime("%A"),
        "temperatura": temp,
        "humedad": hr,
        "vpd": vpd
    }
    
    # Guardar según el entorno
    env = esta_en_produccion()
    if env == "supabase":
        # Producción: Supabase (recomendado)
        return guardar_registro_supabase(nuevo_registro)
    elif env == "gsheets":
        # Producción: Google Sheets (alternativa)
        return guardar_registro_gsheets(nuevo_registro)
    else:
        # Desarrollo: JSON local
        historico = cargar_historico()
        historico.append(nuevo_registro)
        
        # Mantener solo últimos 7 días
        if len(historico) > 672:
            historico = historico[-672:]
        
        guardar_historico(historico)
        return True

def obtener_ultimo_registro_tiempo():
    """Obtiene el timestamp del último registro para determinar si han pasado 15 minutos"""
    historico = cargar_historico()
    if historico:
        try:
            ultimo = historico[-1]
            return datetime.fromisoformat(ultimo["timestamp"])
        except:
            return None
    return None

def debe_guardar_lectura():
    """Determina si deben haber pasado al menos 15 minutos desde la última lectura"""
    ultimo_tiempo = obtener_ultimo_registro_tiempo()
    if ultimo_tiempo is None:
        return True
    
    colombia_tz = timezone(timedelta(hours=-5))
    ahora = datetime.now(colombia_tz)
    diferencia = ahora - ultimo_tiempo
    
    # Retornar True si han pasado al menos 15 minutos (900 segundos)
    return diferencia.total_seconds() >= 900

# 🔑 Función para validar credenciales
def validar_credenciales():
    st.sidebar.markdown("### 🔑 Validación de Credenciales")
    
    st.sidebar.info("💡 **Verifica en WeatherLink:**\n- Consola de desarrolladores\n- API Keys activas\n- Permisos de lectura")
    
    # Solo el botón para probar autenticación
    if st.sidebar.button("🧪 Probar Solo Autenticación"):
        probar_autenticacion()

# 🔬 Función para explorar la estructura completa de datos
def explorar_datos_crudos():
    """Explora la estructura completa de datos de la estación"""
    try:
        url = f"https://api.weatherlink.com/v2/current/{STATION_ID}"
        headers = {
            "X-Api-Secret": API_SECRET
        }
        params = {
            "api-key": API_KEY
        }
        
        st.write("🔬 **Explorando estructura completa de datos...**")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            st.success("✅ Datos obtenidos exitosamente")
            st.write("📊 **Estructura completa de la respuesta:**")
            
            # Mostrar la estructura JSON completa
            st.json(data)
            
            # Análisis detallado
            if 'sensors' in data:
                st.write("---")
                st.write("🔍 **Análisis de sensores:**")
                
                for i, sensor in enumerate(data['sensors']):
                    with st.expander(f"📡 Sensor {i+1} - Tipo: {sensor.get('sensor_type', 'N/A')}"):
                        st.write(f"**Información del sensor:**")
                        st.write(f"- Tipo: {sensor.get('sensor_type')}")
                        st.write(f"- ID: {sensor.get('lsid')}")
                        
                        if 'data' in sensor and sensor['data']:
                            st.write(f"**Campos disponibles:**")
                            data_keys = list(sensor['data'][0].keys())
                            st.write(data_keys)
                            
                            st.write(f"**Valores actuales:**")
                            for key, value in sensor['data'][0].items():
                                st.write(f"- {key}: {value}")
                        else:
                            st.write("❌ No hay datos disponibles para este sensor")
            
            # Buscar todos los campos que podrían ser temperatura o humedad
            st.write("---")
            st.write("🌡️ **Campos que podrían ser temperatura:**")
            temp_fields = []
            humidity_fields = []
            
            if 'sensors' in data:
                for sensor in data['sensors']:
                    if 'data' in sensor and sensor['data']:
                        for key, value in sensor['data'][0].items():
                            if any(word in key.lower() for word in ['temp', 'temperature']):
                                temp_fields.append(f"{key}: {value}")
                            if any(word in key.lower() for word in ['hum', 'humidity', 'rh']):
                                humidity_fields.append(f"{key}: {value}")
            
            if temp_fields:
                st.write("🌡️ **Posibles campos de temperatura:**")
                for field in temp_fields:
                    st.write(f"- {field}")
            else:
                st.warning("⚠️ No se encontraron campos de temperatura")
            
            if humidity_fields:
                st.write("💧 **Posibles campos de humedad:**")
                for field in humidity_fields:
                    st.write(f"- {field}")
            else:
                st.warning("⚠️ No se encontraron campos de humedad")
                
        else:
            st.error(f"❌ Error: Código {response.status_code}")
            st.write(response.text)
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# 🔍 Función para listar todas las estaciones disponibles
def listar_estaciones():
    """Lista todas las estaciones disponibles para encontrar el ID correcto"""
    try:
        url = f"https://api.weatherlink.com/v2/stations"
        headers = {
            "X-Api-Secret": API_SECRET
        }
        params = {
            "api-key": API_KEY
        }
        
        st.write("🔄 **Consultando endpoint /stations...**")
        st.write(f"🌐 URL: {url}")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        st.write(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            st.success("✅ ¡Conexión exitosa al endpoint /stations!")
            data = response.json()
            
            # Mostrar información general
            total_stations = len(data.get('stations', []))
            st.write(f"📈 **Total de estaciones encontradas: {total_stations}**")
            
            if 'stations' in data and data['stations']:
                st.write("---")
                st.write("🏠 **Detalles de tus estaciones:**")
                
                for i, station in enumerate(data['stations'], 1):
                    st.write(f"### 📡 Estación {i}")
                    st.write(f"**🆔 Station ID**: `{station.get('station_id', 'N/A')}`")
                    st.write(f"**📛 Nombre**: {station.get('station_name', 'Sin nombre')}")
                    st.write(f"**🏷️ Descripción**: {station.get('description', 'Sin descripción')}")
                    st.write(f"**🌍 Zona horaria**: {station.get('time_zone', 'N/A')}")
                    st.write(f"**🗺️ Ubicación**: Lat {station.get('latitude', 'N/A')}, Lon {station.get('longitude', 'N/A')}")
                    st.write(f"**🔢 UUID**: `{station.get('station_uuid', 'N/A')}`")
                    
                    # Verificar si coincide con el Station ID actual
                    if station.get('station_id') == STATION_ID:
                        st.success(f"✅ **¡Esta es la estación configurada actualmente en el código!**")
                    
                    # Mostrar sensores si están disponibles
                    if 'gateway_id_hex' in station:
                        st.write(f"**🌐 Gateway ID**: {station.get('gateway_id_hex', 'N/A')}")
                    
                    st.write("---")
                
                # Recomendación
                st.info("💡 **Recomendación**: Si ves una estación diferente a la ID 167591, copia el Station ID correcto y actualiza el código.")
                
            else:
                st.warning("⚠️ No se encontraron estaciones en tu cuenta")
                
        elif response.status_code == 401:
            st.error("❌ Error de autenticación")
            try:
                error_detail = response.json()
                st.write(f"**Error detallado**: {error_detail}")
            except:
                st.write(f"**Respuesta raw**: {response.text}")
        else:
            st.error(f"❌ Error inesperado: Código {response.status_code}")
            try:
                error_detail = response.json()
                st.write(f"**Error detallado**: {error_detail}")
            except:
                st.write(f"**Respuesta raw**: {response.text}")
            
    except Exception as e:
        st.error(f"❌ Error al consultar estaciones: {str(e)}")

# 🧪 Función para probar credenciales manuales
def probar_credenciales_manuales(api_key, api_secret, station_id):
    """Prueba credenciales ingresadas manualmente"""
    try:
        url = f"https://api.weatherlink.com/v2/stations"
        headers = {
            "X-Api-Secret": api_secret
        }
        params = {
            "api-key": api_key
        }
        
        st.sidebar.write("🔄 Probando credenciales...")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            st.sidebar.success("✅ ¡Credenciales correctas!")
            data = response.json()
            st.sidebar.write(f"Estaciones encontradas: {len(data.get('stations', []))}")
            
            # Mostrar detalles de las estaciones
            if 'stations' in data:
                for station in data['stations']:
                    if station.get('station_id') == station_id:
                        st.sidebar.success(f"✅ Estación {station_id} encontrada!")
                        st.sidebar.write(f"Nombre: {station.get('station_name', 'N/A')}")
                        break
                else:
                    st.sidebar.warning(f"⚠️ Station ID {station_id} no encontrada en tus estaciones")
                    
        elif response.status_code == 401:
            st.sidebar.error("❌ Credenciales incorrectas")
            try:
                error_detail = response.json()
                st.sidebar.write(f"Error: {error_detail}")
            except:
                st.sidebar.write(f"Respuesta: {response.text}")
        else:
            st.sidebar.warning(f"⚠️ Código inesperado: {response.status_code}")
            
    except Exception as e:
        st.sidebar.error(f"❌ Error: {str(e)}")

# 🧪 Función para probar solo la autenticación
def probar_autenticacion():
    """Prueba la autenticación sin procesar datos"""
    try:
        url = f"https://api.weatherlink.com/v2/stations"
        headers = {
            "X-Api-Secret": API_SECRET
        }
        params = {
            "api-key": API_KEY
        }
        
        st.sidebar.write("🔄 Probando autenticación...")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            st.sidebar.success("✅ Autenticación exitosa")
            data = response.json()
            st.sidebar.write(f"Estaciones encontradas: {len(data.get('stations', []))}")
        elif response.status_code == 401:
            st.sidebar.error("❌ Error de autenticación")
            try:
                error_detail = response.json()
                st.sidebar.write(f"Error: {error_detail}")
            except:
                st.sidebar.write(f"Respuesta: {response.text}")
        else:
            st.sidebar.warning(f"⚠️ Código inesperado: {response.status_code}")
            
    except Exception as e:
        st.sidebar.error(f"❌ Error en la prueba: {str(e)}")

# 📈 Función para calcular VPD
def calcular_vpd(temp_c, hr):
    svp = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    vpd = (1 - hr / 100) * svp
    return round(vpd, 2)

# 📊 Clasificación del VPD
def clasificar_vpd(vpd):
    if vpd < 0.4:
        return "🔵 Muy bajo (riesgo de hongos)"
    elif vpd < 1.2:
        return "🟢 Ideal para crecimiento"
    elif vpd < 2.0:
        return "🟠 Moderado (estrés hídrico)"
    else:
        return "🔴 Alto (riesgo de cierre estomático)"

# 🌐 Consulta a la API
def obtener_datos_estacion():
    try:
        url = f"https://api.weatherlink.com/v2/current/{STATION_ID}"
        headers = {
            "X-Api-Secret": API_SECRET
        }
        params = {
            "api-key": API_KEY
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 401:
            st.error("🔑 **Error de Autenticación (401)**")
            st.markdown("""
### 🔑 ¿Error de credenciales?
Si recibes un error 401, verifica:
1. **API Key y Secret**: Deben tener exactamente 32 caracteres cada una
2. **WeatherLink Console**: Ve a [weatherlink.com](https://www.weatherlink.com) → Developer Console
3. **Permisos**: Asegúrate de que la API Key tenga permisos de lectura
4. **Station ID**: Verifica que el ID 167591 sea correcto para tu estación
            """)
            st.info("💡 También puedes usar el botón '🧪 Probar Solo Autenticación' en el sidebar para verificar las credenciales")
            return None, None
            
        response.raise_for_status()
        
        data = response.json()
        
        # Verificar que la respuesta tenga sensores
        if 'sensors' not in data or not data['sensors']:
            st.error("❌ No se encontraron sensores en la respuesta de la API")
            return None, None
        
        # Buscar temperatura y humedad en el sensor correcto
        temp = None
        hr = None
        
        for i, sensor in enumerate(data['sensors']):
            if sensor.get('data'):
                sensor_data = sensor['data'][0]
                sensor_type = sensor.get('sensor_type', 'N/A')
                
                # Buscar en sensor que tenga 'hum' y 'temp'
                if 'hum' in sensor_data and 'temp' in sensor_data:
                    temp_f = sensor_data['temp']  # Temperatura en Fahrenheit
                    temp = (temp_f - 32) * 5/9  # Convertir a Celsius
                    hr = sensor_data['hum']
                    break
                # También buscar en sensor tipo 53 específicamente
                elif sensor_type == 53:
                    for temp_key in ['temp', 'temperature', 'temp_out', 'temp_f']:
                        if temp_key in sensor_data:
                            temp_f = sensor_data[temp_key]
                            temp = (temp_f - 32) * 5/9
                            break
                    for humidity_key in ['hum', 'humidity', 'humidity_out', 'rh']:
                        if humidity_key in sensor_data:
                            hr = sensor_data[humidity_key]
                            break
                    if temp is not None and hr is not None:
                        break
        
        if temp is None or hr is None:
            st.error("❌ No se pudieron encontrar datos de temperatura o humedad")
            st.write("Verifica que la estación esté enviando datos")
            return None, None
            
        return temp, hr
        
    except requests.exceptions.Timeout:
        st.error("⏰ Tiempo de espera agotado. Verifica tu conexión a internet.")
        return None, None
    except requests.exceptions.ConnectionError:
        st.error("🌐 Error de conexión. Verifica tu conexión a internet.")
        return None, None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Error HTTP {e.response.status_code}: Verifica las credenciales de la API")
        return None, None
    except KeyError as e:
        st.error(f"❌ Error en la estructura de datos: {e}")
        return None, None
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        return None, None

# 📈 Gráfico de líneas - Evolución VPD por hora
def graficar_evolucion_vpd():
    """Genera gráfico de líneas mostrando la evolución del VPD en el tiempo"""
    try:
        historico = cargar_historico()
        
        if not historico or len(historico) == 0:
            st.warning("⚠️ No hay datos históricos disponibles. La app guardará datos automáticamente cada 15 minutos.")
            return
        
        st.info(f"📊 Cargados {len(historico)} registros desde Supabase")
        
        # Convertir a DataFrame
        df = pd.DataFrame(historico)
        
        # Verificar columnas
        if 'timestamp' not in df.columns:
            st.error(f"❌ Error: Columnas encontradas: {list(df.columns)}")
            st.error(f"Primer registro: {historico[0]}")
            return
            
        df['datetime'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('datetime')
    except Exception as e:
        st.error(f"❌ Error al cargar datos históricos: {str(e)}")
        return
    
    # Crear figura
    fig = go.Figure()
    
    # Línea principal de VPD
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['vpd'],
        mode='lines+markers',
        name='VPD',
        line=dict(color='#2196F3', width=3),
        marker=dict(size=8, color='#1976D2'),
        hovertemplate='<b>%{x|%d/%m/%Y %H:%M}</b><br>VPD: %{y} kPa<extra></extra>'
    ))
    
    # Zona ideal (0.4 - 1.2 kPa)
    fig.add_hrect(
        y0=0.4, y1=1.2,
        fillcolor="green", opacity=0.1,
        layer="below", line_width=0,
        annotation_text="Zona Ideal",
        annotation_position="top left"
    )
    
    # Líneas de referencia
    fig.add_hline(y=0.4, line_dash="dash", line_color="green", opacity=0.5, annotation_text="VPD Min (0.4)")
    fig.add_hline(y=1.2, line_dash="dash", line_color="green", opacity=0.5, annotation_text="VPD Max (1.2)")
    
    # Configuración del gráfico
    fig.update_layout(
        title='📈 Evolución de VPD - PYGANFLOR',
        xaxis_title='Fecha y Hora',
        yaxis_title='VPD (kPa)',
        height=500,
        hovermode='x unified',
        showlegend=False,
        template='plotly_white',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickformat='%d/%m %H:%M'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            range=[0, max(df['vpd'].max() + 0.5, 2.0)]
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Estadísticas rápidas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total Registros", len(df))
    with col2:
        st.metric("📈 VPD Promedio", f"{df['vpd'].mean():.2f} kPa")
    with col3:
        st.metric("⬆️ VPD Máximo", f"{df['vpd'].max():.2f} kPa")
    with col4:
        st.metric("⬇️ VPD Mínimo", f"{df['vpd'].min():.2f} kPa")

# 🎨 Gráfico psicrométrico de Mollier
def graficar_psicrometrico(temp_actual, hr_actual, vpd_actual):
    import numpy as np
    
    fig = go.Figure()
    
    # Función para calcular humedad absoluta (g/kg aire seco)
    def calcular_humedad_absoluta(temp, hr):
        # Presión de vapor saturado (kPa)
        svp = 0.6108 * np.exp((17.27 * temp) / (temp + 237.3))
        # Presión de vapor real (kPa)
        vp = (hr / 100) * svp
        # Humedad absoluta (g/kg aire seco)
        # W = 621.97 * vp / (101.325 - vp)
        ha = 621.97 * vp / (101.325 - vp)
        return ha
    
    # Rango de temperaturas para el diagrama
    temp_range = np.linspace(-5, 40, 100)
    
    # Curvas de humedad relativa (10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 90%, 100%)
    hr_levels = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    
    for hr in hr_levels:
        humedad_abs_curve = []
        temp_curve = []
        
        for temp in temp_range:
            if temp >= -5:  # Rango de temperaturas válidas
                try:
                    ha = calcular_humedad_absoluta(temp, hr)
                    if 0 <= ha <= 50:  # Rango razonable de humedad absoluta
                        humedad_abs_curve.append(ha)
                        temp_curve.append(temp)
                except:
                    continue
        
        # Líneas de humedad relativa más gruesas
        fig.add_trace(go.Scatter(
            x=humedad_abs_curve,
            y=temp_curve,
            mode='lines',
            name=f'HR {hr}%',
            line=dict(width=3, color='blue'),
            opacity=0.7,
            hovertemplate=f'HR: {hr}%<br>Temp: %{{y:.1f}}°C<br>Humedad Abs: %{{x:.1f}} g/kg<extra></extra>',
            showlegend=False  # Quitar etiquetas de la derecha
        ))
    
    # Líneas de VPD constante (solo zona ideal - verde)
    vpd_levels = [0.4, 0.8, 1.2]  # Solo líneas de zona ideal
    
    for vpd_level in vpd_levels:
        humedad_abs_vpd = []
        temp_vpd = []
        
        for temp in temp_range:
            if temp >= 0:
                try:
                    svp = 0.6108 * np.exp((17.27 * temp) / (temp + 237.3))
                    # Para VPD constante: HR = (1 - VPD/SVP) * 100
                    if svp > vpd_level:  # Solo si es físicamente posible
                        hr_calc = (1 - vpd_level / svp) * 100
                        if 10 <= hr_calc <= 100:  # Rango razonable
                            ha = calcular_humedad_absoluta(temp, hr_calc)
                            if 0 <= ha <= 50:
                                humedad_abs_vpd.append(ha)
                                temp_vpd.append(temp)
                except:
                    continue
        
        # Solo colores verdes para zona ideal
        if vpd_level == 0.4:
            color = '#00FF00'  # Verde brillante (límite inferior ideal)
        elif vpd_level == 1.2:
            color = '#00AA00'  # Verde oscuro (límite superior ideal)
        else:
            color = '#90EE90'  # Verde claro
            
        fig.add_trace(go.Scatter(
            x=humedad_abs_vpd,
            y=temp_vpd,
            mode='lines',
            name=f'VPD {vpd_level} kPa',
            line=dict(width=1, color=color, dash='dash'),  # Líneas más delgadas
            hovertemplate=f'VPD: {vpd_level} kPa<br>Temp: %{{y:.1f}}°C<br>Humedad Abs: %{{x:.1f}} g/kg<extra></extra>',
            showlegend=False  # Quitar etiquetas de la derecha
        ))
    
    # Zona ideal de VPD (entre 0.4 y 1.2 kPa) - Área sombreada
    temp_zona = np.linspace(0, 35, 50)
    ha_limite_04 = []  # Humedad absoluta para VPD = 0.4
    ha_limite_12 = []  # Humedad absoluta para VPD = 1.2
    temp_zona_valida = []
    
    for temp in temp_zona:
        try:
            svp = 0.6108 * np.exp((17.27 * temp) / (temp + 237.3))
            
            # HR para VPD = 0.4
            hr_04 = (1 - 0.4 / svp) * 100
            # HR para VPD = 1.2
            hr_12 = (1 - 1.2 / svp) * 100
            
            if 10 <= hr_04 <= 100 and 10 <= hr_12 <= 100:
                ha_04 = calcular_humedad_absoluta(temp, hr_04)
                ha_12 = calcular_humedad_absoluta(temp, hr_12)
                
                if 0 <= ha_04 <= 50 and 0 <= ha_12 <= 50:
                    ha_limite_04.append(ha_04)
                    ha_limite_12.append(ha_12)
                    temp_zona_valida.append(temp)
        except:
            continue
    
    # Crear área sombreada para zona ideal
    if len(temp_zona_valida) > 0:
        fig.add_trace(go.Scatter(
            x=ha_limite_04 + ha_limite_12[::-1],
            y=temp_zona_valida + temp_zona_valida[::-1],
            fill='toself',
            fillcolor='rgba(0, 255, 0, 0.15)',
            line=dict(color='rgba(0,0,0,0)'),
            name='Zona Ideal VPD (0.4-1.2 kPa)',
            hoverinfo='name',
            showlegend=False  # Quitar etiquetas de la derecha
        ))
    
    # Punto actual de la estación (punto en lugar de estrella)
    ha_actual = calcular_humedad_absoluta(temp_actual, hr_actual)
    
    fig.add_trace(go.Scatter(
        x=[ha_actual],
        y=[temp_actual],
        mode='markers',
        name=f'PYGANFLOR VPD: {vpd_actual} kPa',
        marker=dict(
            size=15,
            color='red',
            symbol='circle',  # Cambiar de estrella a punto
            line=dict(width=3, color='darkred')
        ),
        hovertemplate=f'🏠 PYGANFLOR<br>Temp: {temp_actual:.1f}°C<br>HR: {hr_actual}%<br>Humedad Abs: {ha_actual:.1f} g/kg<br>VPD: {vpd_actual} kPa<extra></extra>',
        showlegend=False  # Quitar etiquetas de la derecha
    ))
    
    # Configuración del gráfico con optimización para iPhone
    fig.update_layout(
        title='DIAGRAMA MOLLIER VPD PYGANFLOR',
        xaxis_title='Humedad Absoluta (g/kg aire seco)',
        yaxis_title='Temperatura (°C)',
        width=900,
        height=700,
        hovermode='closest',
        showlegend=False,  # Ocultar completamente la leyenda
        template='plotly_white',
        title_font_size=16,
        title_x=0.5,
        # Optimizaciones específicas para móvil
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Eje X principal (inferior) - Humedad Absoluta
    fig.update_xaxes(
        range=[0, 25], 
        dtick=5, 
        showgrid=True, 
        gridwidth=1, 
        gridcolor='lightgray',
        side='bottom'
    )
    
    # Eje Y
    fig.update_yaxes(
        range=[-5, 40], 
        dtick=5, 
        showgrid=True, 
        gridwidth=1, 
        gridcolor='lightgray'
    )
    
    # Agregar anotaciones para VPD
    fig.add_annotation(
        x=15, y=30,
        text="🟢 ZONA IDEAL<br>VPD: 0.4 - 1.2 kPa",
        showarrow=True,
        arrowhead=2,
        arrowcolor="green",
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="green",
        borderwidth=2,
        font=dict(size=12)
    )
    
    # Configuración específica para dispositivos móviles
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'VPD_PYGANFLOR',
            'height': 500,
            'width': 700,
            'scale': 1
        },
        'responsive': True
    }
    
    # Renderizar gráfico
    try:
        st.plotly_chart(fig, use_container_width=True, config=config)
    except Exception as e:
        # Fallback para iPhone si hay problemas con Plotly
        st.error("⚠️ Problema al cargar gráfico en iPhone")
        st.info("📊 Mostrando datos en formato simple:")
        
        # Mostrar datos en tabla como fallback
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌡️ Temperatura", f"{temp_actual:.1f}°C")
        with col2:
            st.metric("💧 Humedad", f"{hr_actual}%")
        with col3:
            ha_actual = calcular_humedad_absoluta(temp_actual, hr_actual)
            st.metric("💨 Humedad Abs.", f"{ha_actual:.1f} g/kg")
        
        # Estado VPD
        estado = clasificar_vpd(vpd_actual)
        if "IDEAL" in estado:
            st.success(f"✅ VPD: {vpd_actual} kPa - {estado}")
        elif "BAJO" in estado:
            st.warning(f"⚠️ VPD: {vpd_actual} kPa - {estado}")
        else:
            st.error(f"❌ VPD: {vpd_actual} kPa - {estado}")
        
        st.write("🔧 **Solución:** Actualiza Safari o usa Chrome en iPhone")
    
    # Interpretación del resultado
    st.markdown("### 📋 Interpretación del Diagrama Mollier:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🌡️ Temperatura", f"{temp_actual:.1f}°C")
        st.metric("💧 Humedad Relativa", f"{hr_actual}%")
    
    with col2:
        st.metric("💨 Humedad Absoluta", f"{ha_actual:.1f} g/kg")
        st.metric("📈 VPD", f"{vpd_actual} kPa")
    
    if vpd_actual < 0.4:
        st.warning("🔵 **PYGANFLOR está en zona de VPD muy bajo**: Riesgo de hongos y enfermedades")
        st.write("💡 **Recomendación**: Aumentar ventilación o reducir humedad")
    elif 0.4 <= vpd_actual <= 1.2:
        st.success("🟢 **¡Perfecto! PYGANFLOR está en la zona ideal**: Condiciones óptimas para crecimiento")
        st.write("✅ **Mantén estas condiciones** para el mejor desarrollo de las plantas")
    elif 1.2 < vpd_actual <= 2.0:
        st.warning("🟠 **PYGANFLOR está en zona moderada**: Posible estrés hídrico")
        st.write("💡 **Recomendación**: Aumentar humedad o reducir temperatura")
    else:
        st.error("🔴 **PYGANFLOR está en zona de VPD alto**: Riesgo de cierre estomático")
        st.write("⚠️ **Acción necesaria**: Aumentar humedad significativamente o reducir temperatura")

# 🖥️ Interfaz Streamlit
st.set_page_config(page_title="Consulta VPD", page_icon="🌿")
# 🌿 APLICACIÓN PRINCIPAL
st.title("🌿 Consulta de VPD PYGANFLOR")

# 📱 DETECCIÓN Y MENSAJE PARA MÓVILES
st.markdown("""
<div style="background-color: #28A745; color: white; padding: 10px; border-radius: 5px; text-align: center; margin: 10px 0;">
    <h3>📱 VPD Monitor PYGANFLOR</h3>
    <p>Monitoreo en tiempo real para agricultura</p>
</div>
""", unsafe_allow_html=True)

# 🔧 PRUEBA DE VISIBILIDAD PARA MÓVILES
st.success("✅ Si ves este mensaje, la app está cargando correctamente")
st.info("📱 Optimizado para dispositivos móviles")

# 📱 Debug para iPhone - mostrar información del navegador
if st.sidebar.checkbox("🔧 Debug Móvil", help="Activar si tienes problemas en móvil"):
    st.sidebar.write("**Info del navegador:**")
    st.sidebar.success("✅ App cargada correctamente")
    st.sidebar.info("💡 Si ves esto, la conexión funciona")
    st.sidebar.write("🔄 Actualizando datos...")

st.title("🌿 Monitor VPD PYGANFLOR")

# 🔄 CREAR TABS PARA SEPARAR CONTENIDO
tab1, tab2, tab3 = st.tabs(["📊 Datos Actuales", "📈 Gráfica Histórica", "📋 Tabla de Datos"])

# ===== TAB 1: DATOS ACTUALES =====
with tab1:
    # Validar credenciales en el sidebar
    validar_credenciales()

    # Información inicial
    st.markdown("""
    ## 📊 Calculadora de Déficit de Presión de Vapor (VPD)

    Esta aplicación obtiene datos en tiempo real de tu estación meteorológica WeatherLink ubicada en la zona 1 de PYGANFLOR
    y calcula el VPD, un parámetro crucial para optimizar el crecimiento de las plantas.

    ### 🎯 Rangos de VPD:
    - 🔵 **Muy bajo (< 0.4 kPa)**: Riesgo de hongos
    - 🟢 **Ideal (0.4 - 1.2 kPa)**: Óptimo para crecimiento
    - 🟠 **Moderado (1.2 - 2.0 kPa)**: Posible estrés hídrico
- 🔴 **Alto (> 2.0 kPa)**: Riesgo de cierre estomático

---
""")

# Botón para obtener datos
if st.button("🔍 Generar VPD", type="primary"):
    # Obtener hora actual de Colombia (UTC-5)
    colombia_tz = timezone(timedelta(hours=-5))
    hora_actual = datetime.now(colombia_tz).strftime("%d/%m/%Y %H:%M:%S")
    
    with st.spinner("🔄 Obteniendo datos de la estación..."):
        temp, hr = obtener_datos_estacion()
        
    if temp is not None and hr is not None:
        vpd = calcular_vpd(temp, hr)
        rango = clasificar_vpd(vpd)

        st.success("✅ Datos obtenidos correctamente")
        
        # 🕐 Mostrar hora de forma más clara
        st.markdown(f"""
        <div style="background-color: #E3F2FD; border: 2px solid #2196F3; border-radius: 10px; padding: 15px; text-align: center; margin: 15px 0;">
            <h4 style="color: #000000; margin: 0;">🕐 Última actualización</h4>
            <h3 style="color: #000000; margin: 10px 0;">{hora_actual}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 📱 MOSTRAR DATOS BÁSICOS PRIMERO (SIEMPRE VISIBLE EN MÓVIL)
        st.markdown("""
        <div style="background-color: #F8F9FA; border: 3px solid #28A745; border-radius: 15px; padding: 20px; margin: 20px 0;">
            <h3 style="color: #000000; text-align: center;">📊 DATOS ACTUALES PYGANFLOR</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar métricas con estilo forzado para móvil
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="background-color: #E3F2FD; border: 2px solid #2196F3; border-radius: 10px; padding: 15px; text-align: center; margin: 10px 0;">
                <h4 style="color: #000000; margin: 0;">🌡️ Temperatura</h4>
                <h2 style="color: #000000; margin: 10px 0;">{temp:.1f}°C</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="background-color: #E8F5E8; border: 2px solid #4CAF50; border-radius: 10px; padding: 15px; text-align: center; margin: 10px 0;">
                <h4 style="color: #000000; margin: 0;">💧 Humedad</h4>
                <h2 style="color: #000000; margin: 10px 0;">{hr}%</h2>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            # Color según VPD
            if "IDEAL" in rango:
                color_bg = "#E8F5E8"
                color_border = "#4CAF50"
                icon = "✅"
            elif "BAJO" in rango:
                color_bg = "#FFF3E0"
                color_border = "#FF9800"
                icon = "⚠️"
            else:
                color_bg = "#FFEBEE"
                color_border = "#F44336"
                icon = "❌"
                
            st.markdown(f"""
            <div style="background-color: {color_bg}; border: 2px solid {color_border}; border-radius: 10px; padding: 15px; text-align: center; margin: 10px 0;">
                <h4 style="color: #000000; margin: 0;">{icon} VPD</h4>
                <h2 style="color: #000000; margin: 10px 0;">{vpd} kPa</h2>
                <p style="color: #000000; margin: 0; font-weight: bold;">{rango}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Mostrar métricas también con el sistema normal (fallback)
        st.write("---")
        col1b, col2b, col3b = st.columns(3)
        with col1b:
            st.metric("🌡️ Temperatura", f"{temp:.1f}°C")
        with col2b:
            st.metric("💧 Humedad Relativa", f"{hr}%")
        with col3b:
            st.metric("📈 VPD", f"{vpd} kPa")
        
        st.info(f"📋 **Estado**: {rango}")
        
        # 💾 Guardar en histórico si han pasado 15 minutos
        if debe_guardar_lectura():
            st.info("💾 Guardando lectura automática...")
            resultado = agregar_lectura_historico(temp, hr, vpd)
            if not resultado:
                st.error("❌ No se pudo guardar la lectura. Revisa los mensajes de error arriba.")
        else:
            ultimo = obtener_ultimo_registro_tiempo()
            if ultimo:
                colombia_tz = timezone(timedelta(hours=-5))
                siguiente = ultimo + timedelta(minutes=15)
                st.info(f"⏱️ Próxima lectura automática: {siguiente.strftime('%H:%M:%S')}")

        # Diagrama Mollier y resumen
        st.write("---")
        mostrar_grafico = st.checkbox("📊 Mostrar Diagrama Mollier", value=True, help="Desactiva si tienes problemas en móvil")
        
        if mostrar_grafico:
            st.write("📊 **Diagrama Psicrométrico de Mollier**")
            graficar_psicrometrico(temp, hr, vpd)
        
        # Tabla con datos de la lectura actual
        st.subheader("📈 Resumen de la lectura")
        data = {
            'Parámetro': ['Temperatura', 'Humedad Relativa', 'VPD'],
            'Valor': [f"{temp:.1f}°C", f"{hr}%", f"{vpd} kPa"],
            'Estado': ['Normal', 'Normal', rango.split(' ', 1)[1]]
        }
        df = pd.DataFrame(data)
        st.table(df)
    else:
        st.error("❌ No se pudieron obtener los datos. Verifica la conexión a internet y las credenciales de la API.")

# ===== TAB 2: GRÁFICA HISTÓRICA =====
with tab2:
    st.header("📈 Evolución de VPD en el Tiempo")
    graficar_evolucion_vpd()

# ===== TAB 3: TABLA DE DATOS =====
with tab3:
    st.header("📋 Tabla de Datos Históricos")
    try:
        historico = cargar_historico()
        
        if not historico or len(historico) == 0:
            st.warning("⚠️ No hay datos históricos disponibles. La app guardará datos automáticamente cada 15 minutos.")
        else:
            st.info(f"📊 Cargados {len(historico)} registros desde Supabase")
            
            # Convertir a DataFrame
            df_historico = pd.DataFrame(historico)
            
            # Traducir días de la semana
            dias_es = {
                'Monday': 'Lunes',
                'Tuesday': 'Martes',
                'Wednesday': 'Miércoles',
                'Thursday': 'Jueves',
                'Friday': 'Viernes',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo'
            }
            df_historico['dia_semana'] = df_historico['dia_semana'].map(dias_es)
            
            # Seleccionar y ordenar columnas
            df_mostrar = df_historico[['dia_semana', 'fecha', 'hora', 'temperatura', 'humedad', 'vpd']].copy()
            df_mostrar.columns = ['Día', 'Fecha', 'Hora', 'Temp (°C)', 'HR (%)', 'VPD (kPa)']
            df_mostrar = df_mostrar.sort_values('Fecha', ascending=False)
            
            # Mostrar tabla con formato
            st.dataframe(
                df_mostrar,
                use_container_width=True,
                height=400
            )
            
            # Botón para descargar CSV
            csv = df_mostrar.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Descargar datos en CSV",
                data=csv,
                file_name=f"vpd_historico_pyganflor_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            # Información adicional
            st.info(f"📊 Total de registros: {len(df_mostrar)} | 📅 Últimos 7 días")
    except Exception as e:
        st.error(f"❌ Error al mostrar tabla: {str(e)}")
        st.info("💡 Si estás usando Supabase, verifica que la tabla 'vpd_historico' exista.")

# Sidebar con información adicional
st.sidebar.markdown("""
### 🔧 Información de la estación
- **ID de estación**: 167591
- **Ubicación**: Configurada en WeatherLink
- **Última actualización**: Tiempo real

### 📚 Sobre VPD
El Déficit de Presión de Vapor es la diferencia entre 
la presión de vapor saturado y la presión de vapor real 
del aire a una temperatura dada.

### 🌱 Aplicaciones
- Control de invernaderos
- Optimización de riego
- Prevención de enfermedades
- Maximización del rendimiento
""")