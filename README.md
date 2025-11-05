# VPD Monitor - PYGANFLOR

Aplicación de monitoreo de VPD (Déficit de Presión de Vapor) para agricultura de precisión.

## 🌱 Características

- Monitoreo en tiempo real de temperatura y humedad
- Cálculo automático de VPD
- Diagrama psicrométrico de Mollier profesional
- Interfaz web responsiva
- Datos de WeatherLink API

## 🚀 Instalación Local

```bash
pip install -r requirements.txt
streamlit run app_vpd.py
```

## 📊 Uso

1. La aplicación se conecta automáticamente a la estación meteorológica
2. Muestra datos actuales de temperatura, humedad y VPD
3. Genera diagrama Mollier interactivo
4. Clasifica el VPD según rangos óptimos para cultivos

## 🔧 Configuración

Para uso en producción, configura las credenciales de API en `.streamlit/secrets.toml`

## 👨‍💻 Desarrollo

- Python 3.8+
- Streamlit
- Plotly para visualizaciones
- WeatherLink API v2