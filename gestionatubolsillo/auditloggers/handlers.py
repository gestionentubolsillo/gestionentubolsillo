from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.http import HttpRequest
from .models import AuditLog

from almacen.models import Almacen_Item

def get_client_ip(request:HttpRequest):
    ip = request.META.get('REMOTE_ADDR')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    return ip


def save_log(request:HttpRequest,apartado,accion,id_user=None,id_client=None)->None:
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request is not None else ''

    device_name = ''
    browser_name_version = ''
    if user_agent:
        browser_name_version = user_agent[:40]
        # Use the first part of the UA string as a simple device identifier.
        if ')' in user_agent:
            device_name = user_agent.split(')')[0].lstrip('(')[:30]
        else:
            device_name = user_agent[:30]

    log = AuditLog(
        apartado=apartado,
        accion=accion,
        id_usuario_cuenta=id_user,
        id_usuario_cliente=id_client,
        ip_sesion=ip,
        device_name=device_name,
        browser_name_version=browser_name_version,
    )
    log.save()


