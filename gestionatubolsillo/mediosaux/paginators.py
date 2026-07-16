from django.http import HttpRequest
from django.db.models.manager import BaseManager
from .models import MedioAuxiliar
from django.core.paginator import Paginator

DEFAULT_PAGINATION_MEDIOS_AUXILIARES = 25

def paginate_medios(request:HttpRequest,lista:BaseManager[MedioAuxiliar])->dict:
    n_pagina = request.GET.get('page',1)
    global DEFAULT_PAGINATION_MEDIOS_AUXILIARES
    n_medios_auxiliares = request.GET.get('n_medios_auxiliares', DEFAULT_PAGINATION_MEDIOS_AUXILIARES)
    paginacion = Paginator(lista,n_medios_auxiliares)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'medios_auxiliares': page_obj,
        'page_obj': page_obj,
        'page':n_pagina,
        'n_medios_auxiliares':n_medios_auxiliares
    }
    return context