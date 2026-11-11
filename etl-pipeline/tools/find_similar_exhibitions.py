import sqlite3
import Levenshtein
import csv

# Conecta con la base de datos
conn = sqlite3.connect('pathwise.db')
cursor = conn.cursor()

# Obtén todos los registros de la tabla "exposicion"
cursor.execute("SELECT id, nombre FROM exposicion")
registros = cursor.fetchall()

# Define un umbral para la similitud
umbral_similitud = 0.85  # Valores entre 0 y 1, donde 1 es idéntico

# Encuentra nombres similares (sin diferenciar entre mayúsculas y minúsculas)
nombres_similares = []
for i in range(len(registros)):
    for j in range(i + 1, len(registros)):
        nombre1 = registros[i][1]
        nombre2 = registros[j][1]
        similitud = Levenshtein.ratio(nombre1, nombre2)
        if similitud >= umbral_similitud:
            nombres_similares.append((registros[i][0], registros[i][1], registros[j][0], registros[j][1], similitud))

# Guarda los resultados en un archivo CSV con UTF-8 con BOM
with open('nombres_similares_exposiciones.csv', mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file, delimiter=';')  # Cambiamos el delimitador a ';'
    writer.writerow(['ID_1', 'Nombre_1', 'ID_2', 'Nombre_2', 'Similitud'])  # Cabeceras
    for registro1_id, nombre1, registro2_id, nombre2, similitud in nombres_similares:
        writer.writerow([registro1_id, nombre1, registro2_id, nombre2, f'{similitud:.2f}'])

# Cierra la conexión
conn.close()

print("Los resultados han sido guardados en 'nombres_similares_exposiciones.csv'")
