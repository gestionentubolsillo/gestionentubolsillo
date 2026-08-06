from decimal import Decimal

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template import loader

from django.views.decorators.http import require_http_methods

from empresas.validators import validate_empresa
from empresas.models import Empresa
from users.validators import validate_register

from users.models import User,Cuenta,PermisosModulo

@require_http_methods(["GET","POST"])
def register_new_user(request:HttpRequest):
    template = loader.get_template('account/register.html')
    context = {'paquetes': Empresa._meta.get_field('paquete').choices}
    if request.method == 'POST':
        #Formulario de creacion de usuario, similar al de creacion de usuario en backoffice
        #Formulario de creacion de empresa, similar al de creacion de empresa en backoffice, para crear la empresa del usuario
        #Validaciones de los formularios, en caso de validacion positiva, crear la cuenta asociada al usuario, crear al usuario y la empresa y asociar al usuario a la empresa
        usuario = request.POST.get('username','')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('password_confirm','')
        nombre = request.POST.get('nombre','')
        apellidos = request.POST.get('apellidos','')
        mail = request.POST.get('mail','')
        direccion = request.POST.get('direccion','')
        provincia = request.POST.get('provincia','')
        municipio = request.POST.get('municipio','')
        telefono = request.POST.get('telefono','')
        nif = request.POST.get('nif','')
        categoria = request.POST.get('categoria','ejecutivo')
        precio_hora = Decimal(request.POST.get('precio_hora') or 0.)

        errores_usuario = validate_register(request,usuario,password,confirm_password,nombre,apellidos,provincia,municipio)
        if errores_usuario:
            return HttpResponse(template.render(context,request))

        nombre_empresa = request.POST.get('name','')
        paquete = request.POST.get('paquete','')

        errores_empresa = validate_empresa(request,nombre_empresa,paquete)
        if errores_empresa:
            return HttpResponse(template.render(context,request))

        cuenta = Cuenta.objects.create()
        user = User.objects.create(
            username=usuario,
            first_name=nombre,
            last_name=apellidos,
            email=mail,
            direccion=direccion,
            provincia=provincia,
            municipio=municipio,
            telefono=telefono,
            nif=nif,
            categoria=categoria,
            precio_hora=precio_hora,
            cuenta=cuenta,
            is_admin=True,  # Asignar el rol de administrador al usuario registrado
            is_active=True  # Activar la cuenta del usuario registrado
        )
        user.set_password(password)
        empresa = Empresa.objects.create(
            nombre=nombre_empresa,
            paquete=paquete,
            usuario_creador=user,
            cuenta=cuenta
        )
        user.empresa = empresa
        user.save()
        PermisosModulo.objects.bulk_create([
            PermisosModulo(user=user,modulo=modulo,nivel='2') for modulo, _ in PermisosModulo._meta.get_field('modulo').choices
        ])
        return redirect('/login')  # Redirigir al usuario a la página de inicio de sesión después del registro exitoso

    if request.method == 'GET':
        return HttpResponse(template.render(context,request))