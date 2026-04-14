# Bot Ferreteria - WhatsApp Business Bot

Bot de WhatsApp para Ferreteria en Las Cabras, Chile. Permite a los clientes consultar precios, productos y horarios de atencion directamente por WhatsApp.

## Caracteristicas

- **Consulta de precios**: Escribe `precio [nombre del producto]` para buscar precios
- **Catalogo completo**: Escribe `productos` para ver todos los productos
- **Busqueda por codigo**: Escribe `codigo [numero]` para buscar por codigo
- **Horario de atencion**: Escribe `horario` para ver el horario
- **Ubicacion**: Escribe `ubicacion` para saber donde estamos

## Comandos disponibles

| Comando | Descripcion |
|---------|-------------|
| `precio [nombre]` | Busca el precio de un producto |
| `productos` | Muestra el catalogo completo |
| `codigo [nro]` | Busca producto por codigo |
| `horario` | Muestra el horario de atencion |
| `ubicacion` | Muestra la direccion |
| `buscar [nombre]` | Busca productos por nombre |

## Despliegue

### Opcion 1: Railway (Recomendado)

1. Ve a [railway.app](https://railway.app) y crea una cuenta
2. Haz clic en "New Project" -> "Deploy from GitHub repo"
3. Selecciona este repositorio: `oviedoem/bot-ferreteria`
4. Configura las variables de entorno:
   - `WHAPI_TOKEN`: Tu token de WHAPI Cloud
5. El despliegue se realizara automaticamente

### Opcion 2: Render

1. Ve a [render.com](https://render.com) y crea una cuenta
2. Crea un nuevo "Web Service"
3. Conecta tu repositorio de GitHub
4. Configuracion:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn bot_ferreteria:app`
5. Agrega las variables de entorno:
   - `WHAPI_TOKEN`: Tu token de WHAPI Cloud
6. Haz clic en "Create Web Service"

### Opcion 3: Heroku

1. Instala el CLI de Heroku
2. Ejecuta en la terminal:
   ```bash
   heroku login
   heroku create bot-ferreteria-whatsapp
   git push heroku main
   heroku config:set WHAPI_TOKEN=tu_token_aqui
   ```

## Configuracion del Webhook en WHAPI Cloud

Una vez desplegado el bot, configura el webhook en WHAPI Cloud:

1. Ve a [WHAPI Cloud](https://whapi.cloud)
2. Ve a la seccion de Webhooks
3. Configura:
   - **URL del Webhook**: `https://tu-dominio.com/webhook`
   - **Metodo**: POST
   - **Formato**: JSON
4. Guarda la configuracion

## Variables de Entorno

| Variable | Descripcion |
|----------|-------------|
| `WHAPI_TOKEN` | Tu token de autenticacion de WHAPI Cloud |
| `PORT` | Puerto del servidor (default: 5000) |

## Archivos del Proyecto

- `bot_ferreteria.py` - Codigo principal del bot
- `productos.json` - Catalogo de productos con precios
- `requirements.txt` - Dependencias de Python
- `Procfile` - Configuracion de despliegue
- `convertir_csv.py` - Script para convertir CSV a JSON
- `descargar_csv.py` - Script para descargar CSV desde OneDrive

## Actualizacion del Catalogo

El catalogo se actualiza automaticamente mediante un workflow de GitHub Actions que:
1. Descarga el CSV desde OneDrive
2. Lo convierte a JSON
3. Actualiza `productos.json` en el repositorio

## Licencia

Este proyecto es de uso interno de Ferreteria.
