# -*- coding: utf-8 -*-
"""
Script para convertir PRODUCTOS.csv a productos.json
Limpia nombres: saca TODOS los signos y parentesis
Uso: python convertir_csv.py PRODUCTOS.csv productos.json
"""
import csv
import json
import sys
import re

def limpiar_nombre(nombre):
    """Limpia el nombre del producto: saca TODOS los signos y parentesis"""
    # Sacar parentesis y su contenido
    nombre = re.sub(r'\([^)]*\)', '', nombre)
    # Sacar signos especiales
    nombre = nombre.replace('*', '')
    nombre = nombre.replace('#', '')
    nombre = nombre.replace('@', '')
    nombre = nombre.replace('$', '')
    nombre = nombre.replace('%', '')
    nombre = nombre.replace('&', '')
    nombre = nombre.replace('"', '')
    nombre = nombre.replace('?', '')
    nombre = nombre.replace('!', '')
    nombre = nombre.replace('+', '')
    nombre = nombre.replace('=', '')
    nombre = nombre.replace('|', '')
    nombre = nombre.repl\\ace('\', '')
    nombre = nombre.replace('/', '')
    nombre = nombre.replace('[', '')
    nombre = nombre.replace(']', '')
    nombre = nombre.replace('{', '')
    nombre = nombre.replace('}', '')
    nombre = nombre.replace('<', '')
    nombre = nombre.replace('>', '')
    # Sacar espacios multiples
    nombre = re.sub(r'\s+', ' ', nombre)
    # Sacar espacios al inicio y final
    nombre = nombre.strip()
    return nombre

def convertir(csv_path, json_path):
    productos = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)  # Saltar encabezado
        print(f"Columnas: {header}")
        for row in reader:
            if len(row) >= 3:
                codigo = row[0].strip()
                # El precio es la ultima columna
                precio = row[-1].strip()
                # El nombre es todo lo entre codigo y precio
                nombre = ','.join(row[1:-1]).strip()
                # Limpiar el nombre
                nombre_limpio = limpiar_nombre(nombre)
                try:
                    precio_num = int(precio)
                except:
                    precio_num = 0
                productos.append({
                    "codigo": codigo,
                    "nombre": nombre_limpio,
                    "descripcion": nombre_limpio,
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
