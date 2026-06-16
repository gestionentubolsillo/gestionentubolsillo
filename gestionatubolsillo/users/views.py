from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import User, can_access_backoffice, can_view_users, can_CRUD_users
from django.core.paginator import Paginator
from django.template import loader
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.contrib import messages
from empresas.models import Empresa
from decimal import Decimal
from servicios.models import can_CRUD_servicios, Servicio
from django.views.decorators.http import require_POST
from django.db.models.manager import BaseManager
# Create your views here.

MIN_CHARS_PASSWORD = 8
DEFAULT_PAGINATION_USERS = 25
DEFAULT_PAGINATION_USER_SERVICES = 25

def validate_user(request : HttpRequest,
                  usuario,password,confirm_password,nombre,apellidos,
                  provincia,municipio,empresa)->bool:
    errors = False
    global MIN_CHARS_PASSWORD
    if usuario == '':
        messages.error(request,"El nombre de usuario no puede estar vacío", extra_tags='error')
        errors = True
    if password == '':
        messages.error(request,"La contraseña no puede estar vacía",extra_tags='error')
        errors = True
    if password != confirm_password:
        messages.error(request,"Las contraseñas no coinciden",extra_tags='error')
        errors = True
    if len(password) < MIN_CHARS_PASSWORD:
        messages.error(request,f"La contraseña debe tener al menos {MIN_CHARS_PASSWORD} caracteres",extra_tags='error')
        errors = True
    if nombre == '' or apellidos == '':
        messages.error(request,"El nombre o apellidos no pueden estar vacíos",extra_tags='error')
        errors = True
    if provincia == '':
        messages.error(request,"Debe indicar la provincia a la que pertenece",extra_tags='error')
        errors = True
    if municipio == '':
        messages.error(request,"Debe indicar el municipio al que pertenece",extra_tags='error')
        errors = True
    empresa_exists = Empresa.objects.filter(EmpresaID=empresa).first()
    if not empresa_exists:
        messages.error(request,"El usuario debe estar asociado a una empresa",extra_tags='error')
        errors = True
    return errors

def validate_user_edit(request : HttpRequest,
                  usuario,nombre,apellidos,
                  provincia,municipio,empresa)->bool:
    errors = False
    if usuario == '':
        messages.error(request,"El nombre de usuario no puede estar vacío", extra_tags='error')
        errors = True
    if nombre == '' or apellidos == '':
        messages.error(request,"El nombre o apellidos no pueden estar vacíos",extra_tags='error')
        errors = True
    if provincia == '':
        messages.error(request,"Debe indicar la provincia a la que pertenece",extra_tags='error')
        errors = True
    if municipio == '':
        messages.error(request,"Debe indicar el municipio al que pertenece",extra_tags='error')
        errors = True
    empresa_exists = Empresa.objects.filter(EmpresaID=empresa).first()
    if not empresa_exists:
        messages.error(request,"El usuario debe estar asociado a una empresa",extra_tags='error')
        errors = True
    return errors

