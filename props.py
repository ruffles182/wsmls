import mysql.connector
import datetime
from datetime import datetime, timedelta
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import googlemaps
from playwright.sync_api import sync_playwright

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
    mts_const = 0
    mts_lot = 0
    map_link = ""

    def __init__(self, code="", link="", name="", address="", neighborhood="", agent_link="", agent_name="", date_listed="", currency="", market_price="", type="", status="", mts_const=0, mts_lot=0, map_link=""):
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
        self.mts_const = mts_const
        self.mts_lot = mts_lot
        self.map_link = map_link
     
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

        # Define la consulta SQL
        query = ("INSERT INTO properties "
                "(code, link, name, address, neighboorhood, agent_link, agent_name, date_listed, currency, market_price, type, status, mts_const, mts_lot, map_link)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        # Validación y conversión de mts_lot y  mts_const


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

        # Define los datos a insertar
        datos = (self.code, self.link, self.name, self.address, self.neighboorhood, self.agent_link, self.agent_name, self.date_listed, self.currency, self.market_price, self.type, self.status, self.mts_const, self.mts_lot, self.map_link)

        # Ejecuta la consulta
        cursor.execute(query, datos)

        # Asegúrate de hacer commit para guardar los cambios
        cnx.commit()

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

def log_action(action_message, timestamp=None):
    timestamp = timestamp if timestamp else datetime.datetime.now()
    log_message = f"{timestamp}: {action_message}"

    with open('log.txt', 'a') as file:
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
def texto_correo_extractor():
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

def texto_correo_status_update(prop):
    texto = f"""
        <h1>Hola!!..</h1>
        <p>Han actualizado los datos de la siguiente propiedad</p>
        <div style='padding-top: 30px'>
            <h1><a href='{prop.link}'>{prop.code} - {prop.name}</a></h1>
            <p><b>Adress: </n>{prop.address}</p>
            <p><b>Price: {prop.currency}</b> <span style='color: #FF5D35'>$ {format(int(prop.market_price), ",")}</span></p>
            <p><b>Neighboorhood:</b>{prop.neighboorhood}</p>
        </div>
        <h2>Made by R84 :)</h2>
        """
    
    return texto


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
    query =  "SELECT code, link, name, address, neighboorhood, agent_link, agent_name, date_listed, currency, market_price, type, status, mts_const, mts_lot, map_link FROM properties WHERE code = %s"
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

def insert_status_change(code, status_id, price):
    cnn = mysql.connector.connect(user='tu_usuario', password='tu_contraseña', host='tu_host', database='tu_base_de_datos')
    cursor = cnn.cursor()

    # Primero, encontrar el property_id basado en el code
    query_property_id = "SELECT id FROM properties WHERE code = %s"
    cursor.execute(query_property_id, (code,))
    property_id = cursor.fetchone()[0]

    # Insertar el nuevo status_change
    insert_query = """
    INSERT INTO status_changes (status_id, property_id, price)
    VALUES (%s, %s, %s)
    """
    cursor.execute(insert_query, (status_id, property_id, price))
    cnn.commit()

    cursor.close()
    cnn.close()
    print("Registro insertado correctamente.")

def get_all_status_from_properties():
    conn = conectar()
    cursor = conn.cursor()

    query = """
    SELECT id,code,status, market_price FROM `properties`
    """
    
    cursor.execute(query)
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results
