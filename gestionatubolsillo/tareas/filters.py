from django.http import HttpRequest
from users.models import User


def filtra_tareas(request:HttpRequest,query_errors:bool)->tuple[dict,dict]:
    user:User = request.user
    filtros = {'usuario_creador_id':user.UserID}
    exclusiones = {}
    if query_errors:
        return filtros, exclusiones
    
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    if fecha_inicio:
        filtros['fecha_creacion__gte'] = fecha_inicio
    if fecha_fin:
        filtros['fecha_creacion__lte'] = fecha_fin

    usuario = request.GET.get('usuario')
    if usuario:
        filtros['usuario_asignado_id'] = usuario

    urgencia = request.GET.get('urgencia')
    if urgencia:
        filtros['es_urgente'] = bool(int(urgencia))

    estado = request.GET.get('estado')
    if estado:
        filtros['estado']=estado
    else:
        exclusiones['estado']= 'borrada'

    return filtros, exclusiones

