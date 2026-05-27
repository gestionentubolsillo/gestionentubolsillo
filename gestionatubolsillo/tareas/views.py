from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template import loader
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.core.paginator import Paginator
from users.models import can_access_backoffice, User
from .models import Tarea, can_view_tareas, can_CRUD_tareas
from empresas.models import Empresa
from django.utils.timezone import now
# Create your views here.

DEFAULT_PAGINATION_TAREAS = 25

def validate_tarea(request:HttpRequest,texto)->bool:
    errors = False
    if texto=='':
        messages.error(request,"Debe indicar descripcion de la tarea",extra_tags='error')
    return errors

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_tareas)
def list_tareas(request:HttpRequest):
    user : User = request.user
    list_tareas = Tarea.objects.filter(
        creador_id = user.UserID
    )
    n_pagina = request.GET.get('page',1)
    global DEFAULT_PAGINATION_TAREAS
    n_tareas = request.GET.get('n_tareas', DEFAULT_PAGINATION_TAREAS)
    paginacion = Paginator(list_tareas,n_tareas)
    page_obj = paginacion.get_page(n_pagina)

    context = {
        'tareas' : page_obj,
        'page_obj': page_obj,
        'page':n_pagina,
        'n_tareas':n_tareas
    }
    return render(request,'list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_tareas)
def create_tarea(request:HttpRequest):
    user:User = request.user
    if request.method == 'POST':
        es_urgente = request.POST.get('is_urgent','Normal') == 'Urgente'
        texto = request.POST.get('texto','')

        errors = validate_tarea(request,texto)
        if errors:
            template = loader.get_template('form.html')
            context = {}
            return HttpResponse(template.render(context,request))

        
        created_at = now()
        #Checkear multiples checkbox para saber a que empresas se asignan las tareas
        #Cada checkbox debe tener un valor tipo empresa_<ID>
        empresas_marcadas_ids = [ int(key.split('_')[1]) for key in request.POST if key.startswith('empresa_')]
        if empresas_marcadas_ids:
            users = User.objects.filter(empresa_id__in=empresas_marcadas_ids).distinct()
            tareas = Tarea.objects.bulk_create(
                [Tarea(
                    texto=texto,
                    estado='pendiente',
                    es_urgente=es_urgente,
                    fecha_creacion = created_at,
                    usuario_creador = user,
                    usuario_asignado = u_asignado

                ) for u_asignado in users]
            )
        else:
            user_asigned_id :int = request.POST.get('user_id')
            user_asigned = User.objects.filter(id=user_asigned_id)
            if not user_asigned:
                messages.error(request,"Debe indicar un usuario válido",extra_tags='error')
                template = loader.get_template('form.html')
                context = {}
                return HttpResponse(template.render(context,request))

            tarea = Tarea()
            tarea.es_urgente = es_urgente
            tarea.estado = 'pendiente'
            tarea.texto = texto
            tarea.fecha_creacion = created_at
            tarea.usuario_creador = user
            tarea.usuario_asignado = user_asigned
            tarea.save()
        return redirect('backoffice/tareas')
    elif request.method == 'GET':
        template = loader.get_template('form.html')
        context = {}
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_tareas)
def delete_tarea(request:HttpRequest,tarea_id):
    tarea = Tarea.objects.filter(id=tarea_id).first()
    tarea.delete()
    messages.success(request,"La tarea se ha eliminado con éxito",extra_tags='success')
    return redirect('backoffice/tareas')


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_tareas)
def change_state_tarea(request:HttpRequest,tarea_id):
    tarea = Tarea.objects.filter(id=tarea_id).first()
    estado = request.POST.get('estado','pendiente')
    tarea.estado = estado
    tarea.save()
    messages.success(request,"Se acaba de actualizar la tarea correspondiente",extra_tags='success')
    return redirect('backoffice/tareas')
