from django import template
from users.models import tiene_acceso, User

register = template.Library()

@register.simple_tag
def permiso(user:User,modulo,nivel_min='1'):
    return tiene_acceso(user,modulo,nivel_min)