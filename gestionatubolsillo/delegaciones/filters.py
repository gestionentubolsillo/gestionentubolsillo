from django.http import HttpRequest
from users.models import User


def filter_delegaciones(request:HttpRequest)->tuple[dict,dict]:
    user:User = request.user
    filtros = {'cuenta_id' : user.cuenta.pk}
    exclusiones = {}
    return filtros,exclusiones