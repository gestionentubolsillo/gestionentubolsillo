from django import template

register = template.Library()

ACCION_CLASS_MAP = {
    'CREATE': 'table-success',
    'UPDATE': 'table-secondary',
    'REMOVE': 'table-secondary',
    'DELETE': 'table-warning',
    'AUTH': 'table-info',
    'UNAUTH': 'table-danger',
    'ERROR': 'table-danger',
    'PERMISSION': 'table-primary',
    'OUT': 'table-light',
}

@register.filter
def accion_class(accion):
    return ACCION_CLASS_MAP.get(accion, '')