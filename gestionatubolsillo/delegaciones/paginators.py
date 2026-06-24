from django.http import HttpRequest
from django.core.paginator import Paginator
from django.db.models.manager import BaseManager
from .models import Delegacion

DEFAULT_PAGINATION_DELEGACIONES = 25

def paginate_delegaciones(request:HttpRequest,delegaciones:BaseManager[Delegacion]):
    n_pagina = request.GET.get('page',1)
    global DEFAULT_PAGINATION_DELEGACIONES
    n_delegaciones = request.GET.get('n_delegaciones', DEFAULT_PAGINATION_DELEGACIONES)
    paginacion = Paginator(delegaciones,n_delegaciones)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'delegaciones': page_obj,
        'page_obj': page_obj,
        'page':n_pagina,
        'n_delegaciones':n_delegaciones
    }
    return context