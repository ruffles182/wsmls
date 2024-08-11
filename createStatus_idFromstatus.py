from props import get_all_status_from_properties
from props import insert_status_change

#Obtenemos todos los valores de status  "id,code,status, market_price"
resultados = get_all_status_from_properties()

for resultado in resultados:
    code = resultado[1]
    status = resultado[2]
    price = resultado[3]
    
    
