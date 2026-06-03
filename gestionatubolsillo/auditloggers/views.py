from django.shortcuts import render
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import User, can_access_backoffice
from clientes.models import user_client
from .models import AuditLog

# Create your views here.
@login_required
@user_passes_test(can_access_backoffice)
def list_logs(request:HttpRequest):
    
    #En teoria mostrar todos los auditLogs asociados a la actividad de la empresa o de las empresas creadas por el usuario q

    
    pass
