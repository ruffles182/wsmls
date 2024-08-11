#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from props import EmailSend
from props import log_action
from props import texto_correo_extractor
from props import check_empty_names
from props import get_lowest_code_last_365_days
from props import check_code_status_price
from props import handle_result
from props import load_from_code
from props import texto_correo_status_update
from props import get_status_changes_by_property_code
from props import get_status_id_by_name
from props import get_status_name_by_id


from conection import Page

import re
import time

#login
islogin = False
#página
pagina_recientes = Page.web
#tipos validos
tipo_validado = ['Residential', 'Land and Lots', 'Commercial']
#Anio en curso
ultimo_code = get_lowest_code_last_365_days()
print(ultimo_code)
#registro para log
propiedades_modificadas = []
#continuar buscando
continuar = True 
numero_pagina = 1
#variables guardar resultados
cambios_estado = []

print("inicializando status Updater")
with sync_playwright() as p:
    if not islogin:
        pagina_actual = pagina_recientes + str(numero_pagina)
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_viewport_size({'width':939, 'height':720})
        page.goto(pagina_actual)


        usuario_input = page.get_by_placeholder("Username")
        if usuario_input is not None:
            print("iniciando sesión")
            page.wait_for_load_state('load')
            page.locator("#btl-panel-login").click()
            time.sleep(3)
            
            page.fill('input#btl-input-username', Page.usr)
            page.fill('input#btl-input-password', Page.pwd)
            page.locator("#btl-checkbox-remember").click()
            page.click('input[value="Log in"]')
            page.wait_for_load_state('load')
            
            time.sleep(5)
            islogin = True
        print('Sesion iniciada')
    while continuar:
        pagina_actual = pagina_recientes + str(numero_pagina)
        page.goto(pagina_actual)
        time.sleep(15)
        html = page.inner_html('.container')
        soup = BeautifulSoup(html, 'html.parser')
        propiedades_bloque = soup.find_all('li', {'class': 'featured'})

        print("página actual: " + pagina_actual)
        for bloque in propiedades_bloque:
            #campo código extract
            codigo_raw = BeautifulSoup(str(bloque), 'html.parser')
            codigo = codigo_raw.find('li', {'class': 'featured'}).get('id')
            #campo estatus
            div_estatus = bloque.find('div', class_='min_height_20 type-value')
            estatus = div_estatus.get_text(strip = True)
            #Tipo de propiedad
            div_tipo_propiedad = codigo_raw.find('a', class_='text-secondary')
            tipo_propiedad = div_tipo_propiedad.text.strip()
            #price
            span_precio_raw = codigo_raw.find('span', class_='price_original')
            precio = 0
            moneda = ""
            try:
                span_precio = span_precio_raw.text.strip()
                precio = re.sub(r'[^\d]', '', str(span_precio))
                moneda = span_precio[:3]
            except:
                pass

            print("Revisando propiedad " + codigo)
            
            if tipo_propiedad in tipo_validado:
                #revisamos si hubo cambio de precio o de status
                caso = check_code_status_price(codigo, estatus, precio, moneda)
                #registramos en el log
                if (caso == 2 or caso== 3):
                    print('UpdateStatus reporta: '+str(codigo) + ' - ' + handle_result(caso))

            
            continuar = True if int(codigo) > int(ultimo_code) else False
            if not continuar:
                break
        # Enviar por correo la lista de propiedades con cambios de estado
        correo = EmailSend()
        titulo = "Cambios de Status en propiedades"
        try:
            correo.send_email(titulo, texto_correo_status_update())
        except Exception as e:
            print(f'ocurrió un problema al enviar el email: {e}')
        
        print("terminado bloque " + str(numero_pagina) if continuar else 'se han revisado todas las propiedades')
        numero_pagina = numero_pagina + 1

total_estado = len(cambios_estado)
print('status modificados: ' + str(len(cambios_estado)))
print("terminado con éxito")
