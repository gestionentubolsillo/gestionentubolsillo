from django.core.paginator import Paginator
from django.http import HttpRequest
from django.db.models.manager import BaseManager
from .models import User, Cuadrante
from servicios.models import Servicio

DEFAULT_PAGINATION_USERS = 25
DEFAULT_PAGINATION_USER_SERVICES = 25
DEFAULT_PAGINATION_USER_CUADRANTES = 25

def paginate_users(request:HttpRequest,users:BaseManager[User]):
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_USERS
    n_usuarios = request.GET.get('n_users', DEFAULT_PAGINATION_USERS)
    paginacion = Paginator(users, n_usuarios)
    page_obj = paginacion.get_page(n_pagina)

    context = {
        'usuarios': page_obj,
        'page_obj': page_obj,
        'page': n_pagina,
        'n_users':n_usuarios
    }
    return context

def paginate_servicios_users(request:HttpRequest,user:User):

    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_USER_SERVICES
    n_services = request.GET.get('n_services', DEFAULT_PAGINATION_USER_SERVICES)

    servicios = Servicio.objects.filter(users=user)

    paginacion = Paginator(servicios, n_services)
    page_obj = paginacion.get_page(n_pagina)

    context = {
        'usuario':user,
        'servicios': page_obj,
        'page_obj': page_obj,
        'page': n_pagina,
        'n_services':n_services
    }
    return context


def paginate_cuadrantes_users(request:HttpRequest,cuadrantes:BaseManager[Cuadrante],user:User):

    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_USER_SERVICES
    n_cuadrantes = request.GET.get('n_cuadrantes', DEFAULT_PAGINATION_USER_CUADRANTES)
    paginacion = Paginator(cuadrantes,n_cuadrantes)
    page_obj = paginacion.get_page(n_pagina)

    context = {
        'usuario':user,
        'cuadrantes': page_obj,
        'page_obj': page_obj,
        'page': n_pagina,
        'n_cuadrantes':n_cuadrantes
    }
    return context