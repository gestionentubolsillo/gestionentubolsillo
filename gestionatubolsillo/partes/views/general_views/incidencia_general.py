from django.http import HttpRequest
from django.shortcuts import render

from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.http import require_GET

from users.models import can_access_backoffice
from partes.models import Parte_Incidencia, can_view_informes

from partes.filters import filtra_partes_incidencia
from partes.paginators import paginate_informes


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
@require_GET
def list_informes_informe_incidencia(request:HttpRequest):
    filtros, exclusiones = filtra_partes_incidencia(request)
    partes = Parte_Incidencia.objects.filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'informes/incidencia/list.html',context)