from django.db import models
from users.models import User
from datetime import datetime, timedelta

# Create your models here.

DIAS_WEEKDAY = {
        'lunes':0,
        'martes':1,
        'miercoles':2,
        'jueves':3,
        'viernes':4,
        'sabado':5,
        'domingo':6
    }

class Parte(models.Model):
    #Clase Abstracta para los diferentes tipos de documentos
    foto = models.ImageField(upload_to='partes/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    #Relaciones con otros modelos
    #1 usuario crea N partes
    usuario_creador = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='%(class)s_creados')
    #1 cliente tiene asociado N partes
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, related_name='%(class)s_clientes')
    #1 empresa tiene N partes
    empresa = models.ForeignKey('empresas.Empresa',on_delete=models.CASCADE,related_name='%(class)s_empresas')


    fecha_finalizacion = models.DateTimeField(blank=True, null=True)
    class Meta:
        abstract = True



class Parte_Trabajo(Parte):
    ParteTrabajoID = models.AutoField(primary_key=True)
    #Campos específicos para partes de trabajo
    #Relaciones con otros modelos
    #Usuario creador del parte de trabajo se considera trabajador inicial
    #0 o 1 usuario releva el parte de trabajo
    usuario_relevo = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True, related_name='partes_relevo')
    fecha_hora_relevo = models.DateTimeField(blank=True, null=True)
    #1 servicio tiene asociado N partes de trabajo
    servicio = models.ForeignKey('servicios.Servicio', on_delete=models.CASCADE, related_name='partes_servicio')
    observaciones = models.TextField(blank=True, null=True)


    def calcular_horas(self)->float | None:
        if self.fecha_creacion and self.fecha_finalizacion:
            diff = self.fecha_finalizacion - self.fecha_creacion
            return round(diff.total_seconds()/3600,1)
        return None


class Linea_Parte_Trabajo(models.Model):
    LineaParteTrabajoID = models.AutoField(primary_key=True)
    #Campos específicos para líneas de partes de trabajo
    #TO-DO: Cambiar el campo de actividad por un campo de eleccion con las actividades predefinidas
    actividad = models.TextField(blank=True, null=True)
    extra_info = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    #Relaciones con otros modelos
    #1 parte de trabajo tiene asociado N líneas de parte de trabajo
    parte_trabajo = models.ForeignKey('Parte_Trabajo', on_delete=models.CASCADE, related_name='lineas_parte_trabajo')

class Parte_Incidencia(Parte):
    ParteIncidenciaID = models.AutoField(primary_key=True)
    #Campos específicos para partes de incidencia
    texto_incidencia = models.TextField(blank=True, null=True)
    fecha_hora_incidencia = models.DateTimeField(auto_now_add=True)
    #Relaciones con otros modelos
    #1 usuario asociado a N incidencias
    usuario_asociado_a_incidencia = models.ForeignKey('users.User',on_delete=models.SET_NULL, blank=True, null=True, related_name='partes_incidencia_sobre_usuario')

class Parte_Inspeccion(Parte):
    ParteInspeccionID = models.AutoField(primary_key=True)
    #Campos específicos para partes de inspeccion
    descripcion = models.TextField(max_length=255)
    #Relaciones con otros modelos
    #1 usuario inspector se asocia con N inspecciones
    inspector_asociado = models.ForeignKey('users.User',on_delete=models.SET_NULL,blank=True,null=True,related_name='partes_inspeccion_inspector_asociado')
    

class Informe_Acuda(Parte):
    InformeAcudaID = models.AutoField(primary_key=True)
    #Campos específicos para informes de acuda
    descripcion = models.TextField(max_length=255)
    #Relaciones con otros modelos
    #1 tecnico inspector registra que acude en N informes de acuda
    tecnico_asociado = models.ForeignKey('users.User', on_delete=models.PROTECT,related_name='informe_acuda_tecnico_asociado')
    #1 central receptora recibe N informes de acuda
    central = models.ForeignKey('centrales.Central', on_delete=models.SET_NULL,null=True,blank=True)


#Parece que solo hay funcionalidad de vista de informes en general, no parece que haya opcion de crear/modificar
def can_view_informes(user:User)->bool:
    return user.permisos_informes in ['view_only','create_modify']

#Resto de informes si tienen opcion
def can_view_parte_trabajo(user:User)->bool:
    return user.permisos_partes_trabajo in ['view_only','create_modify']
def can_CRUD_parte_trabajo(user:User)->bool:
    return user.permisos_partes_trabajo == 'create_modify'

def can_view_parte_inspeccion(user:User)->bool:
    return user.permisos_partes_inspeccion in ['view_only','create_modify']

def can_CRUD_parte_inspeccion(user:User)->bool:
    return user.permisos_partes_inspeccion == 'create_modify'

def can_view_parte_incidencia(user:User)->bool:
    return user.permisos_partes_incidencias in ['view_only','create_modify']

def can_CRUD_parte_incidencia(user:User)->bool:
    return user.permisos_partes_incidencias == 'create_modify'

def can_view_acuda(user:User)->bool:
    return user.permisos_informes_acuda in ['view_only','create_modify']

def can_CRUD_acuda(user:User)->bool:
    return user.permisos_informes_acuda == 'create_modify'


