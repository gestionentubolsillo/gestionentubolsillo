from django.http import HttpRequest
from django.core.paginator import Paginator
from django.db.models.manager import BaseManager
from .models import Central

DEFAULT_PAGINATION_CENTRALES = 25

def paginate_centrales(request:HttpRequest,centrales:BaseManager[Central]):
    n_pagina = request.GET.get('page',1)
    global DEFAULT_PAGINATION_CENTRALES
    n_centrales = request.GET.get('n_centrales', DEFAULT_PAGINATION_CENTRALES)
    paginacion = Paginator(centrales,n_centrales)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'centrales': page_obj,
        'page_obj': page_obj,
        'page':n_pagina,
        'n_centrales':n_centrales
    }
    return context