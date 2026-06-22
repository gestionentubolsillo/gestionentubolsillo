from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template import loader
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.core.paginator import Paginator
from users.models import can_access_backoffice, User
from .models import Tarea, can_view_tareas, can_CRUD_tareas, ListadoUsers
from empresas.models import Empresa
from django.utils.timezone import now
from django.db.models import Count

from .validators import validate_query_filters, QueryFilterData, parse_datetime, validate_list_users,validate_tarea, validate_users_assigned
from .paginators import paginate_tareas, paginate_listados
from .filters import filtra_tareas
from .builders import create_bulk_tareas, build_listado_users
# Create your views here.


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_tareas)
def list_tareas(request:HttpRequest):

    data:QueryFilterData = {
        'usuario_id': request.GET.get('usuario'),
        'fecha_inicio': parse_datetime(request.GET.get('fecha_inicio')),
        'fecha_fin': parse_datetime(request.GET.get('fecha_fin')),
        'estado': request.GET.get('estado'),
        'es_urgente': request.GET.get('urgencia')

    }

    errors = validate_query_filters(request,data=data)

    filtros, exclusiones = filtra_tareas(request,errors)
    list_tareas = Tarea.objects.filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')

    context = paginate_tareas(request,list_tareas)

    return render(request,'tareas/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_tareas)
def create_tarea(request:HttpRequest):
    user:User = request.user
    users_allowed = User.objects.filter(empresa__usuario_creador=user)
    empresas = Empresa.objects.filter(usuario_creador=user)
    listas = ListadoUsers.objects.all()
    context = {'action':'create','empresas':empresas,'usuarios':users_allowed, 'listados':listas}
    template = loader.get_template('tareas/form.html')
    if request.method == 'POST':
        es_urgente = request.POST.get('is_urgent','Normal') == 'Urgente'
        texto = request.POST.get('texto','')

        errors = validate_tarea(request,texto)
        if errors:
            return HttpResponse(template.render(context,request))
        
        created_at = now()

        empresas_ids = [eid for eid in request.POST.getlist('empresas_ids') if eid]
        listas_usuarios_ids = [luid for luid in request.POST.getlist('listas_ids') if luid] 

        if empresas_ids:
            users = User.objects.filter(empresa_id__in=empresas_ids).distinct()
            create_bulk_tareas(data={'texto':texto,'es_urgente':es_urgente,'usuario_creador':user,'usuarios':users},created_at=created_at)

        elif listas_usuarios_ids:
            users = User.objects.filter(listados__id__in=listas_usuarios_ids).distinct()
            create_bulk_tareas(data={'texto':texto,'es_urgente':es_urgente,'usuario_creador':user,'usuarios':users},created_at=created_at)                  
        else:
            errors = validate_users_assigned(request)
            if errors:
                return HttpResponse(template.render(context,request))
            
            create_bulk_tareas(data={'texto':texto,'es_urgente':es_urgente,'usuario_creador':user,'usuarios':users},created_at=created_at)
        return redirect('/backoffice/tareas')
    
    elif request.method == 'GET':
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


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_tareas)
def details_tarea(request:HttpRequest,tarea_id):
    tarea = Tarea.objects.filter(TareaID=tarea_id).first()
    if not tarea:
        messages.error(request,"La tarea no existe",extra_tags='error')
        return redirect('/backoffice/tareas')
    template = loader.get_template('tareas/form.html')
    context = {'action': 'view','tarea': tarea}

    return HttpResponse(template.render(context,request))


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_tareas)
def create_list_usuarios(request:HttpRequest):
    template = loader.get_template('tareas/list_users/form.html')
    user:User = request.user
    users_allowed = User.objects.filter(empresa__usuario_creador=user)
    context = {'usuarios':users_allowed,'action':'create'}
    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        users_ids = request.POST.getlist('users_ids')
        errors = validate_list_users(request,nombre,users_ids)
        if errors:
            return HttpResponse(template.render(context,request))
        
        users = User.objects.filter(UserID__in=users_ids)
        build_listado_users(data={'nombre':nombre,'usuarios':users})
        return redirect('/backoffice/tareas/listados')

    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))
    
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_tareas)
def edit_list_usuarios(request:HttpRequest,lista_id):
    template = loader.get_template('tareas/list_users/form.html')
    user:User = request.user
    listado = ListadoUsers.objects.filter(id=lista_id).first()
    users_allowed = User.objects.filter(empresa__usuario_creador=user)
    listado_users_ids = set(listado.usuarios.values_list('UserID', flat=True))
    context = {'usuarios':users_allowed,'listado':listado, 'action':'edit','listado_users':listado_users_ids}
    if request.method == 'POST':
        users_ids = request.POST.getlist('users_ids')
        users = User.objects.filter(UserID__in=users_ids)
        listado.usuarios.set(users)
        return redirect('/backoffice/tareas/listados')
    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_tareas)
def lista_listados_de_usuarios(request:HttpRequest):
    listas = ListadoUsers.objects.all().annotate(num_users=Count('usuarios',distinct=True))
    context = paginate_listados(request,listas)
    return render(request,'tareas/list_users/list.html',context)

