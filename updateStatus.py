#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from props import EmailSend
from props import StatusChange
from props import log_action
from props import get_lowest_code_last_365_days
from props import check_code_status_price
from props import handle_result
from props import load_from_code
from props import texto_correo_status_update
from props import get_status_id_by_name
from props import insert_status_change

import datetime
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
#registro para log
propiedades_modificadas = []
#continuar buscando
continuar = True 
numero_pagina = 1
#variables guardar resultados
cambios_estado = []

log_action("inicializando status Updater", datetime.datetime.now(), 'update_status.log')
with sync_playwright() as p:
    if not islogin:
        pagina_actual = pagina_recientes + str(numero_pagina)
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_viewport_size({'width':939, 'height':720})
        page.goto(pagina_actual)


        usuario_input = page.get_by_placeholder("Username")
        if usuario_input is not None:
            log_action("iniciando sesión", datetime.datetime.now(), 'update_status.log')
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
        log_action('Sesion iniciada', datetime.datetime.now(), 'update_status.log')
    while continuar:
        pagina_actual = pagina_recientes + str(numero_pagina)
        page.goto(pagina_actual)
        time.sleep(15)
        html = page.inner_html('.container')
        soup = BeautifulSoup(html, 'html.parser')
        propiedades_bloque = soup.find_all('li', {'class': 'featured'})

        log_action("página actual: " + pagina_actual, datetime.datetime.now(), 'update_status.log')
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
            span_precio_raw = codigo_raw.find('span', class_='price')
            if (span_precio_raw is None):
                span_precio_raw = codigo_raw.find('span', class_='price_original')

            precio = 0
            moneda = ""
            try:
                span_precio = span_precio_raw.text.strip()
                precio = re.sub(r'[^\d]', '', str(span_precio))
                moneda = span_precio[:3]

            except:
                pass
            
            if tipo_propiedad in tipo_validado:
                #revisamos si hubo cambio de precio o de status
                caso = check_code_status_price(codigo, estatus, precio, moneda)
                #si cambio precio o estatus
                if (caso == 2 or caso== 3):
                    #mandamos log
                    log_action('UpdateStatus reporta: '+str(codigo) + ' - ' + handle_result(caso), datetime.datetime.now(), 'update_status.log')
                    #creamos una instancia de Propiedad con los datos de la bdd
                    prop = load_from_code(codigo)
                    # creamos una instancia de statusChange para manejar más facil los datos sin tener que usar '[0]'
                    sc = StatusChange(prop.status_id, prop.currency, prop.market_price, get_status_id_by_name(estatus), moneda, precio, prop.link, prop.code)
                    #agregamos este StatusChange a la lista para el envío de correo
                    cambios_estado.append(sc)
                    #creamos los status_changes y actualizamos los campos en properties
                    try:
                        insert_status_change(prop.code, get_status_id_by_name(estatus), precio, moneda, True)
                        log_action(f"haciendo try a {prop.code}, {get_status_id_by_name(estatus)}, {precio}, {moneda} ", None, "update_status.log")
                    except Exception as e:
                        log_action(f"error haciendo el status change en {prop.code}: {e}", datetime.datetime.now(), 'update_status.log')
                        log_action(f"haciendo try a {prop.code}, {get_status_id_by_name(estatus)}, {precio}, {moneda} ", None, "update_status.log")

            
            continuar = True if int(codigo) > int(ultimo_code) else False
            if not continuar:
                break
        
        log_action("terminado bloque " + str(numero_pagina) if continuar else 'se han revisado todas las propiedades', datetime.datetime.now(), 'update_status.log')
        numero_pagina = numero_pagina + 1
    
    # Enviar por correo la lista de propiedades con cambios de estado
    if (len(cambios_estado) > 0):
        correo = EmailSend()
        titulo = "Cambios de Status en propiedades"
        try:
            correo.send_email(titulo, texto_correo_status_update(cambios_estado))
        except Exception as e:
            log_action(f'ocurrió un problema al enviar el email: {e}', datetime.datetime.now(), 'update_status.log')

total_estado = len(cambios_estado)
log_action('status modificados: ' + str(len(cambios_estado)), datetime.datetime.now(), 'update_status.log')
log_action("terminado con éxito", datetime.datetime.now(), 'update_status.log')
