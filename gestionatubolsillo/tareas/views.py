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

def create_bulk_tareas(texto, es_urgente, created_at, usuario_creador, usuarios):
    Tarea.objects.bulk_create(
                [Tarea(
                    texto=texto,
                    estado='pendiente',
                    es_urgente=es_urgente,
                    fecha_creacion = created_at,
                    usuario_creador = usuario_creador,
                    usuario_asignado = u_asignado

                ) for u_asignado in usuarios]
            )

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_tareas)
def list_tareas(request:HttpRequest):
    user : User = request.user
    list_tareas = Tarea.objects.filter(
        usuario_creador_id = user.UserID
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
    return render(request,'tareas/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_tareas)
def create_tarea(request:HttpRequest):
    user:User = request.user
    users_allowed = User.objects.filter(empresa__usuario_creador=user)
    empresas = Empresa.objects.filter(usuario_creador=user)
    context = {'action':'create','empresas':empresas,'usuarios':users_allowed}
    if request.method == 'POST':
        es_urgente = request.POST.get('is_urgent','Normal') == 'Urgente'
        texto = request.POST.get('texto','')

        errors = validate_tarea(request,texto)
        if errors:
            template = loader.get_template('tareas/form.html')
            return HttpResponse(template.render(context,request))
        
        created_at = now()

        empresas_ids = [eid for eid in request.POST.getlist('empresas_ids') if eid]
        listas_usuarios_ids = [luid for luid in request.POST.getlist('listas_ids') if luid] 
        if empresas_ids:
            users = User.objects.filter(empresa_id__in=empresas_ids).distinct()
            create_bulk_tareas(texto=texto,es_urgente=es_urgente,created_at=created_at,usuario_creador=user,usuarios=users)

        elif listas_usuarios_ids:
            #TODO: Implementar clase lista de usuarios para poder asignar usuarios repetidamente en bloque
            #Funcionalidad pensada para tareas que requieren repetirse cada cierto tiempo
            pass                   
        else:
            users_asigned_id :int = [uid for uid in request.POST.getlist('users_id') if uid]
            users_asigned = User.objects.filter(UserID__in=users_asigned_id)
            if not users_asigned:
                messages.error(request,"Debe indicar un usuario válido",extra_tags='error')
                template = loader.get_template('tareas/form.html')
                return HttpResponse(template.render(context,request))
            create_bulk_tareas(texto=texto,es_urgente=es_urgente,created_at=created_at,usuario_creador=user,usuarios=users_asigned)  
        return redirect('/backoffice/tareas')
    
    elif request.method == 'GET':
        template = loader.get_template('tareas/form.html')
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_tareas)
def delete_tarea(request:HttpRequest,tarea_id):
    tarea = Tarea.objects.filter(TareaID=tarea_id).first()
    tarea.delete()
    messages.success(request,"La tarea se ha eliminado con éxito",extra_tags='success')
    return redirect('/backoffice/tareas')


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_tareas)
def change_state_tarea(request:HttpRequest,tarea_id):
    tarea = Tarea.objects.filter(TareaID=tarea_id).first()
    estado = request.POST.get('estado','pendiente')
    tarea.estado = estado
    tarea.save()
    messages.success(request,"Se acaba de actualizar la tarea correspondiente",extra_tags='success')
    return redirect('/backoffice/tareas')
