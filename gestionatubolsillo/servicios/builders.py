from typing import TypedDict
from users.models import User
from empresas.models import Empresa
from .models import Servicio
from datetime import datetime
from decimal import Decimal

class ServicioData(TypedDict):
    nombre:str
    descripcion:str
    dias_semana:list[str]
    hora_inicio:str
    hora_fin:str
    precio_hora:Decimal
    is_active:bool
    is_exterior:bool
    empresa:Empresa
    mail:str
    need_gps:bool

def build_Servicio(data:ServicioData,user:User,created_at:datetime | None = None, servicio:Servicio | None = None):
    if servicio is None:
        servicio = Servicio()
        servicio.fecha_creacion = created_at
        servicio.cuenta = user.cuenta

    servicio.nombre = data.get('nombre')
    servicio.descripcion = data.get('descripcion')
    servicio.dias_semana = data.get('dias_semana')
    servicio.hora_inicio = data.get('hora_inicio')
    servicio.hora_fin = data.get('hora_fin')
    servicio.precio_por_hora = data.get('precio_hora')
    servicio.is_active = data.get('is_active')
    servicio.es_exterior = data.get('is_exterior')
    servicio.empresa = data.get('empresa')
    servicio.mail_de_contacto = data.get('mail')
    servicio.requiere_gps = data.get('need_gps')
    servicio.save()




