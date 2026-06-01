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

# Create your views here.
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
def dashboard_informes(request:HttpRequest):
    #Vista que lista los diferentes enlaces para consulta de los diferentes tipos de informe
    pass

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_trabajo)
def list_partes_trabajo(request:HttpRequest):
    pass

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_incidencia)
def list_partes_incidencia(request:HttpRequest):
    pass

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_inspeccion)
def list_partes_inspeccion(request:HttpRequest):
    pass

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_acuda)
def list_inf_acuda(request:HttpRequest):
    pass

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