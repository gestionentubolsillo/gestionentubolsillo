from django.core.paginator import Paginator
from django.http import HttpRequest
from users.models import User
from empresas.models import Empresa
from .models import Sugerencia
from django.db.models.manager import BaseManager


DEFAULT_PAGINATION_SUGERENCIAS = 25

def paginate_sugerencias(request:HttpRequest,sugerencias:BaseManager[Sugerencia]):
    choices = Sugerencia._meta.get_field('estado').choices
    user:User = request.user
    empresas = Empresa.objects.filter(usuario_creador=user)
    #TOREFACTOR: Solo seleccionar los usuarios que pertenecen a una misma cuenta
    users = User.objects.all()
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_SUGERENCIAS
    n_sugerencias = request.GET.get('n_sugerencias', DEFAULT_PAGINATION_SUGERENCIAS)
    paginator = Paginator(sugerencias, n_sugerencias)
    page_obj = paginator.get_page(n_pagina)
    context = {
        'sugerencias': page_obj,
        'page_obj': page_obj,
        'n_pagina': n_pagina,
        'n_sugerencias': n_sugerencias,
        'estados':choices,
        'empresas':empresas,
        'usuarios':users
    }
    return context