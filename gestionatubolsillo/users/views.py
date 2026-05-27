from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import User, can_access_backoffice, can_view_users, can_CRUD_users
from django.core.paginator import Paginator
from django.template import loader
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.contrib import messages
from empresas.models import Empresa
# Create your views here.

MIN_CHARS_PASSWORD = 8
DEFAULT_PAGINATION_USERS = 25

def validate_user(request : HttpRequest,
                  usuario,password,nombre,apellidos,
                  provincia,municipio,empresa)->bool:
    errors = False
    global MIN_CHARS_PASSWORD
    if usuario == '':
        messages.error(request,"El nombre de usuario no puede estar vacío", extra_tags='error')
        errors = True
    if password == '':
        messages.error(request,"La contraseña no puede estar vacía",extra_tags='error')
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
    empresa_exists = Empresa.objects.filter(id=empresa).first()
    if not empresa_exists:
        messages.error(request,"El usuario debe estar asociado a una empresa",extra_tags='error')
        errors = True
    return errors

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
def create_user(request:HttpRequest):
    if request.method == 'POST':
        usuario = request.POST.get('username','')
        password = request.POST.get('password', '')
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

        errors = validate_user(request,usuario,password,nombre,apellidos,provincia,municipio, empresa)
        user_empresa = Empresa.objects.filter(id=empresa).first()

        if not errors:
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
            user.save()
            return redirect('/backoffice/users')
    elif request.method == 'GET':
        template = loader.get_template('create_form.html')
        context = {}
        return HttpResponse(template.render(context,request))


@login_required
@user_passes_test(can_access_backoffice)
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
    return render(request,'list.html', context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
def user_details(request:HttpRequest,user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        messages.error(request,"El usuario no existe",extra_tags='error')
        return redirect('/backoffice/users')
    template = loader.get_template('crud_form.html')
    pass

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
def edit_user(request:HttpRequest,user_id):
    user = User.objects.filter(id=user_id).first()
    if request.method == 'POST':
        usuario = request.POST.get('username','')
        password = request.POST.get('password', '')
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

        errors = validate_user(request,usuario,password,nombre,apellidos,provincia,municipio, empresa)
        user_empresa = Empresa.objects.filter(id=empresa).first()

        if errors:
            return redirect("/backoffice/users/edit/"+str(user.UserID))
        
        user.username = usuario
        user.password = password
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
        template = loader.get_template('crud_form.html')
        context = {
            'user':user
        }
        return HttpResponse(template.render(context,request))

    pass



@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
def delete_user(request:HttpRequest,user_id):
    user = User.objects.filter(id=user_id).first()
    user.delete()
    messages.success(request,"El usuario ha sido eliminado correctamente",extra_tags='success')
    return redirect('/backoffice/users')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
def alter_user_permissions(request:HttpRequest,user_id):
    user = User.objects.filter(id=user_id).first()
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
        template = loader.get_template('perms_form.html')
        context = {
            'user':user
        }
        return HttpResponse(template.render(context,request))