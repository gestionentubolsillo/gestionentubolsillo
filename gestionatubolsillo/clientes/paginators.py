from django.core.paginator import Paginator
from django.http import HttpRequest
from users.models import User
from empresas.models import Empresa
from django.db.models.manager import BaseManager
from .models import Cliente, user_client

DEFAULT_PAGINATION_CLIENTS = 25
DEFAULT_PAGINATION_CLIENT_SERVICES = 10
DEFAULT_PAGINATION_USER_CLI = 25

def paginate_clientes(request:HttpRequest,clientes:BaseManager[Cliente]):
    user:User = request.user
    empresas = Empresa.objects.filter(usuario_creador_id=user.UserID)
    empresa:Empresa = user.empresa
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_CLIENTS
    n_clientes = request.GET.get('n_clients', DEFAULT_PAGINATION_CLIENTS)
    filtro_empresa = request.GET.get('empresa',empresa.EmpresaID)

    paginacion = Paginator(clientes,n_clientes)
    page_obj = paginacion.get_page(n_pagina)

    context = {
        'clientes':page_obj,
        'page_obj':page_obj,
        'page':n_pagina,
        'n_clients':n_clientes,
        'empresas':empresas,
        'filtro_empresa':filtro_empresa
    }

    return context


def paginate_servicios_de_cliente(request:HttpRequest,cliente:Cliente):
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_CLIENT_SERVICES
    n_services = request.GET.get('n_services', DEFAULT_PAGINATION_CLIENT_SERVICES)
    servicios = cliente.servicios.all().order_by('ServicioID')
    paginacion = Paginator(servicios,n_services)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'cliente':cliente,
        'action':'view',
        'servicios':page_obj,
        'page_obj':page_obj,
        'page':n_pagina,
        'n_services':n_services

    }
    return context

def paginate_cliente_users(request:HttpRequest, cliente:Cliente):
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_USER_CLI
    n_user_clis = request.GET.get('n_us_clis', DEFAULT_PAGINATION_USER_CLI)
    lista_user_clis = user_client.objects.filter(cliente_id = cliente.ClienteID)
    paginacion = Paginator(lista_user_clis,n_user_clis)
    page_obj = paginacion.get_page(n_pagina)

    context = {
        'user_clis':page_obj,
        'page_obj':page_obj,
        'page':n_pagina,
        'n_user_clis':n_user_clis
    }

    return context