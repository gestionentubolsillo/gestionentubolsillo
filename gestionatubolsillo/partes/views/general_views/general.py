from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.http import require_GET

from users.models import can_access_backoffice
from partes.models import can_view_informes, can_CRUD_parte_trabajo
from servicios.models import Servicio


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
@require_GET
def dashboard_informes(request:HttpRequest):
    #Vista que lista los diferentes enlaces para consulta de los diferentes tipos de informe
    context = {}
    return render(request,'informes/general.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
@require_GET
def get_servicios_por_cliente(request:HttpRequest,cliente_id):
    #Vista que devuelve los servicios asociados a un cliente, para ser usados en un select de un formulario
    servicios = Servicio.objects.filter(clientes__ClienteID = cliente_id).values('ServicioID','nombre').distinct()
    return JsonResponse(list(servicios),safe=False)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_parte_trabajo)
@require_GET
def get_servicios_por_cliente_y_usuario(request:HttpRequest,cliente_id,usuario_id):
    #Vista que devuelve los servicios asociados a un cliente y a un usuario, para ser usados en un select de formulario creacion de parte de trabajo
    servicios = Servicio.objects.filter(clientes__ClienteID = cliente_id, users__UserID = usuario_id).values('ServicioID','nombre').distinct()
    return JsonResponse(list(servicios),safe=False)