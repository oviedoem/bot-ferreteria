from flask import Flask, request, jsonify
import requests, json, os

app = Flask(__name__)

# ============================================================
#  EDITA SOLO ESTA LÍNEA CON TU TOKEN DE WHAPI.CLOUD
# ============================================================
WHAPI_TOKEN = "paZBDoXBHetA48viZxKc2KzAWnxnKpbH"
# ============================================================

WHAPI_URL = "https://gate.whapi.cloud/messages/text"

def cargar_datos():
    with open("productos.json", "r", encoding="utf-8") as f:
        return json.load(f)

def construir_catalogo(datos):
    lineas = ["📦 *Catálogo Ferretería:*\n"]
    for p in datos["productos"]:
        if p["stock"] == "disponible":
            estado = "✅"
        elif p["stock"] == "agotado":
            estado = "❌ Agotado"
        else:
            estado = "⚠️ Consultar"
        lineas.append(f"• {p['nombre']}: ${p['precio']:,} CLP  {estado}")
    lineas.append("\n_Precios pueden variar. Escribe *precio [producto]* para buscar uno específico._")
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
            "📍 Escribe *ubicacion* → Cómo llegar\n\n"
            "También puedes escribirnos directo y te respondemos pronto 😊"
        )

    elif "horario" in t:
        h = datos["horario"]
        return f"⏰ *Horario de atención:*\n\n{h}"

    elif any(p in t for p in ["producto", "catalogo", "catálogo", "lista", "que tienen", "qué tienen", "que venden"]):
        return construir_catalogo(datos)

    elif "ubicacion" in t or "ubicación" in t or "donde" in t or "dónde" in t or "direccion" in t or "dirección" in t:
        d = datos.get("ubicacion", "Las Cabras, Región de O'Higgins")
        return f"📍 *Ubicación:*\n\n{d}"

    elif any(p in t for p in ["precio", "cuanto", "cuánto", "vale", "cuesta", "valor"]):
        busqueda = (t.replace("precio", "").replace("cuanto vale", "")
                     .replace("cuánto vale", "").replace("cuanto cuesta", "")
                     .replace("cuánto cuesta", "").replace("valor", "").strip())
        if busqueda:
            encontrados = [p for p in datos["productos"] if busqueda in p["nombre"].lower()]
            if encontrados:
                resp = "💰 *Precio(s) encontrado(s):*\n"
                for p in encontrados:
                    resp += f"\n• {p['nombre']}: ${p['precio']:,} CLP"
                return resp
            else:
                return (f"🔍 No encontré *{busqueda}* en el catálogo.\n"
                        "Escribe *productos* para ver la lista completa o contáctanos directamente.")
        else:
            return construir_catalogo(datos)

    else:
        return (
            "Gracias por escribirnos 🔧\n\n"
            "Puedo ayudarte con:\n"
            "• *horario* → Horario de atención\n"
            "• *productos* → Catálogo de productos\n"
            "• *precio [nombre]* → Buscar precio\n"
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
        texto  = msg.get("text", {}).get("body", "")
        if texto:
            respuesta = procesar(texto, numero)
            enviar(numero, respuesta)
    except Exception as e:
        print("Error en webhook:", e)
    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot Ferretería activo"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
