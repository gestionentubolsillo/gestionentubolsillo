from django.shortcuts import redirect, render
from django.http import HttpRequest,HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import can_access_backoffice, User
from .models import Delegacion
from django.core.paginator import Paginator
from django.template import loader
from django.utils.timezone import now
from django.contrib import messages

DEFAULT_PAGINATION_DELEGACIONES = 25

def validate_delegacion(request:HttpRequest,nombre)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe indicar un nombre a la delegación",extra_tags='error')
        errors = True
    return errors
# Create your views here.
@login_required
@user_passes_test(can_access_backoffice)
def list_delegaciones(request: HttpRequest):
    user:User = request.user
    delegaciones = Delegacion.objects.filter(usuario_creador_id = user.UserID)
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
    return render(request,'delegaciones/list.html',context)

def create_delegacion(request: HttpRequest):
    if request.method == 'POST':
        created_at = now()
        nombre = request.POST.get('nombre','')
        user : User = request.user
        errors = validate_delegacion(request,nombre)
        if errors:
            template = loader.get_template('form.html')
            context = {'action':'create'}
            return HttpResponse(template.render(context,request))
        delegacion = Delegacion()
        delegacion.nombre = nombre
        delegacion.usuario_creador = user
        delegacion.fecha_creacion = created_at
        delegacion.save()
        return redirect('/backoffice/delegaciones')
    
    elif request.method == 'GET':
        template = loader.get_template('delegaciones/form.html')
        context = {'action':'create'}
        return HttpResponse(template.render(context,request))
    
@login_required
@user_passes_test(can_access_backoffice)
def delete_delegacion(request: HttpRequest, delegacion_id):
    delegacion = Delegacion.objects.filter(DelegacionID=delegacion_id).first()
    delegacion.delete()
    messages.success(request, 'La delegación ha sido borrada exitosamente.',extra_tags='success')
    return redirect('/backoffice/delegaciones')

@login_required
@user_passes_test(can_access_backoffice)
def edit_delegacion(request: HttpRequest, delegacion_id):
    delegacion = Delegacion.objects.filter(DelegacionID=delegacion_id).first()
    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        errors = validate_delegacion(request,nombre)
        if errors:
            template = loader.get_template('delegaciones/form.html')
            context = {
                'delegacion':delegacion,
                'action':'edit'
            }
            return HttpResponse(template.render(context,request))
        delegacion.nombre = nombre
        delegacion.save()
        messages.success(request, 'La delegación ha sido actualizada exitosamente.',extra_tags='success')
        return redirect('/backoffice/delegaciones')
    
    elif request.method == 'GET':
        template = loader.get_template('delegaciones/form.html')
        context = {
                'delegacion':delegacion,
                'action':'edit'
            }
        return HttpResponse(template.render(context,request))
    

@login_required
@user_passes_test(can_access_backoffice)
def delegacion_details(request: HttpRequest, delegacion_id):
    delegacion = Delegacion.objects.filter(DelegacionID=delegacion_id).first()
    if not delegacion:
        messages.error(request,"La delegación no existe",extra_tags='error')
        return redirect('/backoffice/delegaciones')
    context={
        'delegacion':delegacion,
        'action':'view'
    }
    return render(request,'delegaciones/form.html',context)