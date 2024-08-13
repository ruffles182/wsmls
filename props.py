import mysql.connector
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import googlemaps
from playwright.sync_api import sync_playwright

import subprocess
import datetime
from datetime import datetime
import os

from conection import Conect
from conection import EmailData
from conection import Page
from conection import apikeys

##Clase propiedad ######################################################################
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
    status_id = 0
    mts_const = 0
    mts_lot = 0
    map_link = ""

    def __init__(self, code="", link="", name="", address="", neighborhood="", agent_link="", agent_name="", date_listed="", currency="", market_price="", type="", status="", status_id=0, mts_const=0, mts_lot=0, map_link=""):
        self.code = code
        self.link = link
        self.name = name
        self.address = address
        self.neighborhood = neighborhood
        self.agent_link = agent_link
        self.agent_name = agent_name
        self.date_listed = date_listed
        self.currency = currency
        self.market_price = market_price
        self.type = type
        self.status = status
        self.status_id = status_id
        self.mts_const = mts_const
        self.mts_lot = mts_lot
        self.map_link = map_link

    def __repr__(self):
        return f"""
        {self.code} - {self.name}
        status: {self.status} - {self.status_id}
        """
     
    def simple_print(self):
        return str(self.code) + ' -> ' + self.name + ' - ' + str(self.date_listed) + ' - ' + str(self.currency) + ' - ' + str(self.market_price) + ' - ' + self.status


    def insertar_propiedad(self):
        con = Conect()
        # Crea una conexión a la base de datos
        cnx = mysql.connector.connect(user=con.user, password=con.password,
                                    host=con.host, database=con.db)

        cursor = cnx.cursor()

        # Verifica si el codigo ya existe
        cursor.execute("SELECT * FROM properties WHERE code = %s", (self.code,))
        if cursor.fetchone():
            # print(f"El codigo {self.code} ya existe en la base de datos.")
            return False
        
        # Fecha y hora actual
        fecha_hora_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Define la consulta SQL
        query = ("INSERT INTO properties "
                "(code, link, name, address, neighboorhood, agent_link, agent_name, date_listed, currency, market_price, type, status, status_id, mts_const, mts_lot, map_link, created_at, updated_at)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        

        #validamos que mts_lot no esté vacio
        if self.mts_lot is None:
            self.mts_lot = 0
        else:
            self.mts_lot = self.mts_lot

        try:
            self.mts_lot = float(self.mts_lot) if self.mts_lot else 0
        except ValueError:
            self.mts_lot = 0  # Asumir 0 si la conversión falla

        # Asumiendo que mts_const también necesita ser un número
        try:
            self.mts_lot = float(self.mts_lot) if self.mts_lot is not None and self.mts_lot != "" else 0
        except ValueError:
            self.mts_lot = 0


        #validamos que mts_const no esté vacio
        if self.mts_const is None:
            self.mts_const = 0
        else:
            self.mts_const = self.mts_const

        try:
            self.mts_const = float(self.mts_const) if self.mts_const else 0
        except ValueError:
            self.mts_const = 0  # Asumir 0 si la conversión falla

        # Asumiendo que mts_const también necesita ser un número
        try:
            self.mts_const = float(self.mts_const) if self.mts_const is not None and self.mts_const != "" else 0
        except ValueError:
            self.mts_const = 0

        try:
            self.status_id = get_status_id_by_name(self.status)
        except ValueError:
            print(f"error al recibir el status a status_id de la propiedad {self.code}")

        # Define los datos a insertar
        datos = (self.code, self.link, self.name, self.address, self.neighboorhood, self.agent_link, self.agent_name, self.date_listed, self.currency, self.market_price, self.type, self.status, self.status_id, self.mts_const, self.mts_lot, self.map_link, fecha_hora_actual, fecha_hora_actual)

        # Ejecuta la consulta
        cursor.execute(query, datos)
        
        # Asegúrate de hacer commit para guardar los cambios
        cnx.commit()
        
        #guardamos un nuevo statusChange
        id_status = get_status_id_by_name(self.status)
        insert_status_change(self.code,id_status, self.market_price, self.currency, False)

        cursor.close()
        cnx.close()
        return True

##Clase Email ##########################################################################################################
class EmailSend:
    email = ""
    receiver = ""
    subject = ""
    message = ""
    show_from = ''
    cc = ""

    def send_email(self,sub,msg):
        edata = EmailData()
        self.email = (edata.email_sender)
        self.receiver = edata.email_receiver
        self.subject = sub
        self.message = msg
        self.show_from = edata.email_from
        self.cc = edata.email_cc

         # Crear un mensaje MIMEMultipart
        message = MIMEMultipart()
        message['From'] = self.show_from
        message['To'] = self.receiver
        message['Subject'] = self.subject
        message['Cc'] = self.cc

        # Asegúrate de que el tipo MIME es 'html'
        html_content = MIMEText(msg, 'html')
        message.attach(html_content)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(self.email, edata.app_password)
        server.send_message(message,to_addrs=[self.receiver, self.cc])
        server.quit()

        print('se envió el email a: ' + self.receiver)


##Clase statusChange #######################################################################
class StatusChange():
    prev_status = 0
    prev_currency = ""
    prev_price = 0

    new_status = 0
    new_currency = ""
    new_price =0

    link = ""
    code = ""

    def __init__(self, prev_status = 0, prev_currency = "", prev_price = 0, new_status = 0, new_currency = "", new_price = 0, link ="", code = ""):
        
        self.prev_status = prev_status
        self.prev_currency = prev_currency
        self.prev_price = prev_price

        self.new_status = new_status
        self.new_currency = new_currency
        self.new_price = new_price

        self.link = link
        self.code = code
    def __repr__(self):
        return f"""
        {self.code} - {self.link}
        valores previos-> status: {self.prev_status} - {self.prev_currency} {self.prev_price} 
        valores nuevos-> status: {self.new_status} - {self.new_currency} {self.new_price}
        """

##Funciones ################################################################################
def conectar():
        con = Conect()
        conn = mysql.connector.connect(
            host=con.host,
            user=con.user,
            password=con.password,
            database=con.db
        )

        return conn

def guardar_en_archivo(texto, nombre_archivo="bloques.txt"):
    with open(nombre_archivo, "a") as archivo:
        archivo.write(texto)

def log_action(action_message, timestamp=None, file = 'log.txt'):
    timestamp = timestamp if timestamp else datetime.now()
    log_message = f"{timestamp}: {action_message}"

    with open(file, 'a') as file:
        file.write(log_message + '\n')
    print(log_message)

def formato_texto(cadena):
    return cadena.strip()

def formato_link(cadena):
    pag = Page()
    return pag.web_format + cadena

def texto_correo_extractor(propiedades):
    cantidad_propiedades = len(propiedades)
    cadena_propiedades = ""
    

    cadena_inicio = f"""
        <h1>Hola!!..</h1>
        <p>Se agregaron {cantidad_propiedades} registros nuevos</p>
    """

    cadena_final = "<h2>Made by R84 :)</r84>"

    for propiedad in propiedades:
        cadena_propiedades = cadena_propiedades + f"""
                <div style='padding-top: 30px'>
                    <h1><a href='{propiedad.link}'>{propiedad.code} - {propiedad.name}</a></h1>
                    <p><b>Adress: </n>{propiedad.address}</p>
                    <p><b>Price: {propiedad.currency}</b> <span style='color: #FF5D35'>$ {format(int(propiedad.market_price), ",")}</span></p>
                    <p><b>Neighboorhood:</b>{propiedad.neighboorhood}</p>
                </div>
        """
    return cadena_inicio + cadena_propiedades + cadena_final 
def texto_correo_extractor(propiedades):
    cantidad_propiedades = len(propiedades)
    cadena_propiedades = ""
    

    cadena_inicio = f"""
        <h1>Hola!!..</h1>
        <p>Se agregaron {cantidad_propiedades} registros nuevos</p>
    """

    cadena_final = "<h3>Made by R84 :)</h3>"

    for propiedad in propiedades:
        cadena_propiedades = cadena_propiedades + f"""
                <div style='padding-top: 30px'>
                    <h1><a href='{propiedad.link}'>{propiedad.code} - {propiedad.name}</a></h1>
                    <p><b>Adress: </n>{propiedad.address}</p>
                    <p><b>Price: {propiedad.currency}</b> <span style='color: #FF5D35'>$ {format(int(propiedad.market_price), ",")}</span></p>
                    <p><b>Neighboorhood:</b>{propiedad.neighboorhood}</p>
                </div>
        """
    return cadena_inicio + cadena_propiedades + cadena_final

def texto_correo_status_update(sc):
    cantidad_sc = len(sc)
    cadena_sc = ""

    

    cadena_inicio = f"""
        <h1>Hola!!..</h1>
        <p>Se modificaron {cantidad_sc} status de propiedades</p>
    """

    cadena_final = "<h3>Made by R84 :)</h3>"

    for cambio in sc:
        nombre_prev_status = get_status_name_by_id(cambio.prev_status)
        nombre_new_status = get_status_name_by_id(cambio.new_status)
        cadena_sc = cadena_sc + f"""
                <div style='padding-bottom: 15px'>
                    <div style='padding: 10px 10px 5px 5px'>
                        <h1><a href='{cambio.link}'>{cambio.code}</a></h1>
                        <p><b>Status anterior: </n>{nombre_prev_status}</p>
                        <p><b>Precio: {cambio.prev_currency}</b> <span style='color: #FF5D35'>$ {format(int(cambio.prev_price), ",")}</span></p>
                    </div>
                    <div style='padding: 10px 10px 5px 5px'>
                        <p><b>Status anterior: </n>{nombre_new_status}</p>
                        <p><b>Precio: {cambio.new_currency}</b> <span style='color: #FF5D35'>$ {format(int(cambio.new_price), ",")}</span></p>
                    </div>
                </div>
        """
    return cadena_inicio + cadena_sc + cadena_final


def check_empty_names(obj_list):
    return all(obj.name == "" for obj in obj_list)

def geolocalizar(direccion):
    ak = apikeys()
    # Reemplaza 'TU_CLAVE_API' con tu clave de API de Google
    gmaps = googlemaps.Client(key=ak.google_maps)

    # Reemplaza 'dirección aquí' con la dirección que deseas geocodificar
    direccion = direccion
    resultado = gmaps.geocode(direccion)

    coordenadas = []

    # Extrae las coordenadas
    lat = resultado[0]['geometry']['location']['lat']
    lng = resultado[0]['geometry']['location']['lng']

    coordenadas = '{"lat":' + str(lat) +',"lng":' + str(lng) + '}'

    return coordenadas

def get_first_code_by_year(year):
    conn = conectar()
    cursor = conn.cursor()
    query = f"SELECT code FROM properties WHERE YEAR(date_listed) = %s ORDER BY CAST(code AS UNSIGNED) ASC LIMIT 1"
    cursor.execute(query, (year,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_current_year():
    return datetime.now().year

def get_lowest_code_last_365_days():
    conn = conectar()
    cursor = conn.cursor()
    today = datetime.now()
    last_year_date = today - timedelta(days=365)
    query = "SELECT code FROM properties WHERE date_listed BETWEEN %s AND %s ORDER BY CAST(code AS UNSIGNED) ASC LIMIT 1"
    cursor.execute(query, (last_year_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def check_code_status_price(code, status, market_price, moneda):
    conn = conectar()
    cursor = conn.cursor()
    query = "SELECT status, market_price, currency FROM properties WHERE code = %s"
    cursor.execute(query, (code,))
    result = cursor.fetchone()
    conn.close()

    status_db = ""
    market_price_db = 0

    if result:
        status_db = result[0]
        market_price_db = result[1]
        moneda_db = result[2]


    if result is None:
        return 0  # "Code no existe en la base de datos"
    elif result[0] == status and int(result[1]) == int(market_price):
        return 1  # "Code existe y ambos campos son iguales"
    elif result[0] != status:
        print("mls: " + status + " - " + moneda + " " + str(market_price) + " ---- bdd: " + status_db + " - " + moneda_db + " " + str(market_price_db))
        return 2  # "Code existe pero el campo status ha cambiado"
    elif str(result[1]) != str(market_price):
        print("mls: " + status + " - " + moneda + " " + str(market_price) + " ---- bdd: " + status_db + " - " + moneda_db + " " + str(market_price_db))
        return 3  # "Code existe pero el campo market_price ha cambiado"
    
def handle_result(result):
    switcher = {
        0: "El código no existe en la base de datos.",
        1: "El código existe y ambos campos son iguales.",
        2: "El código existe pero el campo status ha cambiado.",
        3: "El código existe pero el campo listed_price ha cambiado."
    }
    return switcher.get(result, "Caso no definido")

def load_from_code(code):
    conn = conectar()
    cursor = conn.cursor()
    query =  "SELECT code, link, name, address, neighboorhood, agent_link, agent_name, date_listed, currency, market_price, type, status, status_id, mts_const, mts_lot, map_link FROM properties WHERE code = %s"
    cursor.execute(query, (code,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return Propiedad(*result)
    else:
        return None
    
def get_status_changes_by_property_code(code):
    conn = conectar()
    cursor = conn.cursor()

    query = """
    SELECT sc.price, sc.created_at, s.name, status_id, p.id
    FROM status_changes sc
    JOIN statuses s ON sc.status_id = s.id
    JOIN properties p ON sc.property_id = p.id
    WHERE p.code = %s
    ORDER BY sc.created_at DESC
    LIMIT 1
    """
    
    cursor.execute(query, (code,))
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results

def get_status_id_by_name(status_name):
    conn = conectar()
    cursor = conn.cursor()

    query = """
    SELECT id from statuses where name = %s
    LIMIT 1
    """
    
    cursor.execute(query, (status_name,))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if result:
        return str(result[0])
    else:
        return "No se encontró el ID para el estado dado."
        
def get_status_name_by_id(status_id):
    conn = conectar()
    cursor = conn.cursor()

    query = """
    SELECT name from statuses where id = %s
    LIMIT 1
    """
    
    cursor.execute(query, (status_id,))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if result:
        return str(result[0])
    else:
        return "No se encontró el nombre para el estado dado."

def insert_status_change(code, status_id, price, currency, actualizar):
    conn = conectar()
    cursor = conn.cursor()

    # Primero, encontrar el property_id basado en el code
    query_property_id = "SELECT id FROM properties WHERE code = %s"
    cursor.execute(query_property_id, (code,))
    property_id = cursor.fetchone()[0]
    # Fecha y hora actual
    fecha_hora_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insertar el nuevo status_change
    insert_query = """
    INSERT INTO status_changes (status_id, property_id, price, currency, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (status_id, property_id, price, currency, fecha_hora_actual, fecha_hora_actual))

    if (actualizar):
        # Actualizar properties
        update_query = """
        UPDATE properties
        SET status_id = %s, market_price = %s, currency = %s, updated_at = %s
        WHERE id = %s
        """
        cursor.execute(update_query, (status_id, price, currency, property_id, fecha_hora_actual))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Registro de status change: {code} insertado correctamente.")

def get_all_status_from_properties():
    conn = conectar()
    cursor = conn.cursor()

    query = """
    SELECT id,code,status, market_price, currency FROM `properties`
    """
    
    cursor.execute(query)
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results

def get_properties_id_by_code(property_code):
    conn = conectar()
    cursor = conn.cursor()

    query = """
    SELECT id from properties where code = %s
    LIMIT 1
    """
    
    cursor.execute(query, (property_code,))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if result:
        return str(result[0])
    else:
        return "No se encontró el ID para el estado dado."
    
def actualizar_status():
    conn = conectar()
    cursor = conn.cursor()

    # Seleccionar todos los registros de la tabla properties
    cursor.execute("SELECT id, status FROM properties")
    properties = cursor.fetchall()

    # Actualizar cada registro con el status_id correspondiente
    for prop in properties:
        status_id = get_status_id_by_name(prop[1])
        if status_id is not None:
            
            # Fecha y hora actual
            fecha_hora_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("UPDATE properties SET status_id = %s, updated_at=%s WHERE id = %s", (status_id, fecha_hora_actual, prop[0]))

    # Guardar los cambios
    conn.commit()

    # Cerrar la conexión
    cursor.close()
    conn.close()    

def realizar_backup(usuario, nombre_db, directorio_backup):
    # Crear el nombre del archivo basado en la fecha y hora actual
    fecha_hora = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    archivo_backup = f"{directorio_backup}/{fecha_hora}-back.sql"

    # Realizar el backup
    try:
        comando_backup = f"mysqldump -u {usuario} -p {nombre_db} > {archivo_backup}"
        subprocess.run(comando_backup, shell=True, check=True)
        log_action(f"Backup realizado con éxito en {archivo_backup}", None, "backupDB.log")
    except subprocess.CalledProcessError:
        log_action("Error al realizar el backup", None, "backupDB.log")

    # Eliminar archivos antiguos si hay más de 20
    try:
        # Listar los archivos en el directorio de backup
        archivos = sorted([f for f in os.listdir(directorio_backup) if f.endswith(".sql")])
        
        max_files = 120
        # Mantener solo los últimos 20 archivos
        if len(archivos) > max_files:
            while len(archivos) > max_files:
                os.remove(os.path.join(directorio_backup, archivos.pop(0)))
            log_action("Archivos antiguos eliminados correctamente.", None, "backupDB.log")
    except Exception as e:
        log_action(f"Error al eliminar archivos antiguos: {e}", None, "backupDB.log")
