from typing import TypedDict
from .models import Central
from datetime import datetime
from users.models import Cuenta

class CentralData(TypedDict):
    nombre:str
    telefono:str
    mail:str
    contacto:str
    observaciones:str

def build_central(data:CentralData,cuenta: Cuenta,created_at:datetime |None = None,central:Central|None = None):
    if central is None:
        central = Central()
        central.fecha_creacion = created_at
        central.cuenta = cuenta
    central.nombre = data.get('nombre')
    central.telefono = data.get('telefono')
    central.mail = data.get('mail')
    central.persona_de_contacto = data.get('contacto')
    central.observaciones = data.get('observaciones')
    central.save()