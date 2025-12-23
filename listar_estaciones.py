import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Usar las credenciales de la Finca 1 (Pyganflor)
API_KEY = os.getenv("FINCA1_API_KEY")
API_SECRET = os.getenv("FINCA1_API_SECRET")

print("🔍 Buscando todas las estaciones en tu cuenta WeatherLink...\n")

try:
    url = "https://api.weatherlink.com/v2/stations"
    headers = {
        "X-Api-Secret": API_SECRET
    }
    params = {
        "api-key": API_KEY
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        
        if "stations" in data and len(data["stations"]) > 0:
            print(f"✅ Se encontraron {len(data['stations'])} estación(es):\n")
            
            for station in data["stations"]:
                print(f"{'='*60}")
                print(f"📍 Nombre: {station.get('station_name', 'Sin nombre')}")
                print(f"🆔 STATION_ID: {station.get('station_id')} ⬅ USA ESTE NÚMERO")
                print(f"📡 Activa: {'Sí' if station.get('active') else 'No'}")
                print(f"📅 Registrada: {station.get('registered_date', 'N/A')}")
                if 'gateway_id' in station:
                    print(f"🌐 Gateway ID: {station.get('gateway_id')}")
                print(f"{'='*60}\n")
        else:
            print("⚠️ No se encontraron estaciones en esta cuenta.")
            print("Verifica que:")
            print("1. Las credenciales API sean correctas")
            print("2. Tengas al menos una estación registrada en weatherlink.com")
    else:
        print(f"❌ Error HTTP {response.status_code}")
        print(f"Respuesta: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n💡 Copia el STATION_ID que necesites y pégalo en tu archivo .env")
