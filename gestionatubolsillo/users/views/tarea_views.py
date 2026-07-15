from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import User,can_access_backoffice, can_view_users
from django.http import HttpRequest
from django.contrib import messages
from django.views.decorators.http import require_GET

# Create your views here.

from users.validators import validate_account_access

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
@require_GET
def list_tareas_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    if not user:
        messages.error(request, "Usuario no encontrado", extra_tags='error')
        return redirect('/backoffice/users/')

    auth_error = validate_account_access(request, user)
    if auth_error:
        return auth_error

    return redirect(f"/backoffice/tareas?usuario={user_id}")