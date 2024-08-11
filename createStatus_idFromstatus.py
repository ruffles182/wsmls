from props import get_all_status_from_properties
from props import insert_status_change
from props import get_status_id_by_name

#Obtenemos todos los valores de status  "id,code,status, market_price, currency"
resultados = get_all_status_from_properties()

for resultado in resultados:
    code = resultado[1]
    status_id = get_status_id_by_name(resultado[2])
    price = resultado[3]
    currency = resultado[4]

    insert_status_change(code, status_id, price, currency, True)
