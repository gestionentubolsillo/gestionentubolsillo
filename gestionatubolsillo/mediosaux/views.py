from django.shortcuts import redirect, render
from django.http import HttpRequest,HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import can_access_backoffice, User
from .models import MedioAuxiliar, can_view_medios_auxiliares, can_CRUD_medios_auxiliares
from django.core.paginator import Paginator
from django.template import loader
from django.utils.timezone import now
from django.contrib import messages

DEFAULT_PAGINATION_MEDIOS_AUXILIARES = 25
# Create your views here.

def validate_medio_auxiliar(request:HttpRequest,nombre)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe indicar un nombre al medio auxiliar",extra_tags='error')
        errors = True
    return errors

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_medios_auxiliares)
def list_medios_auxiliares(request:HttpRequest):
    user:User = request.user
    medios_auxiliares = MedioAuxiliar.objects.filter(usuario_creador_id = user.UserID)
    n_pagina = request.GET.get('page',1)
    global DEFAULT_PAGINATION_MEDIOS_AUXILIARES
    n_medios_auxiliares = request.GET.get('n_medios_auxiliares', DEFAULT_PAGINATION_MEDIOS_AUXILIARES)
    paginacion = Paginator(medios_auxiliares,n_medios_auxiliares)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'medios_auxiliares': page_obj,
        'page_obj': page_obj,
        'page':n_pagina,
        'n_medios_auxiliares':n_medios_auxiliares
    }
    return render(request,'list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_medios_auxiliares)
def create_medio_auxiliar(request:HttpRequest):
    if request.method == 'POST':
        created_at = now()
        nombre = request.POST.get('nombre','')
        errors = validate_medio_auxiliar(request,nombre)
        if errors:
            template = loader.get_template('form.html')
            context = {}
            return HttpResponse(template.render(context,request))
        medio_auxiliar = MedioAuxiliar()
        medio_auxiliar.nombre = nombre
        medio_auxiliar.fecha_creacion = created_at
        medio_auxiliar.usuario_creador = request.user
        medio_auxiliar.save()
        return redirect('backoffice/medios_auxiliares')
    elif request.method == 'GET':
        template = loader.get_template('form.html')
        context = {}
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_medios_auxiliares)
def edit_medio_auxiliar(request:HttpRequest, medio_auxiliar_id):
    medio_auxiliar = MedioAuxiliar.objects.filter(id=medio_auxiliar_id).first()
    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        errors = validate_medio_auxiliar(request,nombre)
        if errors:
            template = loader.get_template('form.html')
            context = {
                'medio_auxiliar': medio_auxiliar,
                'action':'edit'
            }
            return HttpResponse(template.render(context,request))
        medio_auxiliar.nombre = nombre
        medio_auxiliar.save()
        return redirect('backoffice/medios_auxiliares')
    elif request.method == 'GET':
        template = loader.get_template('form.html')
        context = {
            'medio_auxiliar': medio_auxiliar,
            'action':'edit'
        }
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_medios_auxiliares)
def delete_medio_auxiliar(request:HttpRequest, medio_auxiliar_id):
    medio_auxiliar = MedioAuxiliar.objects.filter(id=medio_auxiliar_id).first()
    medio_auxiliar.delete()
    messages.success(request,"Medio auxiliar eliminado correctamente",extra_tags='success')
    return redirect('backoffice/medios_auxiliares')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_medios_auxiliares)
def medio_auxiliar_details(request:HttpRequest, medio_auxiliar_id):
    medio_auxiliar = MedioAuxiliar.objects.filter(id=medio_auxiliar_id).first()
    if not medio_auxiliar:
        messages.error(request,"El medio auxiliar no existe",extra_tags='error')
        return redirect('backoffice/medios_auxiliares')
    context = {
        'medio_auxiliar': medio_auxiliar,
        'action':'view'
    }
    return render(request,'form.html',context)
