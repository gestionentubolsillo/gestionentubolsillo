from typing import TypedDict
from users.models import User
from datetime import datetime
from .models import Delegacion


class DelegacionData(TypedDict):
    nombre:str
    user:User

def build_delegacion(data:DelegacionData,created_at:datetime|None = None,delegacion:Delegacion|None = None):
    if delegacion is None:
        delegacion = Delegacion()
        delegacion.usuario_creador = data.get('user')
        delegacion.fecha_creacion = created_at
    delegacion.nombre = data.get('nombre')
    delegacion.save()