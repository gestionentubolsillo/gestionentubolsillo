#Decoradores sobre usuario tipo cliente
from functools import wraps
from django.shortcuts import redirect

def cli_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request, "user_client", None):
            return redirect("client/login")
        return view_func(request, *args, **kwargs)
    return wrapper