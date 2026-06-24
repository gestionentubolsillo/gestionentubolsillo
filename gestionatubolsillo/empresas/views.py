from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import can_access_backoffice
from .models import Empresa, can_CRUD_empresas, can_view_empresas
from django.template import loader
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.core.paginator import Paginator
from users.models import User

from .filters import filtra_empresa
from .paginators import paginate_empresas
from .validators import validate_empresa
from .builders import build_empresa

# Create your views here.

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_empresas)
def create_empresa(request:HttpRequest):
    return _create_or_modify_empresa(request)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_empresas)
def list_empresas(request:HttpRequest):
    #TODO: Cambiar el filtro a cuenta a la que pertenece la empresa
    filtros, exclusiones = filtra_empresa(request)
    list_empresas = Empresa.objects.filter(**filtros).exclude(**exclusiones).order_by('EmpresaID')
    context = paginate_empresas(request,list_empresas)
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
    return _create_or_modify_empresa(request,empresa)
    

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_empresas)
def delete_empresa(request:HttpRequest,empresa_id):
    empresa = Empresa.objects.filter(EmpresaID=empresa_id).first()
    empresa.delete()
    messages.success(request,"La empresa se ha eliminado con éxito",extra_tags='success')
    return redirect('/backoffice/empresas')


def _create_or_modify_empresa(request:HttpRequest,empresa:Empresa | None = None):
    template = loader.get_template('empresas/form.html')
    if empresa is None:
        context = {'action':'create'}
    else:
        context = {'empresa': empresa,'action': 'edit'}

    if request.method == 'POST':
        nombre = request.POST.get('name','')
        paquete = request.POST.get('paquete','')
        errors = validate_empresa(request,nombre,paquete)
        if errors:
            return HttpResponse(template.render(context,request))
        user:User = request.user
        build_empresa(data={'nombre':nombre,'paquete':paquete},creador=user,empresa=empresa)
        return redirect('/backoffice/empresas')
        

    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))