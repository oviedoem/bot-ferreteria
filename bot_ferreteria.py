#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Ferretería - WhatsApp Business Bot
Conecta con productos.json para consultas de productos y precios
"""

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
WHAPI_TOKEN = os.environ.get("WHAPI_TOKEN", "paZBDoXBHetA48viZxKc2KzAMnxnKpbH")  # Configura en Railway/Render
WHAPI_URL = "https://gate.whapi.cloud/messages/text"
# =========================================================

# Variables globales para cache de datos
datos_cache = None
ultima_carga = 0

def cargar_datos():
    """Carga datos de productos.json con manejo de errores"""
    global datos_cache, ultima_carga
    import time
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
    """Envia mensaje de texto via WHAPI"""
    if not numero or not texto:
        return
    headers = {"Authorization": f"Bearer {WHAPI_TOKEN}"}
    payload = {
        "chat_id": numero,
        "text": texto
    }
    try:
        resp = requests.post(WHAPI_URL, json=payload, headers=headers, timeout=10)
        print(f"Enviado a {numero}: {resp.status_code}")
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
            return f"No encontre '{busqueda}' en el catalogo.\nEscribe 'productos' para ver la lista completa o contactanos directamente."

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
            return f"No encontre el código '{codigo_busqueda}' en el catalogo."

    elif texto_lower in ("productos", "catalogo", "catálogo", "lista"):
        productos = datos.get("productos", [])[:50]
        resp = f"Catalogo ({len(datos.get('productos', []))} productos):\n"
        for p in productos:
            nombre = p.get("nombre", p.get("descripcion", "Sin nombre"))
            precio = p.get("precio", 0)
            codigo = p.get("codigo", "")
            if codigo:
                resp += f"\n- {codigo}: {nombre} -> ${precio:,}"
            else:
                resp += f"\n- {nombre} -> ${precio:,}"
        if len(datos.get("productos", [])) > 50:
            resp += "\n\nEscribe 'precio [nombre]' para buscar un producto especifico."
        return resp

    elif texto_lower in ("horario", "atencion", "atención"):
        horario = datos.get("horario", "Lunes a Viernes 09:00 - 18:00")
        return f"Horario de atencion:\n{horario}\n\n¿En que mas puedo ayudarte?"

    elif texto_lower in ("ubicacion", "direccion", "donde", "ubicación"):
        ubicacion = datos.get("ubicacion", "Las Cabras, Chile")
        return f"Te esperamos en:\n{ubicacion}\n\n¿Necesitas algo mas?"

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
            return f"No encontre '{busqueda}' en nuestro catalogo."

    else:
        return (
            "Gracias por escribirnos\n\n"
            "Puedo ayudarte con:\n"
            "- 'horario' -> Horario de atencion\n"
            "- 'productos' -> Catalogo de productos\n"
            "- 'precio [nombre]' -> Buscar precio\n"
            "- 'codigo [nro]' -> Buscar por codigo\n"
            "- 'ubicacion' -> Donde encontrarnos\n\n"
            "Para consultas especificas, un vendedor te respondera pronto."
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
    datos = cargar_datos()
    num_prod = len(datos.get("productos", []))
    return f"Bot Ferreteria activo - {num_prod} productos cargados"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
