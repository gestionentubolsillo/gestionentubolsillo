from django.shortcuts import redirect, render
from django.http import HttpRequest,HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import can_access_backoffice, User
from .models import Mantenimiento_DOC, Mantenimiento_DOC_GRUPO,Mantenimiento_DOC_CAMPO, can_view_mantenimientos, can_CRUD_mantenimientos
from django.core.paginator import Paginator
from django.template import loader
from django.contrib import messages
from django.utils.timezone import now
from empresas.models import Empresa
# Create your views here.

def validate_mantenimiento(request:HttpRequest,nombre,empresa_id)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe indicar un nombre al documento de mantenimiento",extra_tags='error')
        errors = True
    empresa = Empresa.objects.filter(id=empresa_id).first()
    if not empresa:
        messages.error(request,"Debe indicar una empresa válida para el documento de mantenimiento",extra_tags='error')
        errors = True
    return errors

def validate_grupo(request:HttpRequest,nombre)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe indicar un nombre al grupo del documento de mantenimiento",extra_tags='error')
        errors = True
    return errors

def validate_campo(request:HttpRequest,nombre,tipo_de_campo)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe indicar un nombre al campo del documento de mantenimiento",extra_tags='error')
        errors = True
    if tipo_de_campo not in ['texto', 'valores_predefinidos', 'checkbox', 'checkbox_dos_estados']:
        messages.error(request,"Debe indicar un tipo de campo válido",extra_tags='error')
        errors = True
    return errors

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_mantenimientos)
def list_mantenimientos(request:HttpRequest):
    user:User = request.user
    empresa = user.empresa
    mantenimientos = Mantenimiento_DOC.objects.filter(empresa=empresa).order_by('-fecha_creacion')
    n_pagina = request.GET.get('page', 1)
    n_mantenimientos = request.GET.get('n_mantenimientos', 25)
    paginator = Paginator(mantenimientos, n_mantenimientos)
    page_obj = paginator.get_page(n_pagina)
    context = {
        'mantenimientos': page_obj,
        'page_obj': page_obj,
        'n_pagina': n_pagina,
        'n_mantenimientos': n_mantenimientos
    }
    return render(request,'list.html', context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_mantenimientos)
def create_mantenimiento(request:HttpRequest):
    if request.method == 'POST':
        created_at = now()
        nombre = request.POST.get('nombre','')
        empresa_id = request.POST.get('empresa_id')
        errors = validate_mantenimiento(request,nombre,empresa_id)
        if errors:
            template = loader.get_template('form.html')
            context = {}
            return HttpResponse(template.render(context,request))
        user:User = request.user
        empresa = Empresa.objects.filter(id=empresa_id).first()
        mantenimiento = Mantenimiento_DOC()
        mantenimiento.nombre = nombre
        mantenimiento.fecha_creacion = created_at
        mantenimiento.usuario_creador = user
        mantenimiento.empresa = empresa
        mantenimiento.save()
        return redirect('backoffice/mantenimientos')
    elif request.method == 'GET':
        template = loader.get_template('form.html')
        context = {}
        return HttpResponse(template.render(context,request))
    
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_mantenimientos)
def create_grupo(request:HttpRequest, mantenimiento_id):
    if request.method == 'POST':
        created_at = now()
        nombre = request.POST.get('nombre','')
        ordendegrupo = request.POST.get('orden_de_grupo',0)
        errors = validate_grupo(request,nombre)
        if errors:
            template = loader.get_template('form.html')
            context = {}
            return HttpResponse(template.render(context,request))
        user:User = request.user
        mantenimiento = Mantenimiento_DOC.objects.filter(id=mantenimiento_id).first()
        grupo = Mantenimiento_DOC_GRUPO()
        grupo.nombre = nombre
        grupo.orden_de_grupo = ordendegrupo
        grupo.fecha_creacion = created_at
        grupo.usuario_creador = user
        grupo.documento_mantenimiento = mantenimiento
        grupo.save()
        return redirect('backoffice/mantenimientos')
    elif request.method == 'GET':
        template = loader.get_template('form.html')
        context = {}
        return HttpResponse(template.render(context,request))
    
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_mantenimientos)
def create_campo(request:HttpRequest, mantenimiento_id):
    if request.method == 'POST':
        created_at = now()
        nombre = request.POST.get('nombre','')
        tipo_de_campo = request.POST.get('tipo_de_campo','texto')
        texto_ayuda = request.POST.get('texto_ayuda','')
        orden_de_campo = request.POST.get('orden_de_campo',0)
        grupo_id = request.POST.get('grupo_id')
        errors = validate_campo(request,nombre,tipo_de_campo)
        if errors:
            template = loader.get_template('form.html')
            context = {}
            return HttpResponse(template.render(context,request))
        user:User = request.user
        grupo = Mantenimiento_DOC_GRUPO.objects.filter(id=grupo_id).first()
        campo = Mantenimiento_DOC_CAMPO()
        campo.nombre = nombre
        campo.tipo_de_campo = tipo_de_campo
        campo.texto_ayuda = texto_ayuda
        campo.orden_de_campo = orden_de_campo
        campo.fecha_creacion = created_at
        campo.usuario_creador = user
        if grupo:
            campo.grupo_documento = grupo
        campo.save()
        return redirect('backoffice/mantenimientos')
    elif request.method == 'GET':
        template = loader.get_template('form.html')
        context = {}
        return HttpResponse(template.render(context,request))
    
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_mantenimientos)
def delete_grupo_mantenimiento(request:HttpRequest, grupo_id):
    grupo = Mantenimiento_DOC_GRUPO.objects.filter(id=grupo_id).first()
    grupo.delete()
    messages.success(request, 'El grupo del documento de mantenimiento ha sido borrado exitosamente.',extra_tags='success')
    return redirect('backoffice/mantenimientos')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_mantenimientos)
