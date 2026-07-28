from django.http import HttpRequest
from django.db.models.manager import BaseManager
from django.core.paginator import Paginator

from .models import Almacen_Item

DEFAULT_PAGINATION_ALMACEN = 25

def paginate_items(request:HttpRequest,items:BaseManager[Almacen_Item])->dict:
    n_pagina = request.GET.get('page',1)
    global DEFAULT_PAGINATION_ALMACEN
    n_almacen_items = request.GET.get('n_almacen_items', DEFAULT_PAGINATION_ALMACEN)
    paginacion = Paginator(items,n_almacen_items)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'almacen_items': page_obj,
        'page_obj': page_obj,
        'page':n_pagina,
        'n_almacen_items':n_almacen_items
    }
    return context