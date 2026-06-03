from django.shortcuts import render, redirect
from django.http import HttpRequest,HttpResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required,user_passes_test
from django.template import loader
from django.core.paginator import Paginator
from users.models import User, can_access_backoffice
from django.contrib import messages
#Mucha info sale mas rentable importarlo todo
from .models import *
from empresas.models import Empresa

# Create your views here.
DEFAULT_PAGINATION_PARTES = 25
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
def dashboard_informes(request:HttpRequest):
    #Vista que lista los diferentes enlaces para consulta de los diferentes tipos de informe
    context = {}
    return render(request,'list_general.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_trabajo)
def list_partes_trabajo(request:HttpRequest):
    empresa_id = request.GET.get('empresa_id')
    partes = Parte_Trabajo.objects.filter(empresa_id = empresa_id).order_by('-fecha_creacion')
    global DEFAULT_PAGINATION_PARTES
    n_pagina = request.GET.get('page',1)
    n_partes = request.GET.get('n_partes',DEFAULT_PAGINATION_PARTES)
    paginacion = Paginator(partes,n_partes)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'partes':page_obj,
        'page_obj':page_obj,
        'page': n_pagina,
        'n_partes': n_partes
    }
    return render(request,'list_trabajo.html',context)
    


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_incidencia)
def list_partes_incidencia(request:HttpRequest):
    empresa_id = request.GET.get('empresa_id')
    partes = Parte_Incidencia.objects.filter(empresa_id = empresa_id).order_by('-fecha_creacion')
    global DEFAULT_PAGINATION_PARTES
    n_pagina = request.GET.get('page',1)
    n_partes = request.GET.get('n_partes',DEFAULT_PAGINATION_PARTES)
    paginacion = Paginator(partes,n_partes)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'partes':page_obj,
        'page_obj':page_obj,
        'page': n_pagina,
        'n_partes': n_partes
    }
    return render(request,'list_incidencia.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_inspeccion)
def list_partes_inspeccion(request:HttpRequest):
    empresa_id = request.GET.get('empresa_id')
    partes = Parte_Inspeccion.objects.filter(empresa_id = empresa_id).order_by('-fecha_creacion')
    global DEFAULT_PAGINATION_PARTES
    n_pagina = request.GET.get('page',1)
    n_partes = request.GET.get('n_partes',DEFAULT_PAGINATION_PARTES)
    paginacion = Paginator(partes,n_partes)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'partes':page_obj,
        'page_obj':page_obj,
        'page': n_pagina,
        'n_partes': n_partes
    }
    return render(request,'list_inspeccion.html',context)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_acuda)
def list_inf_acuda(request:HttpRequest):
    empresa_id = request.GET.get('empresa_id')
    partes = Informe_Acuda.objects.filter(empresa_id = empresa_id).order_by('-fecha_creacion')
    global DEFAULT_PAGINATION_PARTES
    n_pagina = request.GET.get('page',1)
    n_partes = request.GET.get('n_partes',DEFAULT_PAGINATION_PARTES)
    paginacion = Paginator(partes,n_partes)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'partes':page_obj,
        'page_obj':page_obj,
        'page': n_pagina,
        'n_partes': n_partes
    }
    return render(request,'list_acuda.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_parte_trabajo)
def create_parte_trabajo(request:HttpRequest):
    pass

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_parte_incidencia)
def create_parte_incidencia(request:HttpRequest):
    pass


#Para la inspeccion el inspector que crea el parte no necesita tener acceso al backoffice
@login_required
@user_passes_test(can_CRUD_parte_inspeccion)
def create_parte_inspeccion(request:HttpRequest):
    pass

@login_required
@user_passes_test(can_CRUD_acuda)
def create_inf_acuda(request:HttpRequest):
    pass

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_parte_trabajo)
def add_actividad_to_parte_trabajo(request:HttpRequest,p_trabajo_id):
    pass

#Necesario indagar más en estas caracteristicas