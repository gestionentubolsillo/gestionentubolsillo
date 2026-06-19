from django.http import HttpRequest
from typing import TypedDict
from datetime import datetime
from django.contrib import messages

from users.models import User
from .models import Tarea

class QueryFilterData(TypedDict):
    usuario_id: str |None
    fecha_inicio: datetime | None
    fecha_fin: datetime | None
    estado: str
    es_urgente:str


def parse_datetime(value:str|None)->datetime:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None

def validate_query_filters(request:HttpRequest,data:QueryFilterData)->bool:
    errors = False

    usuario_id = data.get('usuario_id')
    if usuario_id and User.objects.filter(UserID=usuario_id).first() is None:
        errors = True
        messages.error(request,"Debe indicar un usuario válido",extra_tags='error')

    urgencia = data.get('es_urgente')
    if urgencia and not str(urgencia).isnumeric():
        messages.error(request,"Debe indicar un valor válido de urgencia de la tarea",extra_tags='error')
        errors = True
    
    choices = Tarea._meta.get_field('estado').choices
    estado = data.get('estado')
    if estado != '' and estado not in [choice[0] for choice in choices]:
        messages.error(request, "El estado debe ser uno de los posibles estados de una tarea",extra_tags='error')
        errors = True

    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    fechas_exists:bool = fecha_inicio and fecha_fin
    if fechas_exists and fecha_fin < fecha_inicio:
        messages.error(request,"La fecha de fin debe ser posterior a la fecha de inicio de la búsqueda", extra_tags='error')
        errors = True

    return errors