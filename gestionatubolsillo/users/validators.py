from django.http import  HttpRequest
from django.contrib import messages
from empresas.models import Empresa
from django.db.models.manager import BaseManager
from django.core.files.uploadedfile import UploadedFile
from servicios.models import  Servicio
from .models import User,Cuadrante
from django.shortcuts import redirect



MIN_CHARS_PASSWORD = 8



def validate_user(request : HttpRequest,
                  usuario,password,confirm_password,nombre,apellidos,
                  provincia,municipio,empresa)->bool:
    errors = False
    global MIN_CHARS_PASSWORD
    if usuario == '':
        messages.error(request,"El nombre de usuario no puede estar vacío", extra_tags='error')
        errors = True
    if password == '':
        messages.error(request,"La contraseña no puede estar vacía",extra_tags='error')
        errors = True
    if password != confirm_password:
        messages.error(request,"Las contraseñas no coinciden",extra_tags='error')
        errors = True
    if len(password) < MIN_CHARS_PASSWORD:
        messages.error(request,f"La contraseña debe tener al menos {MIN_CHARS_PASSWORD} caracteres",extra_tags='error')
        errors = True
    if nombre == '' or apellidos == '':
        messages.error(request,"El nombre o apellidos no pueden estar vacíos",extra_tags='error')
        errors = True
    if provincia == '':
        messages.error(request,"Debe indicar la provincia a la que pertenece",extra_tags='error')
        errors = True
    if municipio == '':
        messages.error(request,"Debe indicar el municipio al que pertenece",extra_tags='error')
        errors = True
    empresa_exists = Empresa.objects.filter(EmpresaID=empresa).first()
    if not empresa_exists:
        messages.error(request,"El usuario debe estar asociado a una empresa",extra_tags='error')
        errors = True
    return errors

def validate_user_edit(request : HttpRequest,
                  usuario,nombre,apellidos,
                  provincia,municipio,empresa)->bool:
    errors = False
    if usuario == '':
        messages.error(request,"El nombre de usuario no puede estar vacío", extra_tags='error')
        errors = True
    if nombre == '' or apellidos == '':
        messages.error(request,"El nombre o apellidos no pueden estar vacíos",extra_tags='error')
        errors = True
    if provincia == '':
        messages.error(request,"Debe indicar la provincia a la que pertenece",extra_tags='error')
        errors = True
    if municipio == '':
        messages.error(request,"Debe indicar el municipio al que pertenece",extra_tags='error')
        errors = True
    empresa_exists = Empresa.objects.filter(EmpresaID=empresa).first()
    if not empresa_exists:
        messages.error(request,"El usuario debe estar asociado a una empresa",extra_tags='error')
        errors = True
    return errors

def validate_services_of_user(request:HttpRequest,user:User,servicios:BaseManager[Servicio])->bool:
    empresa : Empresa = user.empresa
    errors = False
    servicios_de_diferente_empresa = servicios.exclude(empresa=empresa)
    if servicios_de_diferente_empresa.exists():
        messages.error(request,"Los servicios deben pertenecer a la misma empresa que el usuario para ser asignados",extra_tags='error')
        errors = True
    return errors


def can_user_access_cuadrante(request:HttpRequest,user:User,cuadrante:Cuadrante)->bool:
    errors = False
    if user is None:
        messages.error(request,"El usuario proporcionado no existe",extra_tags='error')
        errors = True
    if cuadrante is None:
        messages.error(request,"El cuadrante proporcionado no existe",extra_tags='error')
        errors = True
    if not user.is_admin and cuadrante.user != user:
        messages.error(request,"No está autorizado a ver el cuadrante",extra_tags='error')
        errors = True
    return errors

def validate_cuadrante(request:HttpRequest,nombre,archivo:UploadedFile)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe proporcionarle un nombre indicativo al cuadrante",extra_tags='error')
        errors = True
    if archivo is None:
        messages.error(request,"Debe proporcionar un archivo que muestre el cuadrante",extra_tags='error')
        errors = True
    return errors

def validate_account_access(request: HttpRequest, user: User | None):
    if not user:
        return redirect("/AuthError")

    logged_user: User = request.user
    if logged_user.cuenta_id != user.cuenta_id:
        return redirect("/AuthError")

    return None

