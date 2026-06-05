from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import can_access_backoffice
from .models import Empresa, can_CRUD_empresas, can_view_empresas
from django.template import loader
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.core.paginator import Paginator
from users.models import User

# Create your views here.
DEFAULT_PAGINATION_EMPRESAS = 25

def validate_empresa(request:HttpRequest,nombre,paquete)->bool:
    errors = False
    if nombre == '' or paquete == '':
        messages.error(request,"Todos los campos son obligatorios",extra_tags='error')
    return errors

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_empresas)
def create_empresa(request:HttpRequest):
    user:User = request.user
    if request.method == 'POST':
        nombre = request.POST.get('name','')
        paquete = request.POST.get('paquete','')
        errors = validate_empresa(request,nombre,paquete)
        if errors:
            template = loader.get_template('empresas/form.html')
            context = {'action':'create'}
            return HttpResponse(template.render(context,request))

        empresa = Empresa()
        empresa.nombre = nombre
        empresa.paquete = paquete
        empresa.usuario_creador = user
        empresa.save()
        return redirect('/backoffice/empresas')
    elif request.method == 'GET':
        template = loader.get_template('empresas/form.html')
        context = {'action':'create'}
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_empresas)
def list_empresas(request:HttpRequest):
    #Listar todas las empresas creadas por el usuario mas la empresa a la que pertenece
    user:User = request.user
    empresa_usuario:Empresa = user.empresa
    list_empresas = Empresa.objects.filter(
        usuario_creador_id = user.UserID
    ).exclude(EmpresaID=empresa_usuario.EmpresaID)

    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_EMPRESAS
    #La empresa del usuario siempre va a aparecer por lo que se debe mostrar 1 empresa menos de paginacion
    n_empresas :int = request.GET.get('n_empresas', DEFAULT_PAGINATION_EMPRESAS) -1
    paginacion = Paginator(list_empresas,n_empresas)
    page_obj = paginacion.get_page(n_pagina)

    context = {
        'empresa_usuario' : empresa_usuario,
        'empresas': page_obj,
        'page_obj': page_obj,
        'page': n_pagina,
        'n_empresas':n_empresas+1,
    }
    return render(request,'empresas/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_empresas)
def details_empresa(request,empresa_id):
    empresa = Empresa.objects.filter(EmpresaID=empresa_id).first()
    if not empresa:
        messages.error(request,"La empresa no existe",extra_tags='error')
        return redirect('backoffice/empresas')
    context = {
        'empresa':empresa,
        'action':'view'
    }
    return render(request,'empresas/form.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_empresas)
def edit_empresa(request : HttpRequest,empresa_id):
    empresa = Empresa.objects.filter(EmpresaID=empresa_id).first()
    if request.method == 'POST':
        nombre = request.POST.get('name','')
        paquete = request.POST.get('paquete','')
        errors = validate_empresa(request,nombre,paquete)
        if errors:
            return redirect('/backoffice/empresas/edit/'+str(empresa.EmpresaID))
        empresa.nombre = nombre
        empresa.paquete = paquete
        empresa.save()
        return redirect('/backoffice/empresas/'+str(empresa.EmpresaID))
    elif request.method == 'GET':
        template = loader.get_template('empresas/form.html')
        context = {
            'empresa': empresa,
            'action': 'edit'
        }
        return HttpResponse(template.render(context,request))
    

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_empresas)
def delete_empresa(request:HttpRequest,empresa_id):
    empresa = Empresa.objects.filter(EmpresaID=empresa_id).first()
    empresa.delete()
    messages.success(request,"La empresa se ha eliminado con éxito",extra_tags='success')
    return redirect('/backoffice/empresas')