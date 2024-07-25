import mysql.connector
from conection import Conect
from props import log_action
from props import geolocalizar

# Establece la conexión con la base de datos
con = Conect()
conexion = mysql.connector.connect(
    host = con.host,
    user = con.user,
    password = con.password,
    database = con.db
)

cursor = conexion.cursor()

# Ejecuta la consulta
cursor.execute("SELECT id, address, code FROM properties WHERE address IS NOT NULL AND address != '' AND (map_link IS NULL OR map_link = '');")

# Guarda los resultados en una lista
resultados = cursor.fetchall()

log_action(f"se encontraron: {len(resultados)} propiedades sin mapa actualizado")

for resultado in resultados:

    # Conexión a la base de datos
    conexion = mysql.connector.connect(
        host = con.host,
        user = con.user,
        password = con.password,
        database = con.db
    )

    cursor = conexion.cursor()
    # Prepara la sentencia SQL para actualizar el campo map_link
    id_propiedad = resultado[0]

    coordenadas = geolocalizar(resultado[1])

    query = f"UPDATE properties SET map_link = %s WHERE id = %s;"

    # Ejecuta la consulta
    cursor.execute(query, (coordenadas, id_propiedad))

    # Confirma los cambios
    conexion.commit()

    # Cierra el cursor y la conexión
    cursor.close()
    conexion.close()

    log_action(f"se agregó geolocalización a la propiedad {resultado[2]}")