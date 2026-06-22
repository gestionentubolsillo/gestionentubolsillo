from typing import TypedDict
from users.models import User
from .models import Tarea, ListadoUsers
from datetime import datetime
from django.db.models.manager import BaseManager



class TareaBulkData(TypedDict):
    texto:str
    es_urgente:bool
    usuario_creador:User
    usuarios:BaseManager[User]



def create_bulk_tareas(data:TareaBulkData, created_at:datetime):
    Tarea.objects.bulk_create(
                [Tarea(
                    texto=data.get('texto'),
                    estado='pendiente',
                    es_urgente=data.get('es_urgente'),
                    fecha_creacion = created_at,
                    usuario_creador = data.get('usuario_creador'),
                    usuario_asignado = u_asignado

                ) for u_asignado in data.get('usuarios')]
            )
    

class ListaUserData(TypedDict):
    nombre:str
    usuarios:BaseManager[User]


def build_listado_users(data:ListaUserData):
    listado = ListadoUsers()
    listado.nombre = data.get('nombre')
    listado.save()
    listado.usuarios.set(data.get('usuarios'))
