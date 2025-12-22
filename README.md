# VPD Monitor - PYGANFLOR

Monitor de VPD (Vapor Pressure Deficit) para agricultura, con integración a WeatherLink API.

## 🚀 Despliegue con Docker

### Requisitos previos
- Docker y Docker Compose instalados
- Servidor VPS (Ubuntu/Debian recomendado)
- Credenciales de WeatherLink API

### Instalación en VPS

1. Clonar el repositorio:
```bash
git clone https://github.com/renealejo96/vpd-monitor-pyganflor.git
cd vpd-monitor-pyganflor
```

2. Crear archivo `.env` con tus credenciales:
```bash
cp .env.example .env
nano .env
```

Editar con tus valores:
```env
API_KEY=tu_api_key
API_SECRET=tu_api_secret
STATION_ID=167591

# Opcional: para almacenamiento en Supabase
SUPABASE_URL=tu_url_supabase
SUPABASE_KEY=tu_key_supabase
```

3. Levantar el contenedor:
```bash
sudo docker compose up -d --build
```

4. Verificar que esté corriendo:
```bash
sudo docker ps
```

5. Acceder en el navegador:
```
http://IP_DEL_VPS:8501
```

### Comandos útiles

- Ver logs: `sudo docker logs vpd_app`
- Detener: `sudo docker compose down`
- Reiniciar: `sudo docker compose restart`
- Ver estado: `sudo docker ps`

## 📊 Almacenamiento de datos

La aplicación soporta tres modos:
- **Local JSON** (desarrollo): datos en `vpd_historico.json`
- **Supabase** (producción recomendado): base de datos cloud
- **Google Sheets** (alternativa): hoja de cálculo

Para usar Supabase, configura las variables `SUPABASE_URL` y `SUPABASE_KEY` en el archivo `.env`.

## 🔧 Tecnologías

- Python 3.11
- Streamlit
- Docker
- WeatherLink API
- Supabase (opcional)

## 📝 Licencia

Proyecto privado - PYGANFLOR