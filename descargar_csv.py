# -*- coding: utf-8 -*-
"""Descarga PRODUCTOS.csv desde OneDrive usando URL directa de descarga"""
import requests
import sys

OUTPUT_FILE = "PRODUCTOS.csv"

def download():
    # URL compartida de OneDrive con parametro download=1
    # Esta URL funciona desde GitHub Actions sin autenticacion
    share_url = "https://1drv.ms/x/c/0997a298f38f1554/IQDTKITBKItUT7N61LmciS_tAbxxt2Zbx_apU49-e_J6qjA?e=IM7Cjn"
    
    # URL de descarga directa con &download=1
    # Esta URL redirige al endpoint de descarga de OneDrive
    download_url = "https://1drv.ms/x/c/0997a298f38f1554/IQDTKITBKItUT7N61LmciS_tAbxxt2Zbx_apU49-e_J6qjA?e=IM7Cjn&download=1"
    
    print(f"Intentando descargar desde: {download_url}")
    
    try:
        response = requests.get(download_url, allow_redirects=True, timeout=120)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        print(f"Tamano: {len(response.content)} bytes")
        
        if response.status_code != 200:
            print(f"ERROR: Status {response.status_code}")
            return 0
        
        content_type = response.headers.get('Content-Type', '').lower()
        if 'html' in content_type or 'json' in content_type:
            text = response.text[:300]
            if 'error' in text.lower() or 'login' in text.lower() or '<html' in text.lower():
                print(f"ERROR: Respuesta no es CSV. Contenido: {text[:200]}")
                return 0
        
        with open(OUTPUT_FILE, 'wb') as f:
            f.write(response.content)
        
        print(f"Descarga exitosa! Archivo guardado como {OUTPUT_FILE}")
        print(f"Tamano: {len(response.content)} bytes")
        
        content = response.content.decode('utf-8', errors='ignore')
        lines = content.split('\n')[:5]
        print("Primeras lineas:")
        for line in lines:
            print(f"  {line[:100]}")
        
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
        print(f"ERROR CRITICO: {e}")
        sys.exit(1)
