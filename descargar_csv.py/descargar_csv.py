# -*- coding: utf-8 -*-
"""
Script para descargar PRODUCTOS.csv desde OneDrive
"""
import requests
import base64
import time

# URL compartida de OneDrive
SHARE_URL = "https://1drv.ms/x/c/0997a298f38f1554/IQDTKITBKItUT7N61LmciS_tAbxxt2Zbx_apU49-e_J6qjA?e=DPIDd1"
OUTPUT_FILE = "PRODUCTOS.csv"

def descargar_onedrive():
    """Intenta descargar el CSV desde OneDrive usando varios metodos"""
    
    # Metodo 1: Usar la API de OneDrive con URL compartida codificada
    encoded_url = base64.b64encode(SHARE_URL.encode()).decode().rstrip('=').replace('/', '_').replace('+', '-')
    api_url = f"https://api.onedrive.com/v1.0/shares/u!{encoded_url}/root/content"
    
    print(f"Intentando descarga via API OneDrive...")
    print(f"URL API: {api_url}")
    
    try:
        response = requests.get(api_url, allow_redirects=True, timeout=60)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        print(f"Tamano: {len(response.content)} bytes")
        
        # Verificar si es HTML (error) o CSV
        content_type = response.headers.get('Content-Type', '')
        
        if 'text/html' in content_type or b'<html' in response.content[:100]:
            print("Respuesta es HTML, intentando metodo alternativo...")
            # Metodo 2: Probar URL directa con resid
            resid_url = "https://onedrive.live.com/download?resid=C18428D38B284F54B37AD4B99C892FED&authkey=!AQDTKITBKItUT7N6"
            response = requests.get(resid_url, allow_redirects=True, timeout=60)
            print(f"Intento 2 - Status: {response.status_code}")
            
        if response.status_code == 200 and len(response.content) > 1000:
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
            return True
        else:
            print(f"Descarga fallo. Status: {response.status_code}")
            print(f"Primeros 200 caracteres: {response.content[:200]}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    exit(0 if descargar_onedrive() else 1)
