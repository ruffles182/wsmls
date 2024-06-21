#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from props import Propiedad
from props import guardar_en_archivo
from props import formato_texto
from props import log_action

from conection import Page

from datetime import datetime, timedelta
import re
import time
import sys

pagina_recientes = Page.web
tipo_validado = ['Residential', 'Land and Lots', 'Commercial']
repeticiones = 1

if len(sys.argv) > 1:
    repeticiones = int(sys.argv[1])

propiedades_agregadas = []

ahora = datetime.now()
fecha_hora = ahora.strftime("%Y-%m-%d %H:%M:%S")
print(fecha_hora)
for numero_pagina in range(repeticiones):
    pagina_recientes = pagina_recientes + str(numero_pagina+1)
    print(pagina_recientes)
    print('iteracion ' + str(numero_pagina + 1) + " de: " + str(repeticiones))

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_viewport_size({'width':939, 'height':720})
        page.goto(pagina_recientes)


        usuario_input = page.get_by_placeholder("Username")
        if usuario_input is not None:
            print("iniciando sesión")
            log_action("iniciando sesión")
            page.wait_for_load_state('load')
            page.locator("#btl-panel-login").click()
            time.sleep(3)
            
            page.fill('input#btl-input-username', Page.usr)
            page.fill('input#btl-input-password', Page.pwd)
            page.locator("#btl-checkbox-remember").click()
            page.click('input[value="Log in"]')
            page.wait_for_load_state('load')
            
            time.sleep(5)

        print('Sesion iniciada')
        log_action("sesion iniciada")
        page.goto(pagina_recientes)
        time.sleep(5)
        html = page.inner_html('.container')
        soup = BeautifulSoup(html, 'html.parser')
        propiedades_bloque = soup.find_all('li', {'class': 'featured'})

        for bloque in propiedades_bloque:
            propiedad = Propiedad()

            #campo código extract
            codigo_raw = BeautifulSoup(str(bloque), 'html.parser')
            codigo = codigo_raw.find('li', {'class': 'featured'}).get('id')
            #campo estatus
            div_estatus = bloque.find('div', class_='min_height_20 type-value')
            estatus = div_estatus.get_text(strip = True)
            #Tipo de propiedad
            div_tipo_propiedad = codigo_raw.find('a', class_='text-secondary')
            tipo_propiedad = div_tipo_propiedad.text.strip()
            #campo días en el mercado
            div_dias_en_mercado = ''
            div_dias_en_mercado = codigo_raw.find('div', class_='type-value min_height_20', string=re.compile("Days"))
            dias_en_mercado = 0
            try:
                dias_en_mercado = div_dias_en_mercado.get_text(strip=True)
                dias_en_mercado = dias_en_mercado.replace("Days", "")
                dias_en_mercado = formato_texto(dias_en_mercado).strip()
            except:
                pass
            #fecha de publicación
            hoy = datetime.now()
            fecha_publicacion_raw = hoy - timedelta(days = int(dias_en_mercado))
            fecha_publicacion = fecha_publicacion_raw.strftime("%Y-%m-%d")
            #region
            div_region_label = codigo_raw.find('div', class_='type-name min_height_20', string=re.compile("Region"))
            div_region = div_region_label.find_next_sibling('div', class_='type-value min_height_20')
            region = div_region.text.strip()
            #mts lot
            lot = 0
            div_lot_label = codigo_raw.find('div', class_='type-name min_height_20', string=re.compile("Lot m"))
            if div_lot_label is not None:
                div_lot = div_lot_label.find_next_sibling('div', class_='type-value min_height_20')
                lot = div_lot.text.strip()
            #mts Const
            const = 0
            div_const_label = codigo_raw.find('div', class_='type-name min_height_20', string=re.compile("Construction m"))
            if div_const_label is not None:
                div_const = div_const_label.find_next_sibling('div', class_='type-value min_height_20')
                const = div_const.text.strip()
            #Dirección
            address_raw = codigo_raw.find('p', class_='address m-1')
            address = address_raw.text.strip()
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

            #Nombre de propiedad y de vendedor, y links 
            links = codigo_raw.find_all('a')
            link = str(links[6].get('href'))

            nombre=""
            try:
                nombre = str(links[6].get_text(strip=True))[10:]
                nombre = formato_texto(nombre)
            except:
                pass

            vendor_link = str(links[5].get('href'))
            nombre_vendor = ""
            try:
                nombre_vendor = str(links[5].get_text(strip=True))
            except:
                pass

            #asignamos las variables a nuestra clase
            propiedad.code = codigo
            propiedad.link = link
            propiedad.name = nombre
            propiedad.address = address 
            propiedad.neighboorhood = str(region)
            propiedad.agent_link = vendor_link
            propiedad.agent_name = nombre_vendor
            propiedad.date_listed = str(fecha_publicacion)
            propiedad.currency = moneda
            propiedad.market_price = str(precio)
            propiedad.type = tipo_propiedad
            propiedad.status = estatus
            propiedad.mts_const = const
            propiedad.mts_lot = lot

            if tipo_propiedad in tipo_validado:
                if propiedad.insertar_propiedad(): 
                    #agregar propiedades a array para mostrar al final y enviar correo
                    propiedades_agregadas.append(propiedad)
                    #info log hacer de esto una sola funcion
                    log_action('Se agregó ' + str(propiedad.simple_print()))
                    print('Se agregó ' + str(propiedad.simple_print()))
                else:
                    log_action('El registro ' + str(codigo) + ' ya existe')
                    print('El registro ' + str(codigo) + ' ya existe')

            else:
                log_action('El registro ' + str(codigo) + ' no coincide con los criterios de búsqueda')
                print('El registro ' + str(codigo) + ' no coincide con los criterios de búsqueda')

            guardar_en_archivo('\n\n\n' + str(bloque.prettify()))

    time.sleep(60)

output_finalizado = "se agregaron " + str(len(propiedades_agregadas)) + ' nuevas propiedades' if len(propiedades_agregadas) > 0 else 'no se agregaron nuevas propiedades'
print('Finalizado: ' + output_finalizado)
log_action('Finalizado: ' + output_finalizado)
