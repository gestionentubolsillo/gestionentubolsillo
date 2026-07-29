from django.http import HttpRequest
from django.shortcuts import render

from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.http import require_GET

from users.models import can_access_backoffice
from partes.models import Informe_Acuda,can_view_informes

from partes.filters import filtra_informes_acuda
from partes.paginators import paginate_informes



ACUDA_LIST_TEMPLATE = 'informes/acuda/list.html'

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
@require_GET
def list_informes_informe_acuda_cliente(request:HttpRequest):
    filtros, exclusiones = filtra_informes_acuda(request)
    partes = Informe_Acuda.objects.filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,ACUDA_LIST_TEMPLATE,context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
@require_GET
def list_informes_informe_acuda_tecnico(request:HttpRequest):
    filtros, exclusiones = filtra_informes_acuda(request)
    partes = Informe_Acuda.objects.filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,ACUDA_LIST_TEMPLATE,context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
@require_GET
def list_informes_informe_acuda(request:HttpRequest):
    filtros, exclusiones = filtra_informes_acuda(request)
    partes = Informe_Acuda.objects.filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,ACUDA_LIST_TEMPLATE,context)