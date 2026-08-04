from django.shortcuts import redirect
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.urls import reverse
from django.template import loader
from clientes.models import user_client
from auditloggers.handlers import save_log
from users.models import User

# Create your views here.
@require_http_methods(["GET","POST"])
def login(request:HttpRequest):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            save_log(request, apartado='LOGIN', accion='AUTH', id_user=user.pk, id_cuenta=user.cuenta.pk)
            return redirect(reverse('home'))
        else:
            # Credenciales inválidas, mostrar mensaje de error
            messages.error(request, "Credenciales inválidas. Por favor, inténtalo de nuevo.", extra_tags='error')
            intento_usuario = User.objects.get(username=username)
            save_log(request, apartado='LOGIN', accion='ERROR', id_cuenta=intento_usuario.cuenta.pk if intento_usuario else None, id_user=intento_usuario.pk if intento_usuario else None)
            return redirect('/login')
    else:
        template = loader.get_template('account/login.html')
        context = {}
        user = request.user
        if user.is_authenticated:
            return redirect(reverse('home'))
        return HttpResponse(template.render(context, request))


@require_http_methods(["GET","POST"])
def login_cli(request:HttpRequest):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        try:
            user_cli = user_client.objects.get(username=username)
            if user_cli.check_password(password) and user_cli.is_active:
                request.session['_user_client_id'] = user_cli.pk
                save_log(request, apartado='LOGIN', accion='AUTH', id_user=user_cli.pk, id_cuenta=user_cli.cuenta.pk)
                #Redirigir al inicio
                return redirect(reverse('home'))
            else:
                # Credenciales inválidas, mostrar mensaje de error
                messages.error(request,"Credenciales inválidas. Por favor, inténtalo de nuevo.", extra_tags='error')
                save_log(request, apartado='LOGIN', accion='ERROR', id_user=None, id_cuenta=None)
                #Ruta provisional
                return redirect('/login_cli')
        except user_client.DoesNotExist:
            # Credenciales inválidas, mostrar mensaje de error
            messages.error(request,"Credenciales inválidas. Por favor, inténtalo de nuevo.", extra_tags='error')
            save_log(request, apartado='LOGIN', accion='ERROR', id_user=None, id_cuenta=None)
            #Ruta provisional
            return redirect('/login_cli')

    else:
        template = loader.get_template('account/login.html')
        context = {}
        user = request.user_client
        if user is not None:
            return redirect(reverse('home'))
        return HttpResponse(template.render(context, request))       

@require_POST
def logout_view(request:HttpRequest):
    save_log(request, apartado='LOGIN', accion='OUT', id_user=request.user.pk, id_cuenta=request.user.cuenta.pk)
    logout(request)
    return redirect('/')

def logout_cli(request:HttpRequest):
    pass