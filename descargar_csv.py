# -*- coding: utf-8 -*-
"""Descarga PRODUCTOS.csv desde OneDrive usando la API publica de OneDrive"""
import requests
import base64
import sys

# URL compartida de OneDrive (publica)
SHARE_URL = "https://1drv.ms/x/c/0997a298f38f1554/IQDTKITBKItUT7N61LmciS_tAbxxt2Zbx_apU49-e_J6qjA?e=DPIDd1"
OUTPUT_FILE = "PRODUCTOS.csv"

def download():
    # Codificar la URL para la API de OneDrive
    encoded = base64.urlsafe_b64encode(SHARE_URL.encode()).rstrip(b'=').decode()
    api_url = f"https://api.onedrive.com/v1.0/shares/u!{encoded}/root/content"
    print(f"Descargando desde: {api_url}")
    
    try:
        response = requests.get(api_url, allow_redirects=True, timeout=120)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        print(f"Tamano: {len(response.content)} bytes")
        
        # Verificar si es HTML (error) o CSV
        content_type = response.headers.get('Content-Type', '')
        
        if 'text/html' in content_type or b'<html' in response.content[:100]:
            print("ERROR: Respuesta es HTML, la URL compartida puede no ser valida o requiere autenticacion")
            return 0
        
        with open(OUTPUT_FILE, 'wb') as f:
            f.write(response.content)
        
        print(f"Descarga exitosa! Archivo guardado como {OUTPUT_FILE}")
        print(f"Tamano: {len(response.content)} bytes")
        
        # Mostrar primeras lineas
        contenido = response.content.decode('utf-8', errors='ignore')
        lineas = contenido.split('\n')[:5]
        print("Primeras lineas:")
        for linea in lineas:
            print(f"  {linea[:100]}")
        
        return len(response.content)
    except Exception as e:
        print(f"ERROR: {e}")
        return 0

if __name__ == "__main__":
    try:
        size = download()
        if size == 0:
            print("ERROR: Archivo vacio o descarga fallida")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
