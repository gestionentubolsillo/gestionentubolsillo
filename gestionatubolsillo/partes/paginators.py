from django.http import HttpRequest
from django.core.paginator import Paginator
from django.db.models.manager import BaseManager
from .models import Parte

DEFAULT_PAGINATION_PARTES = 25

def paginate_informes(request:HttpRequest,listado:BaseManager[Parte]):
    global DEFAULT_PAGINATION_PARTES
    n_pagina = request.GET.get('page',1)
    n_partes = request.GET.get('n_partes',DEFAULT_PAGINATION_PARTES)
    paginacion = Paginator(listado,n_partes)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'partes':page_obj,
        'page_obj':page_obj,
        'page': n_pagina,
        'n_partes': n_partes
    }
    return context