def validate_services_of_user(request:HttpRequest,user:User,servicios:BaseManager[Servicio])->bool:
    empresa : Empresa = user.empresa
    errors = False
    servicios_de_diferente_empresa = servicios.exclude(empresa=empresa)
    if servicios_de_diferente_empresa.exists():
        messages.error(request,"Los servicios deben pertenecer a la misma empresa que el usuario para ser asignados",extra_tags='error')
        errors = True
    return errors

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
def create_user(request:HttpRequest):
    logged_user:User = request.user
    empresas = Empresa.objects.filter(usuario_creador_id=logged_user.UserID)
    categorias = User._meta.get_field('categoria').choices
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

        errors = validate_user(request,usuario,password,confirm_password,nombre,apellidos,provincia,municipio, empresa)
        user_empresa = Empresa.objects.filter(EmpresaID=empresa).first()

        if errors:
            template = loader.get_template('account/users/form.html')
            context = {
                'action':'create',
                'empresas':empresas,
                'categorias_choices':categorias
            }
            return HttpResponse(template.render(context,request))
        user = User.objects.create_user(
                username=usuario,
                password=password,
                first_name = nombre,
                last_name = apellidos,
                email = mail,
                direccion = direccion,
                telefono = telefono,
                nif = nif,
                provincia = provincia,
                municipio = municipio,
                empresa = user_empresa,
                esInspector = check_es_inspector,
                esInspector_parteTrabajo = check_es_inspector_de_trabajo,
                always_track_GPS = always_track_gps,
                categoria = categoria,
                precio_hora = precio_hora,
                comentarios = comentarios
        )
        user.set_password(password)
        user.save()
        return redirect('/backoffice/users')
    elif request.method == 'GET':
        template = loader.get_template('account/users/form.html')
        context = {
            'action':'create',
            'empresas':empresas,
            'categorias_choices':categorias
        }
        return HttpResponse(template.render(context,request))


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
def lista_users(request:HttpRequest):
    usuario : User = request.user
    empresa_de_usuario :Empresa = usuario.empresa

    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_USERS
    n_usuarios = request.GET.get('n_users', DEFAULT_PAGINATION_USERS)
    filtro_empresa = request.GET.get('empresa',empresa_de_usuario.EmpresaID)

    lista_usuarios = User.objects.filter(
        empresa_id=filtro_empresa
    )

    paginacion = Paginator(lista_usuarios, n_usuarios)
    page_obj = paginacion.get_page(n_pagina)

    context = {
        'usuarios': page_obj,
        'page_obj': page_obj,
        'page': n_pagina,
        'n_users':n_usuarios
    }
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
    logged_user:User = request.user
    empresas = Empresa.objects.filter(usuario_creador_id=logged_user.UserID)
    categorias = User._meta.get_field('categoria').choices
    #Password formulario a parte de reseteo de password, no debe ser editado por usuario
    if request.method == 'POST':
        usuario = request.POST.get('username','')
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
        precio_hora = request.POST.get('precio_hora', 0.)
        always_track_gps = request.POST.get('track_gps') == 'on'
        comentarios = request.POST.get('comentarios','')

        errors = validate_user_edit(request,usuario,nombre,apellidos,provincia,municipio, empresa)
        user_empresa = Empresa.objects.filter(EmpresaID=empresa).first()

        if errors:
            return redirect("/backoffice/users/edit/"+str(user.UserID))
        
        user.username = usuario
        user.first_name = nombre
        user.last_name = apellidos
        user.email = mail
        user.direccion = direccion
        user.provincia = provincia
        user.municipio = municipio
        user.telefono = telefono
        user.nif = nif
        user.empresa = user_empresa
        user.esInspector = check_es_inspector
        user.esInspector_parteTrabajo = check_es_inspector_de_trabajo
        user.categoria = categoria
        user.precio_hora = precio_hora
        user.always_track_GPS = always_track_gps
        user.comentarios = comentarios
        user.save()
        return redirect("/backoffice/users/"+str(user.UserID))
    elif request.method == 'GET':
        template = loader.get_template('account/users/form.html')
        context = {
            'usuario':user,
            'action':'edit',
            'categorias_choices':categorias,
            'empresas':empresas
        }
        return HttpResponse(template.render(context,request))

    pass



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

        user.permisos_almacen = p_almacen
        user.permisos_central_receptora = p_central
        user.permisos_clientes = p_clientes
        user.permisos_configuracion = p_config
        user.permisos_empresas = p_empresas
        user.permisos_informes = p_informes
        user.permisos_informes_acuda = p_acuda
        user.permisos_mantenimientos = p_mantenimiento
        user.permisos_medios_auxiliares = p_medio_aux
        user.permisos_partes_incidencias = p_parte_incidencia
        user.permisos_partes_inspeccion = p_parte_inspeccion
        user.permisos_partes_trabajo = p_parte_trabajo
        user.permisos_servicios_NFC = p_servicio_NFC
        user.permisos_sugerencias = p_sugerencias
        user.permisos_tareas = p_tareas
        user.permisos_usuario = p_usuario
        user.has_dashboard_access = p_dashboard
        user.has_login_access = p_login
        user.can_view_own_partes_trabajo = p_view_self_trabajo
        user.save()
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
    if request.method == 'POST':
        servicios_ids = request.POST.getlist('servicios_ids')
        servicios = Servicio.objects.filter(ServicioID__in=servicios_ids)
        errors = validate_services_of_user(request,user,servicios)
        if errors:
            template = loader.get_template('account/users/services/form.html')
            allowed_servicios = Servicio.objects.filter(empresa=user.empresa)
            context = {'servicios':allowed_servicios,'usuario':user}
            return HttpResponse(template.render(context,request))
        
        user.servicios.add(*servicios)
        return redirect(f"/backoffice/users/{str(user_id)}/services")

    if request.method == 'GET':
        template = loader.get_template('account/users/services/form.html')
        allowed_servicios = Servicio.objects.filter(empresa=user.empresa)
        context = {'servicios':allowed_servicios,'usuario':user}
        return HttpResponse(template.render(context,request))


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
def list_services_of_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_USER_SERVICES
    n_services = request.GET.get('n_services', DEFAULT_PAGINATION_USER_SERVICES)

    servicios = Servicio.objects.filter(users=user)

    paginacion = Paginator(servicios, n_services)
    page_obj = paginacion.get_page(n_pagina)

    context = {
        'usuario':user,
        'servicios': page_obj,
        'page_obj': page_obj,
        'page': n_pagina,
        'n_services':n_services
    }
    return render(request,'account/users/services/list.html', context)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
@require_POST
def remove_services_to_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    servicios_ids = request.POST.getlist('servicios_ids')
    servicios = Servicio.objects.filter(ServicioID__in=servicios_ids)
    errors = validate_services_of_user(request,user,servicios)
    if errors:
            return redirect(f"/backoffice/users/{str(user_id)}/services")
    user.servicios.remove(*servicios)
    return redirect(f"/backoffice/users/{str(user_id)}/services")