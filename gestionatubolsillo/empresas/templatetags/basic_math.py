from django import template

register = template.Library()

@register.filter
def substract(arg1:int|float,arg2:int|float):
    return arg1-arg2
