from typing import TypedDict
from .models import User,Cuadrante, EncryptedFilePDF, PermisosModulo, Cuenta
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
    cuenta:Cuenta
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
        
        PermisosModulo.objects.bulk_create([
            PermisosModulo(user=user, modulo=modulo, nivel='0')
            for modulo, _ in PermisosModulo._meta.get_field('modulo').choices
        ])

    else:
        User.objects.filter(UserID=user.UserID).update(
                                                       **{K:v for K,v in data.items() if K not in ('password','cuenta')})
        
    return user


class ModulesData(TypedDict, total=False):
    USR:str
    TAR:str
    CLI:str
    CEN:str
    NFC:str
    MED:str
    SUG:str
    PAR:str
    INC:str
    ACU:str
    INS:str
    MAN:str
    ALM:str
    INF:str
    EMP:str
    CON:str

class UserPermissionsData(TypedDict):
    permisos:ModulesData
    has_dashboard_access:bool
    has_login_access:bool
    can_view_own_partes_trabajo:bool



def build_permissions(data:UserPermissionsData,user:User)->User:
    User.objects.filter(UserID=user.UserID).update(has_dashboard_access=data.get('has_dashboard_access'),
                                                          has_login_access=data.get('has_login_access'),
                                                        can_view_own_partes_trabajo=data.get('can_view_own_partes_trabajo'))
    modulos = data.get('permisos')
    for modulo, nivel in modulos.items():
        PermisosModulo.objects.update_or_create(user=user,modulo=modulo,defaults={'nivel':nivel})
    return user


class CuadranteData(TypedDict):
    nombre:str
    file:EncryptedFilePDF
    user:User

def build_cuadrante(data:CuadranteData)->Cuadrante:
    cuadrante = Cuadrante.objects.create(**data)
    return cuadrante