from enum import Enum

class Moneda(Enum):
    Dollar = 0
    Pesos = 1

class TipoPropiedad(Enum):
    Residencial = 0


class Propiedad:
    id = ""
    link = ""
    nombre = ""
    direcion = ""
    precio = 0
    moneda = ""
    tipo = ""
    estatus = ""
    region = ""