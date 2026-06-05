from django.shortcuts import redirect
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.template import loader
from clientes.models import user_client

# Create your views here.
def login(request:HttpRequest):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            #Redirigir al inicio
            return redirect(reverse('home'))
        else:
            # Credenciales inválidas, mostrar mensaje de error
            messages.error(request, "Credenciales inválidas. Por favor, inténtalo de nuevo.", extra_tags='error')
            return redirect('/login')
    else:
        template = loader.get_template('account/login.html')
        context = {}
        user = request.user
        if user.is_authenticated:
            return redirect(reverse('home'))
        return HttpResponse(template.render(context, request))



def login_cli(request:HttpRequest):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        try:
            user_cli = user_client.objects.get(username=username)
            if user_cli.check_password(password) and user_cli.is_active:
                request.session['_user_client_id'] = user_cli.pk
                #Redirigir al inicio
                return redirect(reverse('home'))
            else:
                # Credenciales inválidas, mostrar mensaje de error
                messages.error(request,"Credenciales inválidas. Por favor, inténtalo de nuevo.", extra_tags='error')
                #Ruta provisional
                return redirect('/login_cli')
        except user_client.DoesNotExist:
            # Credenciales inválidas, mostrar mensaje de error
            messages.error(request,"Credenciales inválidas. Por favor, inténtalo de nuevo.", extra_tags='error')
            #Ruta provisional
            return redirect('/login_cli')

    else:
        template = loader.get_template('account/login.html')
        context = {}
        user = request.user_client
        if user is not None:
            return redirect(reverse('home'))
        return HttpResponse(template.render(context, request))       


def logout_view(request:HttpRequest):
    logout(request)
    return redirect('/')

def logout_cli(request:HttpRequest):
    pass