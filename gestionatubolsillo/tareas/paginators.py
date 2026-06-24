from django.core.paginator import Paginator
from django.http import HttpRequest
from django.db.models.manager import BaseManager

#Models to import
from users.models import User
from .models import Tarea, ListadoUsers

DEFAULT_PAGINATION_TAREAS = 25
DEFAULT_PAGINATION_LISTADOS = 25

def paginate_tareas(request:HttpRequest,tareas:BaseManager[Tarea]):

    user : User = request.user
    usuarios = User.objects.filter(tareas_asignadas__usuario_creador=user).distinct()
    choices = Tarea._meta.get_field('estado').choices

    n_pagina = request.GET.get('page',1)
    global DEFAULT_PAGINATION_TAREAS
    n_tareas = request.GET.get('n_tareas', DEFAULT_PAGINATION_TAREAS)
    paginacion = Paginator(tareas,n_tareas)
    page_obj = paginacion.get_page(n_pagina)

    context = {
        'tareas' : page_obj,
        'page_obj': page_obj,
        'page':n_pagina,
        'n_tareas':n_tareas,
        'usuarios':usuarios,
        'estados':choices
    }

    return context


def paginate_listados(request:HttpRequest,listados:BaseManager[ListadoUsers]):
    n_pagina = request.GET.get('page',1)
    global DEFAULT_PAGINATION_LISTADOS
    n_listas = request.GET.get('n_listas', DEFAULT_PAGINATION_LISTADOS)
    paginacion = Paginator(listados,n_listas)
    page_obj = paginacion.get_page(n_pagina)

    context = {
        'listados' : page_obj,
        'page_obj': page_obj,
        'page':n_pagina,
        'n_listas':n_listas
    }
    return context


def parse_data_listado_CRUD(request:HttpRequest,lista_id=None):
    user:User = request.user
    users_allowed = User.objects.filter(empresa__usuario_creador=user)
    context = {'usuarios':users_allowed}

    #Datos de edicion
    if lista_id:
        pass
    #Datos creacion
    else:
        context['action'] = 'create'
    return context

