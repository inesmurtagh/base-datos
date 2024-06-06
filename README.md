# Trabajo Práctico Obligatorio
Fecha de Entrega: 19 de junio de 2024

## Integrantes
- Luciano Neimark
- Paz Aramburu
- Inés Murtagh

*Repositorio de Datasets: * 
[en este link](https://l1nk.dev/aTrRE)

---

### Ejercicio 1 - MongoDB
Para este ejercicio, se utilizará la base de datos MongoDB. Se deberá realizar una conexión desde Docker a MongoDB. Para ello, ejecutar los siguientes comandos:

```bash
docker pull mongo
docker run --name Mymongo -p 27017:27017 -d mongo


### Ejercicio 1 - MongoDB
Para este ejercicio, se utilizará la base de datos MongoDB. Se deberá realizar una conexión desde Docker a MongoDB. 
Para ello, ejecutar los siguientes comandos:

```bash
docker pull mongo
docker run --name Mymongo -p 27017:27017 -d mongo
```

Copiar el archivo `albumlist.csv` al contenedor de MongoDB:

```bash
docker cp albumlist.csv Mymongo:/albumlist.csv
docker exec -it Mymongo bash
```

Luego, importar el archivo CSV a MongoDB y ejecutar las consultas necesarias. Para ello, hay que acceder al contenedor de MongoDB y utilizar el shell de MongoDB (`mongosh`):

```bash
# Acceder al contenedor MongoDB
docker exec -it Mymongo bash

# Importar el archivo CSV a MongoDB
mongoimport --headerline --db tpo --collection albumlist --type csv --file /albumlist.csv

# Acceder al shell de MongoDB
mongosh

# Conectar a la base de datos 'tpo'
use tpo
```

```bash
# 1. Contar la cantidad de álbumes por año y ordenarlos de manera descendente
db.albumlist.aggregate([
    { "$group": { "_id": "$Year", "count": { "$sum": 1 } } },
    { "$sort": { "count": -1 } }
])

# 2. Agregar un nuevo atributo 'score' a cada documento
db.albumlist.updateMany({}, [
    { "$set": { "score": { "$subtract": [501, "$Number"] } } }
])

# 3. Mostrar el 'score' de cada artista
db.albumlist.aggregate([
    { $group: { _id: "$Artist", total_score: { $sum: "$score" } } },
    { $project: { _id: 0, artist: "$_id", total_score: 1 } },
    { $sort: { total_score: -1 } }
])
```


### Ejercicio 3 - Redis
Para este ejercicio, se utilizará la base de datos Redis. Se deberá realizar una conexión desde docker a redis. Para ello ejecutar los siguientes comandos:
    
```bash
docker pull redis
docker run --name Myredis -p 6379:6379 -d redis
```
Copiar los archivos bataxi.csv y script_redis.py al contenedor de redis:
        
```bash
docker cp bataxi.csv <id_container>:/bataxi.csv
docker cp script_redis.py <id_container>:/script_redis.py
docker exec -it Myredis bash
```

siendo `<id_container>` el id del contenedor de redis.

Luego, ejecutar el script de python en el contenedor. Para ello, hay que tener instalado python3 en el contenedor y la dependencia de redis:
```bash
cd ..
apt-get update
apt-get install python3
apt-get install python3-redis
```
Ejecutar el script:
```bash
./script_redis.py
```

#### Script y resultados
En el siguiente script se resolvieron los ejercicios
```python
#! /usr/bin/env python3
import csv
import redis

r = redis.Redis(host='localhost', port=6379, db=0)
geo_key = 'bataxi'
print("Adding data to redis...")
# a. Importar los datos del archivo a Redis
with open('bataxi.csv', mode='r', encoding='utf-8-sig') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        id = row['id_viaje_r']
        longitude = row['origen_viaje_x']
        latitude = row['origen_viaje_y']
        r.geoadd(geo_key, (longitude, latitude, id))

print("Geospacial data added to Redis.\n")

# b. ¿Cuántos viajes se generaron a 1 km de distancia de estos 3 lugares?
places = [
    {"place": "Parque Chas", "lon": -58.479258, "lat": -34.582497},
    {"place": "UTN", "lon": -58.468606, "lat": -34.658304},
    {"place": "ITBA Madero", "lon": -58.367862, "lat": -34.602938}
]

total_nearby_trips = 0

for place in places:
    nearby_trips = r.georadius("bataxi", place["lon"], place["lat"], 1, unit='km')
    total_nearby_trips += len(nearby_trips)
    print(f"Found {len(nearby_trips)} trips near {place['place']}")

print(f"Total trips within 1 km of the places: {total_nearby_trips}\n")

# c. ¿Cuántas KEYS hay en la base de datos Redis?
keys_qty = r.dbsize()
print("Total keys in redis: ", keys_qty, '\n')

# d. ¿Cuántos miembros tiene la key 'bataxi'?
members_qty = r.zcard('bataxi')
print("Total members in bataxi: ", members_qty, '\n')

# e. ¿Sobre qué estructura de Redis trabaja el GeoADD?
print("GEOADD uses a sorted set")
```

y sus respectivos resultados fueron:
```
Adding data to redis...
Geospacial data added to Redis.

Found 339 trips near Parque Chas
Found 9 trips near UTN
Found 242 trips near ITBA Madero
Total trips within 1 km of the places: 590

Total keys in redis:  1 

Total members in bataxi:  19148 

GEOADD uses a sorted set
```
