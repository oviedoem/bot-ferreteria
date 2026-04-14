# -*- coding: utf-8 -*-
"""Descarga PRODUCTOS.csv desde OneDrive usando el API publico de OneDrive"""
import base64
import urllib.request
import sys

# URL de compartir de OneDrive (publica)
SHARE_URL = "https://1drv.ms/x/c/0997a298f38f1554/IQDTKITBKItUT7N61LmciS_tAbyxt2Zby_apU49-e_J6qjA?e=he8jxe"
OUTPUT_FILE = "PRODUCTOS.csv"

def download():
    # Codificar la URL para el API de OneDrive
    encoded = base64.urlsafe_b64encode(SHARE_URL.encode()).rstrip(b'=').decode()
    api_url = f"https://api.onedrive.com/v1.0/shares/u!{encoded}/root/content"
    print(f"Descargando desde: {api_url}")
    
    headers = {"Accept": "*/*"}
    req = urllib.request.Request(api_url, headers=headers)
    
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    
    with open(OUTPUT_FILE, "wb") as f:
        f.write(data)
    
    print(f"Descargado: {len(data)} bytes")
    return len(data)

if __name__ == "__main__":
    try:
        size = download()
        if size == 0:
            print("ERROR: Archivo vacio")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
