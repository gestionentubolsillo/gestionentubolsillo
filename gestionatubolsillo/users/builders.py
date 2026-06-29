from typing import TypedDict
from .models import User,Cuadrante, EncryptedFilePDF
from empresas.models import Empresa
from decimal import Decimal
from django.core.files.uploadedfile import UploadedFile


class UserCoreData(TypedDict):
    username:str
    password:str
    email:str

class UserData(UserCoreData):
    first_name:str
    last_name:str
    direccion:str
    telefono:str
    nif:str
    provincia:str
    municipio:str
    empresa:Empresa
    esInspector:bool
    esInspector_parteTrabajo:bool
    always_track_GPS:bool
    categoria:str
    precio_hora:Decimal
    comentarios:str

def build_user(data:UserData,user:User|None = None)->User:
    if user is None:
        user = User.objects.create_user(username=data.get('username'),email=data.get('email'),password=data.get('password'),
                                        **{K:v for K,v in data.items() if K not in ('username', 'email', 'password')})
    else:
        User.objects.filter(UserID=user.UserID).update(
                                                       **{K:v for K,v in data.items() if K !='password'})
        
    return user

class UserPermissionsData(TypedDict):
    permisos_central_receptora:str
    permisos_clientes:str
    permisos_configuracion:str
    permisos_almacen:str
    permisos_empresas:str
    permisos_informes:str
    permisos_informes_acuda:str
    permisos_mantenimientos:str
    permisos_medios_auxiliares:str
    permisos_partes_incidencias:str
    permisos_partes_inspeccion:str
    permisos_partes_trabajo:str
    permisos_servicios_NFC:str
    permisos_sugerencias:str
    permisos_tareas:str
    permisos_usuario:str
    has_dashboard_access:bool
    has_login_access:bool
    can_view_own_partes_trabajo:bool

def build_permissions(data:UserPermissionsData,user:User)->User:
    user = User.objects.filter(UserID=user.UserID).update(**data)
    return user


class CuadranteData(TypedDict):
    nombre:str
    file:EncryptedFilePDF
    user:User

def build_cuadrante(data:CuadranteData)->Cuadrante:
    cuadrante = Cuadrante.objects.create(**data)
    return cuadrante