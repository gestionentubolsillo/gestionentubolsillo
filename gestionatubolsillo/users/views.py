from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import User,Cuadrante, can_access_backoffice, can_view_users, can_CRUD_users
from django.core.paginator import Paginator
from django.template import loader
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest, FileResponse
from django.contrib import messages
from empresas.models import Empresa
from decimal import Decimal
from servicios.models import can_CRUD_servicios, Servicio
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.db.models.manager import BaseManager
from enum import Enum
from django.views.decorators.clickjacking import xframe_options_sameorigin
# Create your views here.

from .filters import filter_users,filter_cuadrantes
from .paginators import paginate_users, paginate_servicios_users, paginate_cuadrantes_users
from .builders import build_user,build_permissions,build_cuadrante
from .validators import validate_user,validate_user_edit,validate_services_of_user,can_user_access_cuadrante, validate_cuadrante

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
def create_user(request:HttpRequest):
    return _create_or_modify_user(request)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
def lista_users(request:HttpRequest):
    
    filtros, exclusiones = filter_users(request)
    lista_usuarios = User.objects.filter(**filtros).exclude(**exclusiones).order_by('UserID')
    context = paginate_users(request,lista_usuarios)

    return render(request,'account/users/list.html', context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
def user_details(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    if not user:
        messages.error(request,"El usuario no existe",extra_tags='error')
        return redirect('/backoffice/users')
    context = {'action':'view','usuario':user}
    return render(request,'account/users/form.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
def edit_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    return _create_or_modify_user(request,user)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
def delete_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    user.delete()
    messages.success(request,"El usuario ha sido eliminado correctamente",extra_tags='success')
    return redirect('/backoffice/users')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
def alter_user_permissions(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    if request.method == 'POST':
        p_almacen = request.POST.get('p_almacen','no_access')
        p_central = request.POST.get('p_central','no_access')
        p_clientes = request.POST.get('p_clientes','no_access')
        p_config = request.POST.get('p_config','no_access')
        p_empresas = request.POST.get('p_empresas','no_access')
        p_informes = request.POST.get('p_informes','no_access')
        p_acuda = request.POST.get('p_acuda','no_access')
        p_mantenimiento = request.POST.get('p_mantenimiento','no_access')
        p_medio_aux = request.POST.get('p_medio_aux','no_access')
        p_parte_incidencia = request.POST.get('p_parte_incidencia','no_access')
        p_parte_trabajo = request.POST.get('p_parte_trabajo','no_access')
        p_parte_inspeccion = request.POST.get('p_parte_inspeccion','no_access')
        p_servicio_NFC = request.POST.get('p_servicio_NFC','no_access')
        p_sugerencias = request.POST.get('p_sugerencias','no_access')
        p_tareas = request.POST.get('p_tareas','no_access')
        p_usuario = request.POST.get('p_usuario','no_access')
        p_dashboard = request.POST.get('p_dashboard') == 'on'
        p_login = request.POST.get('p_login') == 'on'
        p_view_self_trabajo = request.POST.get('p_view_self_trabajo') == 'on'

        
        user = build_permissions(data={
            'can_view_own_partes_trabajo':p_view_self_trabajo,
            'has_dashboard_access':p_dashboard,
            'has_login_access':p_login,
            'permisos_almacen':p_almacen,
            'permisos_central_receptora':p_central,
            'permisos_clientes':p_clientes,
            'permisos_configuracion':p_config,
            'permisos_empresas':p_empresas,
            'permisos_informes':p_informes,
            'permisos_informes_acuda':p_acuda,
            'permisos_mantenimientos':p_mantenimiento,
            'permisos_medios_auxiliares':p_medio_aux,
            'permisos_partes_incidencias':p_parte_incidencia,
            'permisos_partes_inspeccion':p_parte_inspeccion,
            'permisos_partes_trabajo':p_parte_trabajo,
            'permisos_servicios_NFC':p_servicio_NFC,
            'permisos_sugerencias':p_sugerencias,
            'permisos_tareas':p_tareas,
            'permisos_usuario':p_usuario
        },user=user)
        return redirect("/backoffice/users")

    elif request.method == 'GET':
        template = loader.get_template('account/users/permissions/form.html')
        context = {
            'usuario':user,
            'action':'edit',
            'choices':User.PERMISSIONS_CHOICES
        }
        return HttpResponse(template.render(context,request))
    
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
def view_user_permissions(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    if not user:
        messages.error(request,"El usuario no existe",extra_tags='error')
        return redirect('/backoffice/users')
    context = {'action':'view','usuario':user}
    return render(request,'account/users/permissions/form.html',context)


"""Logica de Relacion Usuario y Servicio
N usuarios tienen asignados N servicios
TODO: Preguntar si para hacer la asignación se necesita tener permisos sobre los servicios
TODO: Asignar servicios mediante formulario
TODO: Poder asignar un servicio, todos o solo los activos
TODO: Poder listar servicios mediante lista
TODO: Poder eliminar servicios del usuario
"""
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
def assign_services_to_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    return _change_user_servicios(request,user,action=ServicioAccionUser.ADD)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
def list_services_of_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    context = paginate_servicios_users(request,user)
    return render(request,'account/users/services/list.html', context)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
@require_POST
def remove_services_to_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    return _change_user_servicios(request,user,action=ServicioAccionUser.REMOVE)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
def list_cuadrantes_of_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    filtros,exclusiones = filter_cuadrantes(user)
    cuadrantes = Cuadrante.objects.filter(**filtros).exclude(**exclusiones).order_by('id')
    context = paginate_cuadrantes_users(request,cuadrantes,user)
    return render(request,'account/users/cuadrantes/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
def cuadrante_details(request:HttpRequest,user_id,cuadrante_id):
    user = User.objects.filter(UserID=user_id).first()
    cuadrante = Cuadrante.objects.filter(id=cuadrante_id).first()
    auth_errors = can_user_access_cuadrante(request,user,cuadrante)
    if auth_errors:
        return redirect(f"/backoffice/users/{user.UserID}/cuadrantes")
    context = {'usuario':user,'cuadrante':cuadrante,'action':'view'}
    return render(request,'account/users/cuadrantes/form.html',context)

@xframe_options_sameorigin
def show_cuadrante_pdf(request:HttpRequest,user_id,cuadrante_id):
    user = User.objects.filter(UserID=user_id).first()
    cuadrante = Cuadrante.objects.filter(id=cuadrante_id).first()
    auth_errors = can_user_access_cuadrante(request,user,cuadrante)
    if auth_errors:
        return redirect(f"/backoffice/users/{user.UserID}/cuadrantes")
    return FileResponse(cuadrante.file.open(), content_type='application/pdf')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
def create_cuadrante(request:HttpRequest,user_id):
    template = loader.get_template('account/users/cuadrantes/form.html')
    
    user = User.objects.filter(UserID=user_id).first()
    context = {'action':'create','usuario':user}

    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        archivo = request.FILES.get('archivo')
        errors = validate_cuadrante(request,nombre,archivo)
        print(f"errors={errors}")
        if errors:
            return HttpResponse(template.render(context,request))
        cuadrante = build_cuadrante(data={'file':archivo,'nombre':nombre,'user':user})
        return redirect(f"/backoffice/users/{user.UserID}/cuadrantes/{cuadrante.pk}")

    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))
    

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
def delete_cuadrante(request:HttpRequest,user_id,cuadrante_id):
    user = User.objects.filter(UserID=user_id).first()
    cuadrante = Cuadrante.objects.filter(id=cuadrante_id).first()
    auth_errors = can_user_access_cuadrante(request,user,cuadrante)
    if auth_errors:
        return redirect(f"/backoffice/users/{user.UserID}/cuadrantes")
    cuadrante.fecha_borrado = now()
    cuadrante.save()
    return redirect(f"/backoffice/users/{user.UserID}/cuadrantes")


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
def list_tareas_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    if not user:
        messages.error(request, "Usuario no encontrado", extra_tags='error')
        return redirect('/backoffice/users/')
    return redirect(f"/backoffice/tareas?usuario={user_id}")

def _create_or_modify_user(request:HttpRequest,user:User|None = None):

    template = loader.get_template('account/users/form.html')
    logged_user:User=request.user
    empresas = Empresa.objects.filter(usuario_creador_id=logged_user.UserID)
    categorias = User._meta.get_field('categoria').choices
    if user is None:
        context = {'action':'create','empresas':empresas,'categorias_choices':categorias}
    else:
        context = {'usuario':user,'action':'edit','categorias_choices':categorias,'empresas':empresas}

    if request.method == 'POST':
        usuario = request.POST.get('username','')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('password_confirm','')
        nombre = request.POST.get('nombre','')
        apellidos = request.POST.get('apellidos','')
        mail = request.POST.get('mail','')
        direccion = request.POST.get('direccion','')
        provincia = request.POST.get('provincia','')
        municipio = request.POST.get('municipio','')
        telefono = request.POST.get('telefono','')
        nif = request.POST.get('nif','')
        empresa = request.POST.get('empresa','')
        check_es_inspector = request.POST.get('es_inspector') == 'on'
        check_es_inspector_de_trabajo = request.POST.get('es_inspector_trabajo') == 'on'
        delegacion = request.POST.get('delegacion','')
        categoria = request.POST.get('categoria','ejecutivo')
        precio_hora = Decimal(request.POST.get('precio_hora') or 0.)
        always_track_gps = request.POST.get('track_gps') == 'on'
        comentarios = request.POST.get('comentarios','')


        errors:bool= False
        if user is None:
            errors = validate_user(request,usuario,password,confirm_password,nombre,apellidos,provincia,municipio, empresa)
        else:
            errors = validate_user_edit(request,usuario,nombre,apellidos,provincia,municipio, empresa)
        if errors:
            return HttpResponse(template.render(context,request))
        
        user_empresa = Empresa.objects.filter(EmpresaID=empresa).first()
        user = build_user(data={
            'username':usuario,
            'password':password,
            'first_name':nombre,
            'last_name':apellidos,
            'email':mail,
            'direccion':direccion,
            'provincia':provincia,
            'municipio':municipio,
            'nif':nif,
            'telefono':telefono,
            'categoria':categoria,
            'always_track_GPS':always_track_gps,
            'comentarios':comentarios,
            'empresa':user_empresa,
            'esInspector':check_es_inspector,
            'esInspector_parteTrabajo':check_es_inspector_de_trabajo,
            'precio_hora':precio_hora
        },user=user)
        return redirect("/backoffice/users/"+str(user.UserID))


    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))

class ServicioAccionUser(Enum):
    ADD = 'add',
    REMOVE = 'remove'


def _change_user_servicios(request:HttpRequest,user:User,action:ServicioAccionUser):
    template = loader.get_template('account/users/services/form.html')

    if action == ServicioAccionUser.ADD:
        allowed_servicios = Servicio.objects.filter(empresa=user.empresa)
        context = {'servicios':allowed_servicios,'usuario':user}
    elif action == ServicioAccionUser.REMOVE:
        context = {}


    if request.method == 'POST':
        servicios_ids = request.POST.getlist('servicios_ids')
        servicios = Servicio.objects.filter(ServicioID__in=servicios_ids)
        errors = validate_services_of_user(request,user,servicios)
        if errors:
            return  HttpResponse(template.render(context,request)) if action == ServicioAccionUser.ADD else redirect(f"/backoffice/users/{str(user.UserID)}/services")
        

        if action == ServicioAccionUser.ADD:
            user.servicios.add(*servicios)
        elif action == ServicioAccionUser.REMOVE:
             user.servicios.remove(*servicios)

        return redirect(f"/backoffice/users/{str(user.UserID)}/services")

    elif request.method == 'GET':
        #ADD Only
        return HttpResponse(template.render(context,request))