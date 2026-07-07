from django.shortcuts import render, redirect
from django.http import HttpRequest
from users.models import User
from django.utils.timezone import localdate, make_aware
from sugerencias.models import Sugerencia
from partes.models import Parte_Trabajo, Parte_Incidencia, Informe_Acuda
from datetime import datetime, time, timedelta

# Create your views here.

def show_backoffice(request:HttpRequest):
    user : User = request.user
    if not user.is_authenticated:
        return redirect('/login')
    today = localdate()
    num_sugerencias_today = Sugerencia.objects.filter(cuenta=user.cuenta,fecha_creacion__date=today).count()
    num_partes_today = Parte_Trabajo.objects.filter(cuenta=user.cuenta,fecha_creacion__date=today).count()
    num_incidencias_today = Parte_Incidencia.objects.filter(cuenta=user.cuenta,fecha_creacion__date=today).count()
    num_acudas_today = Informe_Acuda.objects.filter(cuenta=user.cuenta,fecha_creacion__date=today).count()
    context = {
        'user':user,
        'today': today,
        'num_sugerencias':num_sugerencias_today,
        'num_partes':num_partes_today,
        'num_incidencias':num_incidencias_today,
        'num_acudas':num_acudas_today
    }
    return render(request,'backoffice/home.html',context)