from django.db import models
from users.models import User, tiene_acceso
from encrypted_fields import EncryptedCharField, EncryptedEmailField, EncryptedTextField

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
    usuario_creador = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='%(class)s_creados')
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, related_name='%(class)s_clientes')
    empresa = models.ForeignKey('empresas.Empresa',on_delete=models.CASCADE,related_name='%(class)s_empresas')
    cuenta = models.ForeignKey('users.Cuenta',on_delete=models.SET_NULL,related_name='%(class)s_cuenta',null=True,blank=True)


    fecha_finalizacion = models.DateTimeField(blank=True, null=True)
    class Meta:
        abstract = True



class Parte_Trabajo(Parte):
    ParteTrabajoID = models.AutoField(primary_key=True)
    #Campos específicos para partes de trabajo
    usuario_relevo = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True, related_name='partes_relevo')
    fecha_hora_relevo = models.DateTimeField(blank=True, null=True)
    servicio = models.ForeignKey('servicios.Servicio', on_delete=models.CASCADE, related_name='partes_servicio')
    observaciones = EncryptedTextField(blank=True, null=True)
    fecha_inicio_registrada = models.DateTimeField(blank=True, null=True)
    fecha_finalizacion_registrada = models.DateTimeField(blank=True, null=True)

    def calcular_horas(self, minutos_redondeo: int | None = None) -> dict | None:
        if self.fecha_creacion and self.fecha_finalizacion:
            diff = self.fecha_finalizacion - self.fecha_creacion
            total_seconds = int(diff.total_seconds())

            if minutos_redondeo is not None and minutos_redondeo > 0:
                total_seconds = (total_seconds // (minutos_redondeo * 60)) * (minutos_redondeo * 60)

            horas = total_seconds // 3600
            minutos = (total_seconds % 3600) // 60
            return {'horas': horas, 'minutos': minutos}
        return None


class Linea_Parte_Trabajo(models.Model):
    ACTIVIDADES = [
        ('Inicio', 'Inicio de Actividad'),
        ('Sin novedad', 'Sin Novedad'),
        ('Incidencia', 'Incidencia'),
        ('Finalización', 'Fin del Servicio'),
        ('Otros', 'Otros'),
        ('Relevo', 'Relevo de Personal')
    ]
    LineaParteTrabajoID = models.AutoField(primary_key=True)
    #Campos específicos para líneas de partes de trabajo
    actividad = models.CharField(max_length=255, choices=ACTIVIDADES, blank=True, null=True)
    extra_info = EncryptedTextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_registrada = models.DateTimeField(blank=True, null=True)
    parte_trabajo = models.ForeignKey('Parte_Trabajo', on_delete=models.CASCADE, related_name='lineas_parte_trabajo')

class Parte_Incidencia(Parte):
    ParteIncidenciaID = models.AutoField(primary_key=True)
    #Campos específicos para partes de incidencia
    texto_incidencia = EncryptedTextField(blank=True, null=True)
    fecha_hora_incidencia = models.DateTimeField(auto_now_add=True)
    usuario_asociado_a_incidencia = models.ForeignKey('users.User',on_delete=models.SET_NULL, blank=True, null=True, related_name='partes_incidencia_sobre_usuario')

class Parte_Inspeccion(Parte):
    ParteInspeccionID = models.AutoField(primary_key=True)
    #Campos específicos para partes de inspeccion
    descripcion = EncryptedTextField(blank=True, null=True)
    inspector_asociado = models.ForeignKey('users.User',on_delete=models.SET_NULL,blank=True,null=True,related_name='partes_inspeccion_inspector_asociado')
    

class Informe_Acuda(Parte):
    InformeAcudaID = models.AutoField(primary_key=True)
    #Campos específicos para informes de acuda
    descripcion = EncryptedTextField(blank=True, null=True)
    tecnico_asociado = models.ForeignKey('users.User', on_delete=models.PROTECT,related_name='informe_acuda_tecnico_asociado')
    central = models.ForeignKey('centrales.Central', on_delete=models.SET_NULL,null=True,blank=True)


#Parece que solo hay funcionalidad de vista de informes en general, no parece que haya opcion de crear/modificar
def can_view_informes(user: User)-> bool:
    return tiene_acceso(user, 'INF')

#Resto de informes si tienen opcion
def can_view_parte_trabajo(user: User)-> bool:
    return tiene_acceso(user, 'PAR')
def can_CRUD_parte_trabajo(user: User)-> bool:
    return tiene_acceso(user, 'PAR', nivel_min='2')

def can_view_parte_inspeccion(user: User)-> bool:
    return tiene_acceso(user, 'INS')

def can_CRUD_parte_inspeccion(user: User)-> bool:
    return tiene_acceso(user, 'INS', nivel_min='2')

def can_view_parte_incidencia(user: User)-> bool:
    return tiene_acceso(user, 'INC')

def can_CRUD_parte_incidencia(user: User)-> bool:
    return tiene_acceso(user, 'INC', nivel_min='2')

def can_view_acuda(user: User)-> bool:
    return tiene_acceso(user, 'ACU')

def can_CRUD_acuda(user: User)-> bool:
    return tiene_acceso(user, 'ACU', nivel_min='2')