def delete_campo_mantenimiento(request:HttpRequest, campo_id):
    campo = Mantenimiento_DOC_CAMPO.objects.filter(id=campo_id).first()
    campo.delete()
    messages.success(request, 'El campo del documento de mantenimiento ha sido borrado exitosamente.',extra_tags='success')
    return redirect('backoffice/mantenimientos')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_mantenimientos)
def delete_mantenimiento(request:HttpRequest, mantenimiento_id):
    mantenimiento = Mantenimiento_DOC.objects.filter(id=mantenimiento_id).first()
    mantenimiento.delete()
    messages.success(request, 'El documento de mantenimiento ha sido borrado exitosamente.',extra_tags='success')
    return redirect('backoffice/mantenimientos')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_mantenimientos)
def edit_grupo_mantenimiento(request:HttpRequest, grupo_id):
    grupo = Mantenimiento_DOC_GRUPO.objects.filter(id=grupo_id).first()
    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        orden_de_grupo = request.POST.get('orden_de_grupo',0)
        errors = validate_grupo(request,nombre)
        if errors:
            template = loader.get_template('form.html')
            context = {'grupo': grupo}
            return HttpResponse(template.render(context,request))
        grupo.nombre = nombre
        grupo.orden_de_grupo = orden_de_grupo
        grupo.save()
        return redirect('backoffice/mantenimientos')
    elif request.method == 'GET':
        template = loader.get_template('form.html')
        context = {'grupo': grupo}
        return HttpResponse(template.render(context,request))
    
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_mantenimientos)
def edit_campo_mantenimiento(request:HttpRequest, campo_id):
    campo = Mantenimiento_DOC_CAMPO.objects.filter(id=campo_id).first()
    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        tipo_de_campo = request.POST.get('tipo_de_campo','texto')
        texto_ayuda = request.POST.get('texto_ayuda','')
        orden_de_campo = request.POST.get('orden_de_campo',0)
        errors = validate_campo(request,nombre,tipo_de_campo)
        if errors:
            template = loader.get_template('form.html')
            context = {'campo': campo}
            return HttpResponse(template.render(context,request))
        campo.nombre = nombre
        campo.tipo_de_campo = tipo_de_campo
        campo.texto_ayuda = texto_ayuda
        campo.orden_de_campo = orden_de_campo
        campo.save()
        return redirect('backoffice/mantenimientos')
    elif request.method == 'GET':
        template = loader.get_template('form.html')
        context = {'campo': campo}
        return HttpResponse(template.render(context,request))
    
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_mantenimientos)
def mantenimiento_details(request:HttpRequest,mantenimiento_id):
    #TODO: indagar en el funcionamiento de la app a refactorizar para saber que detalles mostrar
    #Quizas los detalles sea una lista de envios de mantenimiento realizados mediante ese doc por los diferentes usuarios
    mantenimiento = Mantenimiento_DOC.objects.filter(id=mantenimiento_id).first()
    if not mantenimiento:
        messages.error(request,"El documento de mantenimiento no existe",extra_tags='error')
        return redirect('backoffice/mantenimientos')
    context = {
        'mantenimiento':mantenimiento,
        'action':'view'
    }
    template = loader.get_template('details.html')
    return HttpResponse(template.render(context,request))