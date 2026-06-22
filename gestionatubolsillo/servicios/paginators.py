from django.core.paginator import Paginator
from django.http import HttpRequest
from users.models import User
from empresas.models import Empresa
from django.db.models.manager import BaseManager
from .models import Servicio

DEFAULT_PAGINATION_SERVICIOS = 25
DEFAULT_PAGINATION_SERVICIOS_CLIENTES = 25

def paginate_servicios(request:HttpRequest,servicios:BaseManager[Servicio]):
    user:User = request.user
    empresas = Empresa.objects.filter(usuario_creador_id=user.UserID)
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_SERVICIOS
    n_servicios = request.GET.get('n_servicios', DEFAULT_PAGINATION_SERVICIOS)
    paginacion = Paginator(servicios,n_servicios)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'servicios':page_obj,
        'page_obj':page_obj,
        'page':n_pagina,
        'n_servicios':n_servicios,
        'empresas':empresas
    }
    return context


def paginate_clientes_de_servicio(request:HttpRequest,servicio:Servicio):
    dias_choices = Servicio._meta.get_field('dias_semana').choices
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_SERVICIOS_CLIENTES
    n_clientes = request.GET.get('n_clientes', DEFAULT_PAGINATION_SERVICIOS_CLIENTES)
    lista_clientes = servicio.clientes.all().order_by('ClienteID')
    paginacion = Paginator(lista_clientes,n_clientes)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'servicio':servicio,
        'dias_choices':dias_choices,
        'action':'view',
        'clientes':page_obj,
        'page_obj':page_obj,
        'page':n_pagina,
        'n_clientes':n_clientes,
    }

    return context