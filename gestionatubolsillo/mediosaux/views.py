from django.shortcuts import redirect, render
from django.http import HttpRequest,HttpResponse
from django.views.decorators.http import require_POST, require_GET, require_http_methods
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
@require_GET
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
    return render(request,'mediosaux/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_medios_auxiliares)
@require_http_methods(["GET","POST"])
def create_medio_auxiliar(request:HttpRequest):
    if request.method == 'POST':
        created_at = now()
        nombre = request.POST.get('nombre','')
        errors = validate_medio_auxiliar(request,nombre)
        if errors:
            template = loader.get_template('mediosaux/form.html')
            context = {'action':'create'}
            return HttpResponse(template.render(context,request))
        medio_auxiliar = MedioAuxiliar()
        medio_auxiliar.nombre = nombre
        medio_auxiliar.fecha_creacion = created_at
        medio_auxiliar.usuario_creador = request.user
        medio_auxiliar.save()
        return redirect('/backoffice/medios_auxiliares')
    elif request.method == 'GET':
        template = loader.get_template('mediosaux/form.html')
        context = {'action':'create'}
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_medios_auxiliares)
@require_http_methods(["GET","POST"])
def edit_medio_auxiliar(request:HttpRequest, medio_auxiliar_id):
    medio_auxiliar = MedioAuxiliar.objects.filter(MedioAuxiliarID=medio_auxiliar_id).first()
    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        errors = validate_medio_auxiliar(request,nombre)
        if errors:
            template = loader.get_template('mediosaux/form.html')
            context = {
                'medio_auxiliar': medio_auxiliar,
                'action':'edit'
            }
            return HttpResponse(template.render(context,request))
        medio_auxiliar.nombre = nombre
        medio_auxiliar.save()
        return redirect('/backoffice/medios_auxiliares')
    elif request.method == 'GET':
        template = loader.get_template('mediosaux/form.html')
        context = {
            'medio_auxiliar': medio_auxiliar,
            'action':'edit'
        }
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_medios_auxiliares)
@require_POST
def delete_medio_auxiliar(request:HttpRequest, medio_auxiliar_id):
    medio_auxiliar = MedioAuxiliar.objects.filter(MedioAuxiliarID=medio_auxiliar_id).first()
    medio_auxiliar.delete()
    messages.success(request,"Medio auxiliar eliminado correctamente",extra_tags='success')
    return redirect('/backoffice/medios_auxiliares')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_medios_auxiliares)
@require_GET
def medio_auxiliar_details(request:HttpRequest, medio_auxiliar_id):
    medio_auxiliar = MedioAuxiliar.objects.filter(MedioAuxiliarID=medio_auxiliar_id).first()
    if not medio_auxiliar:
        messages.error(request,"El medio auxiliar no existe",extra_tags='error')
        return redirect('/backoffice/medios_auxiliares')
    context = {
        'medio_auxiliar': medio_auxiliar,
        'action':'view'
    }
    return render(request,'mediosaux/form.html',context)
