from typing import TypedDict
from django.db.models.manager import BaseManager
from users.models import User
from empresas.models import Empresa
from .models import Cliente, user_client
from servicios.models import Servicio
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


class UserClientData(TypedDict):
    username:str
    password:str
    cliente:Cliente

def build_user_client(data:UserClientData,servicios:BaseManager[Servicio],created_at:datetime |None = None,user_cli:user_client|None=None):
    if user_cli is None:
        user_cli = user_client()
        user_cli.fecha_creacion = created_at
        user_cli.cliente = data.get('cliente')
    user_cli.username = data.get('username')
    user_cli.set_password(data.get('password'))
    user_cli.save()
    user_cli.servicios.set(servicios)
