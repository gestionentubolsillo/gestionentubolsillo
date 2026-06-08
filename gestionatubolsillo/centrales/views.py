from django.contrib import messages
from django.template import loader
from django.shortcuts import render, redirect
from django.http import HttpRequest,HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import can_access_backoffice, User
from .models import Central, can_view_centrales, can_CRUD_centrales
from django.core.paginator import Paginator
from django.utils.timezone import now


DEFAULT_PAGINATION_CENTRALES = 25
# Create your views here.

def validate_central(request:HttpRequest,nombre)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe indicar un nombre a la central receptora",extra_tags='error')
        errors = True
    return errors

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_centrales)
def list_centrales(request: HttpRequest):
    user:User = request.user
    centrales = Central.objects.filter(usuario_creador_id = user.UserID)
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
    return render(request,'centrales/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_centrales)
def create_central(request: HttpRequest):
    if request.method == 'POST':
        created_at = now()
        nombre = request.POST.get('nombre','')
        telefono = request.POST.get('telefono','')
        mail = request.POST.get('mail','')
        persona_de_contacto = request.POST.get('persona_de_contacto','')
        observaciones = request.POST.get('observaciones','')

        errors = validate_central(request,nombre)
         
        if errors:
            template = loader.get_template('form.html')
            context = {'action':'create'}
            return HttpResponse(template.render(context,request))
         
        central = Central()
        central.nombre = nombre
        central.telefono = telefono
        central.mail = mail
        central.persona_de_contacto = persona_de_contacto
        central.observaciones = observaciones
        central.usuario_creador = request.user
        central.fecha_creacion = created_at
        central.save()

        return redirect('/backoffice/centrales')
    
    elif request.method == 'GET':
        template = loader.get_template('centrales/form.html')
        context = {'action':'create'}
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_centrales)
def edit_central(request: HttpRequest, central_id):
    central = Central.objects.filter(CentralID=central_id).first()
    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        telefono = request.POST.get('telefono','')
        mail = request.POST.get('mail','')
        persona_de_contacto = request.POST.get('persona_de_contacto','')
        observaciones = request.POST.get('observaciones','')
        errors = validate_central(request,nombre)
        if errors:
            template = loader.get_template('centrales/form.html')
            context = {
            'action':'edit',
            'central': central
            }
            return HttpResponse(template.render(context,request))
        central.nombre = nombre
        central.telefono = telefono
        central.mail = mail
        central.persona_de_contacto = persona_de_contacto
        central.observaciones = observaciones
        central.save()
        return redirect('/backoffice/centrales')
    elif request.method == 'GET':
        template = loader.get_template('centrales/form.html')
        context = {
            'action':'edit',
            'central': central
            }
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_centrales)
def delete_central(request: HttpRequest, central_id):
    central = Central.objects.filter(CentralID=central_id).first()
    central.delete()
    messages.success(request,"Central receptora eliminada correctamente",extra_tags='success')
    return redirect('/backoffice/centrales')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_centrales)
def central_details(request: HttpRequest, central_id):
    central = Central.objects.filter(CentralID=central_id).first()
    if not central:
        messages.error(request,"La central receptora no existe",extra_tags='error')
        return redirect('/backoffice/centrales')
    context = {
        'central': central,
        'action':'view'
    }
    return render(request,'centrales/form.html',context)