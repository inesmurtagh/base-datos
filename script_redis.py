#! /usr/bin/env python3
import csv
import redis

# Conectar a Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Nombre del conjunto geoespacial en Redis
geo_key = 'bataxi'
print("Populando la base de datos redis...")
# Abre el archivo CSV
with open('bataxi.csv', mode='r', encoding='utf-8-sig') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        # Extrae los datos necesarios
        id = row['id_viaje_r']
        longitude = row['origen_viaje_x']
        latitude = row['origen_viaje_y']

        # Usa el comando GEOADD para añadir los datos
        r.geoadd(geo_key, (longitude, latitude, id))

print("Data geoespacial cargada en la base de datos.\n")

# Definir la lista de lugares
places = [
    {"place": "Parque Chas", "lon": -58.479258, "lat": -34.582497},
    {"place": "UTN", "lon": -58.468606, "lat": -34.658304},
    {"place": "ITBA Madero", "lon": -58.367862, "lat": -34.602938}
]

# Contar la cantidad de viajes a 1 km de distancia de cada lugar
total_nearby_trips = 0

for place in places:
    nearby_trips = r.georadius("bataxi", place["lon"], place["lat"], 1, unit='km')
    total_nearby_trips += len(nearby_trips)
    print(f"Se encontraron {len(nearby_trips)} viajes cercanos a {place['place']}")

print(f"Cantidad de viajes total a 1KM: {total_nearby_trips}\n")

# Cantidad de keys en redis
keys_qty = r.dbsize()
print("Claves totales: ", keys_qty, '\n')

# Cantidad de miembros de bataxi
members_qty = r.zcard('bataxi')
print("Claves dentro de bataxi: ", members_qty, '\n')

# Estructura de redis de geoadd
print("GEOADD usa un set ordenado.")
