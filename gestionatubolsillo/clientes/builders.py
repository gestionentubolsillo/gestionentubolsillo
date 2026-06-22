from typing import TypedDict
from users.models import User
from empresas.models import Empresa
from .models import Cliente
from datetime import datetime


class ClienteData(TypedDict):
    nombre:str
    mail:str
    contacto:str
    direccion:str
    provincia:str
    municipio:str
    telefono:str
    empresa:Empresa

def build_cliente(data:ClienteData,created_at:datetime | None = None,cliente:Cliente | None = None):
    if cliente is None:
        cliente = Cliente()
        cliente.fecha_creacion = created_at
    cliente.nombre = data.get('nombre')
    cliente.email = data.get('mail')
    cliente.persona_contacto = data.get('contacto')
    cliente.direccion = data.get('direccion')
    cliente.provincia = data.get('provincia')
    cliente.municipio = data.get('municipio')
    cliente.telefono = data.get('telefono')
    cliente.empresa = data.get('empresa')
    cliente.save()