from django.shortcuts import render
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from users.models import User, can_access_backoffice
from .models import AuditLog

DEFAULT_PAGINATION_AUDIT = 50

# Create your views here.

def admin_required(user:User)-> bool:
    return user.is_admin

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(admin_required)
@require_GET
def list_logs(request:HttpRequest):
    
    logged_user : User = request.user
    logs = AuditLog.objects.filter(cuenta_id=logged_user.cuenta.pk).order_by('-fecha')

    n_pagina = request.GET.get('page', 1)
    n_logs = request.GET.get('n_logs', DEFAULT_PAGINATION_AUDIT)
    paginator = Paginator(logs, n_logs)
    page_obj = paginator.get_page(n_pagina)

    context = {
        'logs': page_obj,
        'page_obj': page_obj,
        'n_pagina': n_pagina,
        'n_logs': n_logs,
    }

    return render(request, 'audit/list.html', context)
