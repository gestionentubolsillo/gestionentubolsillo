from django.shortcuts import render
from django.http import HttpRequest,HttpResponse
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.http import require_GET, require_http_methods
from django.template import loader
from users.models import User, can_access_backoffice
#Mucha info sale mas rentable importarlo todo
from partes.models import Parte_Inspeccion,can_view_parte_inspeccion,can_CRUD_parte_inspeccion
from clientes.models import Cliente

from partes.paginators import paginate_informes
from partes.filters import filtra_partes_inspeccion
# Create your views here.
DEFAULT_PAGINATION_PARTES = 25
 

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_inspeccion)
@require_GET
def list_partes_inspeccion(request:HttpRequest):
    filtros, exclusiones = filtra_partes_inspeccion(request)
    partes = Parte_Inspeccion.objects.filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'list_inspeccion.html',context)

#Para la inspeccion el inspector que crea el parte no necesita tener acceso al backoffice
"""
@DEPRECATED
Este método de momento no se trabajará
"""
@login_required
@user_passes_test(can_CRUD_parte_inspeccion)
@require_http_methods(["GET","POST"])
def create_parte_inspeccion(request:HttpRequest):
    user:User = request.user
    template = loader.get_template('informes/inspeccion/form.html')
    allowed_users = User.objects.filter(cuenta=user.cuenta, is_active=True)
    allowed_clientes = Cliente.objects.filter(cuenta=user.cuenta)
    context = {'usuarios':allowed_users,'clientes':allowed_clientes}
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))


