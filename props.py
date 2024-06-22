import mysql.connector
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from conection import Conect
from conection import EmailData
from conection import Page

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
                "(code, link, name, address, neighboorhood, agent_link, agent_name, date_listed, currency, market_price, type, status, mts_const, mts_lot)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
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
        datos = (self.code, self.link, self.name, self.address, self.neighboorhood, self.agent_link, self.agent_name, self.date_listed, self.currency, self.market_price, self.type, self.status, self.mts_const, self.mts_lot)

        # Ejecuta la consulta
        cursor.execute(query, datos)

        # Asegúrate de hacer commit para guardar los cambios
        cnx.commit()

        cursor.close()
        cnx.close()
        return True
    
class EmailSend:
    email = ""
    receiver = ""
    subject = ""
    message = ""
    show_from = ''

    def send_email(self,sub,msg):
        edata = EmailData()
        self.email = (edata.email_sender)
        self.receiver = edata.email_receiver
        self.subject = sub
        self.message = msg
        self.show_from = edata.email_from

         # Crear un mensaje MIMEMultipart
        message = MIMEMultipart()
        message['From'] = self.show_from
        message['To'] = self.receiver
        message['Subject'] = self.subject

        # Asegúrate de que el tipo MIME es 'html'
        html_content = MIMEText(msg, 'html')
        message.attach(html_content)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(self.email, edata.app_password)
        server.send_message(message)
        server.quit()

        print('se envió el email a: ' + self.receiver)

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

def formato_link(cadena):
    pag = Page()
    return cadena + pag.web_format

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
                <div>
                    <h1>{propiedad.code}</h1>
                    <p><a href='{propiedad.link}'>{propiedad.name}</a></p>
                    <p><b>Adress: </n>{propiedad.address}</p>
                    <p><b>Price: {propiedad.currency}</b> <span style='color: #FF5D35'>$ {propiedad.price}</span></p>
                    <p><b>Neighboorhood:</b>{propiedad.neighboorhood}</p>
                </div>
        """
    return cadena_inicio + cadena_propiedades + cadena_final 


