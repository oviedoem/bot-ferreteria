# -*- coding: utf-8 -*-
"""
Script para convertir PRODUCTOS.csv a productos.json
Uso: python convertir_csv.py PRODUCTOS.csv productos.json
"""
import csv
import json
import sys

def convertir(csv_path, json_path):
    productos = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Saltar encabezado
        print(f"Columnas: {header}")
        for row in reader:
            if len(row) >= 3:
                codigo = row[0].strip()
                # El nombre puede contener comas, tomar todo entre codigo y precio
                precio = row[-1].strip()
                nombre = ','.join(row[1:-1]).strip()
                try:
                    precio_num = int(precio)
                except:
                    precio_num = 0
                productos.append({
                    "codigo": codigo,
                    "descripcion": nombre,
                    "precio": precio_num,
                    "stock": "disponible"
                })
                if len(productos) % 1000 == 0:
                    print(f"  {len(productos)} productos procesados...")
    
    resultado = {
        "horario": "Lunes a Viernes: 8:30 - 13:30 y 14:30 - 18:00\nSabado: 9:00 - 13:30\nDomingo: Cerrado",
        "ubicacion": "Carretera H66, km62, El Manzano, Las Cabras, Region de O'Higgins",
        "productos": productos
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print(f"Listo! {len(productos)} productos guardados en {json_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python convertir_csv.py PRODUCTOS.csv productos.json")
        sys.exit(1)
    convertir(sys.argv[1], sys.argv[2])
