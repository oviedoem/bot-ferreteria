#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Ferretería - WhatsApp Business Bot
Conecta con productos.json para consultas de productos y precios
Version 2.5 - Mensaje de bienvenida mejorado"""

import os
import json
import time
import re
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# =========================================================
# EDITE SOLO ESTAS LINEAS CON TU TOKEN Y URL
# =========================================================
WHAPI_TOKEN = os.environ.get("WHAPI_TOKEN", "paZBDoXBHetA48viZxKc2KzAMnxnKpbH")
WHAPI_URL = "https://gate.whapi.cloud/messages/text"
# =========================================================

# Variables globales para cache de datos
datos_cache = None
ultima_carga = 0

def cargar_datos():
    """Carga datos de productos.json con manejo de errores"""
    global datos_cache, ultima_carga
    ahora = time.time()
    if datos_cache and (ahora - ultima_carga) < 30:
        return datos_cache
    try:
        with open("productos.json", "r", encoding="utf-8") as f:
            datos_cache = json.load(f)
        ultima_carga = ahora
        print(f"Datos cargados: {len(datos_cache.get('productos', []))} productos")
        return datos_cache
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return {"productos": [], "horario": "Consultar por WhatsApp", "ubicacion": "Las Cabras"}

def enviar(numero, texto):
    """Envía mensaje de texto vía WHAPI"""
    if not numero or not texto:
        return
    # Limpiar el número: quitar @s.whatsapp.net y caracteres no numéricos
    chat_id = numero
    if "@s.whatsapp.net" in numero:
        chat_id = numero.replace("@s.whatsapp.net", "")
    # Asegurar formato correcto (solo números)
    chat_id = re.sub(r'[^0-9]', '', chat_id)
    if not chat_id:
        print(f"Número inválido después de limpieza: {numero}")
        return
    headers = {"Authorization": f"Bearer {WHAPI_TOKEN}"}
    payload = {
        "to": f"{chat_id}@s.whatsapp.net",
        "body": texto
    }
    try:
        resp = requests.post(WHAPI_URL, json=payload, headers=headers, timeout=10)
        print(f"Enviado a {chat_id}@s.whatsapp.net: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Respuesta API: {resp.text[:200]}")
    except Exception as e:
        print(f"Error enviando: {e}")

def buscar_productos(datos, busqueda):
    """Busca productos por nombre, descripción o código"""
    productos = datos.get("productos", [])
    busqueda_lower = busqueda.lower()
    encontrados = []
    for p in productos:
        nombre = p.get("nombre", p.get("descripcion", "")).lower()
        codigo = p.get("codigo", "").lower()
        if busqueda_lower in nombre or busqueda_lower in codigo:
            encontrados.append(p)
    return encontrados

def procesar(texto, numero):
    """Procesa el mensaje y devuelve la respuesta"""
    datos = cargar_datos()
    texto = texto.strip()
    texto_lower = texto.lower()
    if texto_lower.startswith("precio "):
        busqueda = texto[7:].strip()
        if len(busqueda) < 2:
            return "Escribe 'precio' seguido del nombre. Ej: precio cemento"
        encontrados = buscar_productos(datos, busqueda)
        if encontrados:
            resp = f"{len(encontrados)} resultado(s) para '{busqueda}':\n"
            for p in encontrados:
                nombre = p.get("nombre", p.get("descripcion", "Sin nombre"))
                precio = p.get("precio", 0)
                codigo = p.get("codigo", "")
                if codigo:
                    resp += f"\n- Cod. {codigo} | {nombre} -> ${precio:,} CLP (IVA inc.)"
                else:
                    resp += f"\n- {nombre} -> ${precio:,} CLP (IVA inc.)"
            return resp
        else:
            return f"No encontré '{busqueda}' en el catálogo.\nEscribe 'productos' para ver la lista completa o contáctanos directamente."
    elif texto_lower.startswith("codigo "):
        codigo_busqueda = texto[7:].strip().lower()
        if len(codigo_busqueda) < 2:
            return "Escribe 'codigo' seguido del código. Ej: codigo 1234"
        encontrados = [p for p in datos.get("productos", []) if codigo_busqueda in p.get("codigo", "").lower()]
        if encontrados:
            resp = f"{len(encontrados)} resultado(s) para código '{codigo_busqueda}':\n"
            for p in encontrados:
                nombre = p.get("nombre", p.get("descripcion", "Sin nombre"))
                precio = p.get("precio", 0)
                codigo = p.get("codigo", "")
                resp += f"\n- Cod. {codigo} | {nombre} -> ${precio:,} CLP (IVA inc.)"
            return resp
        else:
            return f"No encontré el código '{codigo_busqueda}' en el catálogo."
    elif texto_lower in ("productos", "catalogo", "catálogo", "lista"):
        productos = datos.get("productos", [])[:50]
        resp = f"Catálogo ({len(datos.get('productos', []))} productos):\n"
        for p in productos:
            nombre = p.get("nombre", p.get("descripcion", "Sin nombre"))
            precio = p.get("precio", 0)
            codigo = p.get("codigo", "")
            if codigo:
                resp += f"\n- {codigo}: {nombre} -> ${precio:,}"
            else:
                resp += f"\n- {nombre} -> ${precio:,}"
        if len(datos.get("productos", [])) > 50:
            resp += "\n\nEscribe 'precio [nombre]' para buscar un producto específico."
        return resp
    elif texto_lower in ("horario", "atencion", "atención"):
        horario = datos.get("horario", "Lunes a Viernes 09:00 - 18:00")
        return f"Horario de atención:\n{horario}\n\n¿En qué más puedo ayudarte?"
    elif texto_lower in ("ubicacion", "direccion", "donde", "ubicación"):
        ubicacion = datos.get("ubicacion", "Las Cabras, Chile")
        return f"Te esperamos en:\n{ubicacion}\n\n¿Necesitas algo más?"
    elif texto_lower.startswith("buscar "):
        busqueda = texto[7:].strip()
        if len(busqueda) < 2:
            return "Escribe 'buscar' seguido del nombre del producto."
        encontrados = buscar_productos(datos, busqueda)
        if encontrados:
            resp = f"{len(encontrados)} resultado(s):\n"
            for p in encontrados:
                nombre = p.get("nombre", p.get("descripcion", "Sin nombre"))
                precio = p.get("precio", 0)
                codigo = p.get("codigo", "")
                if codigo:
                    resp += f"\n- Cod. {codigo} | {nombre} -> ${precio:,} CLP"
                else:
                    resp += f"\n- {nombre} -> ${precio:,} CLP"
            return resp
        else:
            return f"No encontré '{busqueda}' en nuestro catálogo."
    else:
        return (
        "*🔧 ¡Gracias por escribirnos! 🔧*\n\n"
        "👋 *Puedo ayudarte con:*\n\n"
        "🕒 *horario* → Horario de atención\n"
        "📋 *productos* → Catálogo de productos\n"
        "💲 *precio [nombre]* → Buscar precio\n"
        "📍 *ubicacion* → Dónde encontrarnos\n\n"
        "👨‍💼 *Para consultas específicas, un vendedor te responderá pronto.*"
    )

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # Webhook verification - responde OK para que Whapi confirme
    if request.method == "GET" and not request.get_json(silent=True):
        return "OK", 200
    data = request.json or {}
    print(f"Webhook recibido: {list(data.keys())}")
    # Manejar eventos de estados (delivery, read) - solo loguear
    if "statuses" in data or "estados" in data:
        print(f"Evento de estado recibido: {data.get('statuses') or data.get('estados', [])}")
        return jsonify({"status": "ok"})
    # Manejar eventos de mensajes entrantes
    if "messages" not in data and "mensajes" not in data:
        print(f"Webhook sin clave 'messages/mensajes': {data}")
        return jsonify({"status": "ok"})
    try:
        msgs = data.get("messages") or data.get("mensajes")
        if not msgs:
            return jsonify({"status": "ok"})
        for msg in msgs:
            # Ignorar mensajes enviados por el bot
            if msg.get("from_me"):
                continue
            numero = msg.get("chat_id", "")
            # Obtener el texto del mensaje
            texto = ""
            if msg.get("type") == "text":
                texto = msg.get("text", {}).get("body", "")
            elif msg.get("type") == "link_preview":
                texto = msg.get("link_preview", {}).get("body", "")
            elif msg.get("type") in ("image", "video", "audio", "voice", "document"):
                texto = "[archivo multimedia]"
            if not texto:
                print(f"Mensaje sin texto: tipo={msg.get('type')}, chat_id={numero}")
                continue
            print(f"Mensaje recibido de {numero}: {texto[:50]}...")
            respuesta = procesar(texto, numero)
            enviar(numero, respuesta)
            print(f"Respuesta enviada a {numero}")
    except Exception as e:
        print(f"Error en webhook: {e}")
        import traceback
        traceback.print_exc()
    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def home():
    datos = cargar_datos()
    num_prod = len(datos.get("productos", []))
    return f"Bot Ferretería activo - {num_prod} productos cargados"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
