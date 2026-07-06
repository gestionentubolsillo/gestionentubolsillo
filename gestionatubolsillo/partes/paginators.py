from django.http import HttpRequest
from django.core.paginator import Paginator
from django.db.models.manager import BaseManager

from clientes.models import Cliente
from empresas.models import Empresa
from .models import Parte
from users.models import User

DEFAULT_PAGINATION_PARTES = 25

def paginate_informes(request:HttpRequest,listado:BaseManager[Parte]):
    #contexto de los filtros
    user : User = request.user
    clientes = Cliente.objects.filter(cuenta=user.cuenta)
    empresas = Empresa.objects.filter(cuenta=user.cuenta)
    usuarios = User.objects.filter(cuenta=user.cuenta)
    global DEFAULT_PAGINATION_PARTES
    n_pagina = request.GET.get('page',1)
    n_partes = request.GET.get('n_partes',DEFAULT_PAGINATION_PARTES)
    paginacion = Paginator(listado,n_partes)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'partes':page_obj,
        'page_obj':page_obj,
        'page': n_pagina,
        'n_partes': n_partes,
        'clientes': clientes,
        'empresas': empresas,
        'usuarios': usuarios
    }
    return context


def paginate_informes_trabajo_resumen(request:HttpRequest,listado:BaseManager[User]):
    user : User = request.user
    clientes = Cliente.objects.filter(cuenta=user.cuenta)
    empresas = Empresa.objects.filter(cuenta=user.cuenta)
    usuarios = User.objects.filter(cuenta=user.cuenta)

    global DEFAULT_PAGINATION_PARTES
    n_pagina = request.GET.get('page',1)
    n_users = request.GET.get('n_users',DEFAULT_PAGINATION_PARTES)
    paginacion = Paginator(listado,n_users)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'usuarios_informes':page_obj,
        'page_obj':page_obj,
        'page': n_pagina,
        'n_users': n_users,
        'clientes': clientes,
        'empresas': empresas,
        'usuarios': usuarios
    }
    return context