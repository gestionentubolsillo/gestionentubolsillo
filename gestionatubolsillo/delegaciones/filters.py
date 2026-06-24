from django.http import HttpRequest
from users.models import User


def filter_delegaciones(request:HttpRequest)->tuple[dict,dict]:
    user:User = request.user
    filtros = {'usuario_creador_id' : user.UserID}
    exclusiones = {}
    return filtros,exclusiones