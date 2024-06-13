import re
from colorama import Fore
import requests
from props import Propiedad

###############################################################################################
#funcion basica de scrappeo
def scrapCode(cont, patr):
    ## sacamos todas las apariciones de nuestro patron
    maquinas_repetidas = re.findall(patr, str(cont))
    ##removemos duplicados y devolvemos
    return list(set(maquinas_repetidas))

###############################################################################################
#extracion de datos del link
def linkExtraction(link_sin_formato):
    separador_id = link_sin_formato.rfind('-')
    id = link_sin_formato[separador_id+1:]
    separador_nombre = link_sin_formato.rfind('/')
    recortar_izquierda = link_sin_formato[separador_nombre+1:]

    nombre = recortar_izquierda[:-6].replace("-", " ")
    id = id

    return [id, nombre]
###############################################################################################
#lo siguiente puede ser una funcion de sacar ids, pensar si vale la pena en el futuro
#sitio
website = "https://www.chapalamls.net/en/properties/recently-added"
id_max_lengh = 4
separador_ids = "This Weeks Featured Properties"

#extraccion de codigo fuente
resultado = requests.get(website)
content = resultado.text.split(separador_ids, 1)[0]
#patron rgx
patron_ids = 'href="(/en/properties/.+?)"'

scrap_ids = scrapCode(content, patron_ids)

##preparamos lista para guardar ids
ids_propiedades = []
for f in scrap_ids:
    #guardamos todos los ids que sean numericos y de mas de cuatro caracteres
    cadena = f
    separador_id = cadena.rfind('-')
    id = cadena[separador_id+1:]
    if id.isdigit() and len(id) >= id_max_lengh: ids_propiedades.append(id)

###############################################################################################
#esta seria otra funcion para sacar bloques de  las propiedades
# haremos una lista de scrapt con la lista anterior que hicimos de ids
#lista que guardará los bloques de texto
bloques_propiedades = []
#archivo para debuggear la correcta salida de datos
archivo_dump = "output/salida.txt"
for id in ids_propiedades:
    delimitador_inicial = "id='"+ str(id) +"'>"
    delimitador_final = '<div class="col-xs-12 col-sm-12 col-md-12 col-lg-12">'
    patron_bloque = re.compile(r'{}(.*?){}'.format(re.escape(delimitador_inicial),re.escape(delimitador_final)),re.DOTALL)
    scrap_bloque = scrapCode(content, patron_bloque)
    bloques_propiedades.append(scrap_bloque)
file1 = open(archivo_dump, 'w')

###############################################################################################
#funcion donde filtramos los campos y los metemos a un objeto de tipo Propiedades
propiedades = []
n = 1
for bloque in bloques_propiedades:
    propiedad = Propiedad()
    precio_final = 0
    domicilio_final = ""
    moneda = ""
    id = 0
    #Scrap domicilio
    patron_domicilio = re.compile(r'<i class="fa fa-map-marker"></i>(.*?)</p>', re.DOTALL)
    scrap_domicilio = scrapCode(bloque, patron_domicilio)
    for domicilio in scrap_domicilio:
        espacio_izquierda = 24
        espacio_derecha = 20
        domicilio = domicilio[espacio_izquierda:]
        domicilio_final = domicilio[:-espacio_derecha]
        
    #scrap precio
    patron_precio = re.compile(r'<span class="price_original">(.*?)</span>', re.DOTALL)
    scrap_precio = scrapCode(bloque, patron_precio)
    for precio in scrap_precio:
        separador_precio = 32
        precio_izquierda = precio[separador_precio:]
        moneda = precio_izquierda[:3]
        precio_izquierda = precio_izquierda [10:]
        precio_final =  re.sub(r'\D', "", precio_izquierda)
    #buscamos el link
    scrap_link = scrapCode(bloque, patron_ids)
    link_seleccionado= ""
    for link in scrap_link:
        separador_id = link.rfind('-')
        id = link[separador_id+1:]
        if id.isdigit() and len(id) >= id_max_lengh: link_seleccionado = link
    if link_seleccionado != "":
        propiedad.link = link_seleccionado
        id_y_nombre = linkExtraction(propiedad.link)
        propiedad.id = id_y_nombre[0]
        propiedad.nombre = id_y_nombre[1]
        propiedad.moneda = moneda
        propiedad.precio = precio_final
        propiedad.direcion = domicilio_final
        # print(link)
        print(str(n) + ": con id - " + str(propiedad.id) + ' - ' + propiedad.nombre + 'con  precio de $' + propiedad.moneda + ' ' + propiedad.precio + ' hubicada en: ' + propiedad.direcion)
        n = n + 1
        

    file1.writelines('\n\n\n' +str(str(n) + ": con id - " + str(propiedad.id) + ' - ' + propiedad.nombre + " registrado################################################################"))
    file1.writelines(bloque)
    
file1.close()

###############################################################################################
