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

pagina_recientes = Page.web

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
        
        page.fill('input#btl-input-username', 'eliaszeitounian')
        page.fill('input#btl-input-password', 'Carretera1')
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

    n = 1
    for bloque in propiedades_bloque:
        propiedad = Propiedad()
        #campo código extract
        codigo_raw = BeautifulSoup(str(bloque), 'html.parser')
        codigo = codigo_raw.find('li', {'class': 'featured'}).get('id')
        #campo estatus
        div_estatus = bloque.find('div', class_='min_height_20 type-value')
        estatus = div_estatus.get_text(strip = True)
        #campo días en el mercado
        div_dias_en_mercado = ''
        div_dias_en_mercado = codigo_raw.find('div', class_='type-value min_height_20', string=re.compile("Days"))
        dias_en_mercado = div_dias_en_mercado.get_text(strip=True)
        dias_en_mercado = dias_en_mercado.replace("Days", "")
        dias_en_mercado = formato_texto(dias_en_mercado).strip()
        #fecha de publicación
        hoy = datetime.now()
        fecha_publicacion_raw = hoy - timedelta(days = int(dias_en_mercado))
        fecha_publicacion = fecha_publicacion_raw.strftime("%Y-%m-%d")
        #Tipo de propiedad
        div_tipo_propiedad = codigo_raw.find('a', class_='text-secondary')
        tipo_propiedad = div_tipo_propiedad.text.strip()
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
        span_precio = span_precio_raw.text.strip()
        precio = re.sub(r'[^\d]', '', str(span_precio))
        moneda = span_precio[:3]

        #Nombre de propiedad y de vendedor, y links 
        links = codigo_raw.find_all('a')
        link = str(links[6].get('href'))

        nombre = str(links[6].get_text(strip=True))[10:]
        nombre = formato_texto(nombre)

        vendor_link = str(links[5].get('href'))
        nombre_vendor = str(links[5].get_text(strip=True))

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

        propiedad.insertar_propiedad()

        log_action(str(n) + ' - ' + str(propiedad.simple_print()) + '\n')
        print(str(n) + propiedad.simple_print() + '\n')
        guardar_en_archivo('\n\n\n' + str(bloque.prettify()))
        n = n + 1
