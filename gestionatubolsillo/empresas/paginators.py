from django.core.paginator import Paginator
from django.http import HttpRequest
from django.db.models.manager import BaseManager
from .models import Empresa
from users.models import User


DEFAULT_PAGINATION_EMPRESAS = 25

def paginate_empresas(request:HttpRequest, empresas:BaseManager[Empresa]):
    user:User = request.user
    empresa_usuario:Empresa = user.empresa
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_EMPRESAS
    #La empresa del usuario siempre va a aparecer por lo que se debe mostrar 1 empresa menos de paginacion
    n_empresas :int = request.GET.get('n_empresas', DEFAULT_PAGINATION_EMPRESAS) -1
    paginacion = Paginator(empresas,n_empresas)
    page_obj = paginacion.get_page(n_pagina)

    context = {
        'empresa_usuario' : empresa_usuario,
        'empresas': page_obj,
        'page_obj': page_obj,
        'page': n_pagina,
        'n_empresas':n_empresas+1,
    }

    return context