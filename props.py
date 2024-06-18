import mysql.connector
import datetime
from conection import Conect

class Propiedad:
    codigo = ""
    link = ""
    nombre = ""
    direcion = ""
    precio = 0
    moneda = ""
    tipo = ""
    estatus = ""
    region = ""

    def simple_print(self):
        return str(self.codigo) + ' - ' + self.nombre + ' -> ' + self.link 


    def insertar_propiedad(self):
        con = Conect()
        # Crea una conexión a la base de datos
        cnx = mysql.connector.connect(user=con.user, password=con.password,
                                    host=con.host, database=con.db)

        cursor = cnx.cursor()

        # Verifica si el codigo ya existe
        cursor.execute("SELECT * FROM propiedads WHERE codigo = %s", (self.codigo,))
        if cursor.fetchone():
            print(f"El codigo {self.codigo} ya existe en la base de datos.")
            return "no"

        # Define la consulta SQL
        query = ("INSERT INTO propiedads "
                "(direccion, nombre, codigo, precio, moneda) "
                "VALUES (%s, %s, %s, %s, %s)")

        # Define los datos a insertar
        datos = (self.direcion, self.nombre, self.codigo, self.precio, self.moneda)

        # Ejecuta la consulta
        cursor.execute(query, datos)

        # Asegúrate de hacer commit para guardar los cambios
        cnx.commit()

        cursor.close()
        cnx.close()
        return "si"

def guardar_en_archivo(texto, nombre_archivo="bloques.txt"):
    with open(nombre_archivo, "a") as archivo:
        archivo.write(texto)

def log_action(action_message, timestamp=None):
    timestamp = timestamp if timestamp else datetime.datetime.now()
    log_message = f"{timestamp}: {action_message}"

    with open('log.txt', 'a') as file:
        file.write(log_message + '\n')

def formato_texto(cadena):
    return cadena.strip()

