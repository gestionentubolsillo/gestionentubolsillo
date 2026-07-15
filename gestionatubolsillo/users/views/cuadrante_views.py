from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import User,Cuadrante, Cuenta, EncryptedFilePDF,can_access_backoffice, can_view_users, can_CRUD_users
from django.template import loader
from django.http import HttpResponse, HttpRequest, FileResponse
from django.contrib import messages
from django.utils.timezone import now
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.views.decorators.clickjacking import xframe_options_sameorigin
from home.utils import file_encrypt, file_decrypt
import base64
import io
# Create your views here.

from users.filters import filter_cuadrantes
from users.paginators import paginate_cuadrantes_users
from users.builders import build_cuadrante
from users.validators import can_user_access_cuadrante, validate_cuadrante,validate_account_access

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
@require_GET
def list_cuadrantes_of_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    auth_error = validate_account_access(request, user)
    if auth_error:
        return auth_error

    filtros,exclusiones = filter_cuadrantes(user)
    cuadrantes = Cuadrante.objects.filter(**filtros).exclude(**exclusiones).order_by('id')
    context = paginate_cuadrantes_users(request,cuadrantes,user)
    return render(request,'account/users/cuadrantes/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
@require_GET
def cuadrante_details(request:HttpRequest,user_id,cuadrante_id):
    user = User.objects.filter(UserID=user_id).first()
    auth_error = validate_account_access(request, user)
    if auth_error:
        return auth_error

    cuadrante = Cuadrante.objects.filter(id=cuadrante_id).first()
    auth_errors = can_user_access_cuadrante(request,user,cuadrante)
    if auth_errors:
        return redirect(f"/backoffice/users/{user.UserID}/cuadrantes")
    context = {'usuario':user,'cuadrante':cuadrante,'action':'view'}
    return render(request,'account/users/cuadrantes/form.html',context)

@xframe_options_sameorigin
@require_GET
def show_cuadrante_pdf(request:HttpRequest,user_id,cuadrante_id):
    user = User.objects.filter(UserID=user_id).first()
    auth_error = validate_account_access(request, user)
    if auth_error:
        return auth_error

    cuadrante = Cuadrante.objects.filter(id=cuadrante_id).first()
    auth_errors = can_user_access_cuadrante(request,user,cuadrante)
    if auth_errors:
        return redirect(f"/backoffice/users/{user.UserID}/cuadrantes")
    
    cuenta:Cuenta = user.cuenta
    plaintext = file_decrypt(enc_file=cuadrante.file, cuenta=cuenta)
    if plaintext is None:
        return HttpResponse('Error descifrando el archivo',status=500)

    return FileResponse(io.BytesIO(plaintext), content_type='application/pdf',filename=cuadrante.file.tag)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
@require_http_methods(["GET","POST"])
def create_cuadrante(request:HttpRequest,user_id):
    template = loader.get_template('account/users/cuadrantes/form.html')
    
    user = User.objects.filter(UserID=user_id).first()
    auth_error = validate_account_access(request, user)
    if auth_error:
        return auth_error

    context = {'action':'create','usuario':user}

    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        archivo = request.FILES.get('archivo')
        errors = validate_cuadrante(request,nombre,archivo)
        print(f"errors={errors}")
        if errors:
            return HttpResponse(template.render(context,request))
        
        #Cifrar el archivo, guardarlo y crear cuadrante
        cuenta: Cuenta = user.cuenta
        encrypted_file = file_encrypt(file=archivo,cuenta=cuenta)
        if encrypted_file is None:
            context['error'] = 'Error cifrando el archivo'
            return HttpResponse(template.render(context, request))
        file = EncryptedFilePDF.from_cipher(cipher_result=encrypted_file,
            upload_path=f'users-{user.UserID}/cuadrantes/{base64.b64encode(encrypted_file.HMAC).decode()}')
        file.save()
        cuadrante = build_cuadrante(data={'file':file,'nombre':nombre,'user':user})
        return redirect(f"/backoffice/users/{user.UserID}/cuadrantes/{cuadrante.pk}")

    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))
    

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
@require_POST
def delete_cuadrante(request:HttpRequest,user_id,cuadrante_id):
    user = User.objects.filter(UserID=user_id).first()
    auth_error = validate_account_access(request, user)
    if auth_error:
        return auth_error

    cuadrante = Cuadrante.objects.filter(id=cuadrante_id).first()
    auth_errors = can_user_access_cuadrante(request,user,cuadrante)
    if auth_errors:
        return redirect(f"/backoffice/users/{user.UserID}/cuadrantes")
    cuadrante.fecha_borrado = now()
    cuadrante.save()
    return redirect(f"/backoffice/users/{user.UserID}/cuadrantes")
