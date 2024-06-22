# Trabajo Práctico Obligatorio

Fecha de Entrega: 19 de junio de 2024

_Repositorio de Datasets [en este link](https://l1nk.dev/aTrRE)_

## Integrantes

- Luciano Neimark (62086)
- Paz Aramburu (62556)
- Inés Murtagh (61759)

---

### Ejercicio 1 - MongoDB

Para este ejercicio, se utilizará la base de datos MongoDB. Se deberá realizar una conexión desde Docker a MongoDB.
Para ello, ejecutar los siguientes comandos:

```bash
docker pull mongo
docker run --name Mymongo -p 27017:27017 -d mongo
```

Copiar el archivo `albumlist.csv` al contenedor de MongoDB y acceder al mismo, para luego importar el archivo CSV a MongoDB:

```bash
docker cp albumlist.csv Mymongo:/albumlist.csv
docker exec -it Mymongo bash
mongoimport --headerline --db tpo --collection albumlist --type csv --file /albumlist.csv
```

El comando mongoimport crea la base de datos y la colección especificadas si no existen. Esto significa que en este caso, como 'tpo' no existe y la colección 'albumlist' tampoco, mongoimport las creará automáticamente durante la importación.

Finalmente, para ejecutar las consultas necesarias, se debe acceder y utilziar el shell de MongoDB (`mongosh`):

```bash
mongosh
use tpo  # conectar a la base de datos 'tpo'
```

En el siguiente código se resolvieron los ejercicios:

```bash
# A. Contar la cantidad de álbumes por año y ordenarlos de manera descendente
db.albumlist.aggregate([
    { "$group": { "_id": "$Year", "count": { "$sum": 1 } } },
    { "$sort": { "count": -1 } }
])

# B. Agregar un nuevo atributo 'score' a cada documento
db.albumlist.updateMany({}, [
    { "$set": { "score": { "$subtract": [501, "$Number"] } } }
])

# C. Mostrar el 'score' de cada artista (se asume score como la suma de los scores por album)
db.albumlist.aggregate([
    { $group: { _id: "$Artist", total_score: { $sum: "$score" } } },
    { $project: { _id: 0, artist: "$_id", total_score: 1 } },
    { $sort: { total_score: -1 } }
])
```

A continuación se dejan los resultados de la ejecucuión:

**Ejercicio A**
(se muestran solo las primeras 5 filas de resultado)

```
{
  _id: 1970,
  count: 26
}
{
  _id: 1972,
  count: 24
}
{
  _id: 1973,
  count: 23
}
{
  _id: 1969,
  count: 22
}
{
  _id: 1968,
  count: 21
}
```

**Ejercicio B**

```
{
  acknowledged: true,
  insertedId: null,
  matchedCount: 500,
  modifiedCount: 500,
  upsertedCount: 0
}
```

**Ejercicio C**
(se muestran solo las primeras 5 filas de resultado)

```
{
  total_score: 3855,
  artist: 'The Beatles'
}
{
  total_score: 3604,
  artist: 'The Rolling Stones'
}
{
  total_score: 3377,
  artist: 'Bob Dylan'
}
{
  total_score: 2251,
  artist: 'Bruce Springsteen'
}
{
  total_score: 2210,
  artist: 'The Who'
}
```

---

### Ejercicio 2 - Neo4j

Se requiere inicializar un sandbox de Neo4j en https://sandbox.neo4j.com/
Luego de popular la base de datos (como se especifica en la consigna) se ejecutan las siguientes consultas:

Query 1: ¿Cuántos productos hay en la base?

```
match (p:Product) return count(p)
```

Salida: 77

Query 2: ¿Cuánto cuesta el “Queso Cabrales”?

```
match (p:Product) where (p.productName = 'Queso Cabrales') return p.unitPrice
```

Salida: 21.0

Query 3: ¿Cuántos productos pertenecen a la categoría “Condiments”?

```
match (p:Product)-[r:PART_OF]->(c:Category {categoryName: 'Condiments'}) return count(p)
```

Salida: 12

Query 4: Del conjunto de productos que ofrecen los proveedores de “UK”, ¿Cuál es el
nombre y el precio unitario de los tres productos más caros?

```
match (s:Supplier {country:'UK'})-[:SUPPLIES]->(p:Product)
return p.productName, p.unitPrice
order by p.unitPrice DESC
limit 3
```

Salida:
| p.productName | p.unitPrice |
| ------------- |:-------------:|
| Chang | 19.0 |
| Chai | 18.0 |
| Anissed Syrup | 10.0 |

---

### Ejercicio 3 - Redis

Para este ejercicio, se utilizará la base de datos Redis. Se deberá realizar una conexión desde docker a redis. Para ello ejecutar los siguientes comandos:

```bash
docker pull redis
docker run --name Myredis -p 6379:6379 -d redis
```

Copiar los archivos bataxi.csv y script_redis.py al contenedor de redis:

```bash
docker cp bataxi.csv Myredis:/bataxi.csv
docker cp script_redis.py Myredis:/script_redis.py
docker exec -it Myredis bash
```

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

#Se asume como la union.
print(f"Cantidad de viajes total a 1KM: {total_nearby_trips}\n")

# Cantidad de keys en redis
keys_qty = r.dbsize()
print("Claves totales: ", keys_qty, '\n')

# Cantidad de miembros de bataxi
members_qty = r.zcard('bataxi')
print("Claves dentro de bataxi: ", members_qty, '\n')

# Estructura de redis de geoadd
print("GEOADD usa un set ordenado.")
```

y sus respectivos resultados fueron:

```
Populando la base de datos redis...
Data geoespacial cargada en la base de datos.

Se encontraron 339 viajes cercanos a Parque Chas
Se encontraron 9 viajes cercanos a UTN
Se encontraron 242 viajes cercanos a ITBA Madero
Cantidad de viajes total a 1KM: 590

Claves totales:  1

Claves dentro de bataxi:  19148

GEOADD usa un set ordenado.
```
