import mysql.connector
import datetime
from conection import Conect

class Propiedad:
    code = ""
    link = ""
    name = ""
    address = ""
    neighboorhood = ""
    agent_link = ""
    agent_name = ""
    date_listed = ""
    currency = ""
    market_price = ""
    type = ""
    status = ""
    mts_const = 0
    mts_lot = 0

    def simple_print(self):
        return str(self.code) + ' -> ' + self.name + ' - ' + str(self.date_listed) + ' - ' + str(self.currency) + ' - ' + str(self.market_price) + ' - ' + self.status'


    def insertar_propiedad(self):
        con = Conect()
        # Crea una conexión a la base de datos
        cnx = mysql.connector.connect(user=con.user, password=con.password,
                                    host=con.host, database=con.db)

        cursor = cnx.cursor()

        # Verifica si el codigo ya existe
        cursor.execute("SELECT * FROM properties WHERE code = %s", (self.code,))
        if cursor.fetchone():
            print(f"El codigo {self.code} ya existe en la base de datos.")
            return "no"

        # Define la consulta SQL
        query = ("INSERT INTO properties "
                "(code, link, name, address, neighboorhood, agent_link, agent_name, date_listed, currency, market_price, type, status, mts_const, mts_lot)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        #validamos que mts_lot no esté vacio
        if not isinstance(self.mts_lot, (int, float)) or self.mts_lot is None:
            self.mts_lot = 0
        else:
            self.mts_lot = self.mts_lot

        # Define los datos a insertar
        datos = (self.code, self.link, self.name, self.address, self.neighboorhood, self.agent_link, self.agent_name, self.date_listed, self.currency, self.market_price, self.type, self.status, self.mts_const, self.mts_lot)

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

