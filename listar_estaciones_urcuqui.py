import requests

# REEMPLAZA CON LAS CREDENCIALES DE LA CUENTA DE URCUQUÍ
API_KEY = "hrd0nyzmwv5esftiktab7nsgazmi6zp8"
API_SECRET = "m5jyv0unsyzktbxdt1xnm9dqw4q4pwktI"

print("Buscando estaciones en la cuenta de Urcuqui...\n")

url = "https://api.weatherlink.com/v2/stations"
headers = {"X-Api-Secret": API_SECRET}
params = {"api-key": API_KEY}

response = requests.get(url, headers=headers, params=params, timeout=10)

if response.status_code == 200:
    data = response.json()
    
    if "stations" in data and len(data["stations"]) > 0:
        print(f"Se encontraron {len(data['stations'])} estacion(es):\n")
        
        for station in data["stations"]:
            print("="*60)
            print(f"Nombre: {station.get('station_name', 'Sin nombre')}")
            print(f"STATION_ID: {station.get('station_id')} <--- USA ESTE NUMERO")
            print(f"Activa: {'Si' if station.get('active') else 'No'}")
            print("="*60 + "\n")
    else:
        print("No se encontraron estaciones.")
else:
    print(f"Error HTTP {response.status_code}")
    print(f"Respuesta: {response.text}")
