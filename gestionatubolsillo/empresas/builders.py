from typing import TypedDict
from users.models import User
from .models import Empresa

class EmpresaData(TypedDict):
    nombre:str
    paquete:str

def build_empresa(data:EmpresaData,creador:User | None = None, empresa:Empresa|None=None ):
    if empresa is None:
        empresa = Empresa()
        empresa.usuario_creador = creador
    empresa.nombre = data.get('nombre')
    empresa.paquete = data.get('paquete')
    empresa.save()