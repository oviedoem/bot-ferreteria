from flask import Flask, request, jsonify
import requests, json, os, re

app = Flask(__name__)

# ============================================================
# EDITA SOLO ESTA LÍNEA CON TU TOKEN DE WHAPI.CLOUD
# ============================================================
WHAPI_TOKEN = "paZBDoXBHetA48viZxKc2KzAWnxnKpbH"
# ============================================================

WHAPI_URL = "https://gate.whapi.cloud/messages/text"

# Variables globales para cache de datos
datos_cache = None
ultima_carga = 0

def cargar_datos():
    global datos_cache, ultima_carga
    import time
    ahora = time.time()
    if datos_cache and (ahora - ultima_carga) < 30:
        return datos_cache
    with open("productos.json", "r", encoding="utf-8") as f:
        datos_cache = json.load(f)
    ultima_carga = ahora
    return datos_cache

def buscar_productos(datos, busqueda):
    """Busca productos por codigo o descripcion"""
    resultados = []
    busqueda = busqueda.strip().lower()
    for p in datos["productos"]:
        codigo = p.get("codigo", "").lower()
        nombre = p.get("nombre", "").lower()
        descripcion = p.get("descripcion", nombre).lower()
        # Busca coincidencia en codigo o descripcion
        if busqueda in codigo or busqueda in descripcion:
            resultados.append(p)
            if len(resultados) >= 20:  # Limita a 20 resultados
                break
    return resultados

def construir_catalogo(datos):
    """Construye catalogo de productos (max 30 para no saturar WhatsApp)"""
    lineas = ["📦 *Catálogo Ferretería:*\n"]
    productos = datos["productos"][:30]  # Muestra solo los primeros 30
    for p in productos:
        precio = p.get("precio", 0)
        stock = p.get("stock", "consultar")
        if stock == "disponible":
            estado = "✅"
        elif stock == "agotado":
            estado = "❌ Agotado"
        else:
            estado = "⚠️ Consultar"
        nombre = p.get("nombre", p.get("descripcion", "Sin nombre"))
        lineas.append(f"• {nombre}: ${precio:,} CLP {estado}")
    lineas.append(f"\n_Se muestran 30 de {len(datos['productos']):,} productos. Escribe *precio [producto]* o *codigo [nro]* para buscar uno específico._")
    return "\n".join(lineas)

def enviar(numero, mensaje):
    payload = {"to": numero, "body": mensaje}
    headers = {
        "Authorization": f"Bearer {WHAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        requests.post(WHAPI_URL, json=payload, headers=headers, timeout=10)
    except Exception as e:
        print("Error enviando mensaje:", e)

def procesar(texto, numero):
    datos = cargar_datos()
    t = texto.lower().strip()
    
    if any(p in t for p in ["hola", "buenas", "buenos", "buen dia", "buenas tardes", "buenas noches"]):
        return (
            "👋 ¡Hola! Bienvenido a *Ferretería Oviedo el Manzano* 🔧\n\n"
            "¿En qué puedo ayudarte?\n\n"
            "⏰ Escribe *horario* → Horario de atención\n"
            "📦 Escribe *productos* → Ver catálogo completo\n"
            "💰 Escribe *precio cemento* → Buscar precio de un producto\n"
            "🔢 Escribe *codigo 12345* → Buscar por código de producto\n"
            "📍 Escribe *ubicacion* → Cómo llegar\n\n"
            "También puedes escribirnos directo y te respondemos pronto 😊"
        )
    
    elif "horario" in t:
        h = datos.get("horario", "Consultar por WhatsApp")
        return f"⏰ *Horario de atención:*\n\n{h}"
    
    elif any(p in t for p in ["producto", "catalogo", "catálogo", "lista", "que tienen", "qué tienen", "que venden"]):
        return construir_catalogo(datos)
    
    elif "ubicacion" in t or "ubicación" in t or "donde" in t or "dónde" in t or "direccion" in t or "dirección" in t:
        d = datos.get("ubicacion", "Las Cabras, Región de O'Higgins")
        return f"📍 *Ubicación:*\n\n{d}"
    
    elif any(p in t for p in ["codigo", "código", "cod", "cod:", "nro", "numero"]):
        # Búsqueda por código
        busqueda = t
        for palabra in ["codigo", "código", "cod", "cod:", "nro", "numero", "precio"]:
            busqueda = busqueda.replace(palabra, "").strip()
        if busqueda:
            encontrados = buscar_productos(datos, busqueda)
            if encontrados:
                resp = f"🔢 *Producto encontrado por código:*\n"
                for p in encontrados:
                    nombre = p.get("nombre", p.get("descripcion", "Sin nombre"))
                    precio = p.get("precio", 0)
                    codigo = p.get("codigo", "N/A")
                    resp += f"\n• Cód. {codigo} | {nombre} → ${precio:,} CLP"
                return resp
            else:
                return f"🔍 No encontré ningún producto con código *{busqueda}*. Verifica el número e intenta nuevamente."
        return "Por favor escribe *codigo* seguido del número de código del producto. Ejemplo: codigo 12345"
    
    elif any(p in t for p in ["precio", "cuanto", "cuánto", "vale", "cuesta", "valor", "precio de"]):
        busqueda = t
        for palabra in ["precio", "cuanto vale", "cuánto vale", "cuanto cuesta", "cuánto cuesta", "valor", "precio de"]:
            busqueda = busqueda.replace(palabra, "").strip()
        if busqueda:
            encontrados = buscar_productos(datos, busqueda)
            if encontrados:
                resp = f"💰 *{len(encontrados)} resultado(s) para '{busqueda}':*\n"
                for p in encontrados:
                    nombre = p.get("nombre", p.get("descripcion", "Sin nombre"))
                    precio = p.get("precio", 0)
                    codigo = p.get("codigo", "")
                    if codigo:
                        resp += f"\n• Cód. {codigo} | {nombre} → ${precio:,} CLP (IVA inc.)"
                    else:
                        resp += f"\n• {nombre} → ${precio:,} CLP (IVA inc.)"
                return resp
            else:
                return (f"🔍 No encontré *{busqueda}* en el catálogo.\n"
                        "Escribe *productos* para ver la lista completa o contáctanos directamente.")
        return "Por favor escribe *precio* seguido del nombre del producto. Ejemplo: precio cemento"
    
    else:
        return (
            "Gracias por escribirnos 🔧\n\n"
            "Puedo ayudarte con:\n"
            "• *horario* → Horario de atención\n"
            "• *productos* → Catálogo de productos\n"
            "• *precio [nombre]* → Buscar precio\n"
            "• *codigo [nro]* → Buscar por código\n"
            "• *ubicacion* → Dónde encontrarnos\n\n"
            "Para consultas específicas, un vendedor te responderá pronto."
        )

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        msg = data["messages"][0]
        if msg.get("from_me"):
            return jsonify({"status": "ok"})
        numero = msg["chat_id"]
        texto = msg.get("text", {}).get("body", "")
        if texto:
            respuesta = procesar(texto, numero)
            enviar(numero, respuesta)
    except Exception as e:
        print("Error en webhook:", e)
    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot Ferretería activo - 12.000+ productos"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
