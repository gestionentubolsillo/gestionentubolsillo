from django.shortcuts import render, redirect
from django.http import HttpRequest,HttpResponse, JsonResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required,user_passes_test
from django.template import loader
from django.core.paginator import Paginator
from users.models import User, can_access_backoffice
from django.contrib import messages
#Mucha info sale mas rentable importarlo todo
from .models import *
from empresas.models import Empresa
from clientes.models import Cliente
from servicios.models import Servicio

from .paginators import paginate_informes

# Create your views here.
DEFAULT_PAGINATION_PARTES = 25
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
def dashboard_informes(request:HttpRequest):
    #Vista que lista los diferentes enlaces para consulta de los diferentes tipos de informe
    context = {}
    return render(request,'informes/general.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_trabajo)
def list_partes_trabajo(request:HttpRequest):
    empresa_id = request.GET.get('empresa_id')
    partes = Parte_Trabajo.objects.filter(empresa_id = empresa_id).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'list_trabajo.html',context)
    


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_incidencia)
def list_partes_incidencia(request:HttpRequest):
    empresa_id = request.GET.get('empresa_id')
    partes = Parte_Incidencia.objects.filter(empresa_id = empresa_id).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'list_incidencia.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_inspeccion)
def list_partes_inspeccion(request:HttpRequest):
    empresa_id = request.GET.get('empresa_id')
    partes = Parte_Inspeccion.objects.filter(empresa_id = empresa_id).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'list_inspeccion.html',context)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_acuda)
def list_inf_acuda(request:HttpRequest):
    empresa_id = request.GET.get('empresa_id')
    partes = Informe_Acuda.objects.filter(empresa_id = empresa_id).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'list_acuda.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_parte_trabajo)
def create_parte_trabajo(request:HttpRequest):
    pass

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_parte_incidencia)
def create_parte_incidencia(request:HttpRequest):
    pass


#Para la inspeccion el inspector que crea el parte no necesita tener acceso al backoffice
@login_required
@user_passes_test(can_CRUD_parte_inspeccion)
def create_parte_inspeccion(request:HttpRequest):
    pass

@login_required
@user_passes_test(can_CRUD_acuda)
def create_inf_acuda(request:HttpRequest):
    pass

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_parte_trabajo)
def add_actividad_to_parte_trabajo(request:HttpRequest,p_trabajo_id):
    pass

#Necesario indagar más en estas caracteristicas
def view_parte_trabajo(request:HttpRequest):
    context = {}
    return render(request,'informes/trabajo/pdfview.html',context)

def view_parte_incidencia(request:HttpRequest):
    context = {}
    return render(request,'informes/incidencia/pdfview.html',context)

def view_parte_acuda(request:HttpRequest):
    context = {}
    return render(request,'informes/acuda/pdfview.html',context)



#TOREFACTOR: Hacer que solo muestre los clientes cuya cuenta es la del usuario logueado y verificar que los servicios que se muestran tambien pertenecen a la cuenta del usuario logueado 
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
def list_informes_informe_trabajo(request:HttpRequest):
    clientes = Cliente.objects.all()
    context = {'clientes': clientes}
    return render(request,'informes/trabajo/list_informes.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
def list_informes_informe_trabajo_horas_cliente(request:HttpRequest):
    clientes = Cliente.objects.all()
    context = {'clientes': clientes}
    return render(request,'informes/trabajo/list_horas_cliente.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
def list_informes_informe_trabajo_horas_tecnico(request:HttpRequest):
    clientes = Cliente.objects.all()
    context = {'clientes': clientes}
    return render(request,'informes/trabajo/list_horas_tecnico.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
def list_informes_informe_trabajo_resumen(request:HttpRequest):
    clientes = Cliente.objects.all()
    context = {'clientes': clientes}
    return render(request,'informes/trabajo/list_resumen.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
def get_servicios_por_cliente(request:HttpRequest,cliente_id):
    #Vista que devuelve los servicios asociados a un cliente, para ser usados en un select de un formulario
    servicios = Servicio.objects.filter(clientes__ClienteID = cliente_id).values('ServicioID','nombre').distinct()
    return JsonResponse(list(servicios),safe=False)