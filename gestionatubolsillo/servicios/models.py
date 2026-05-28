from django.db import models
from multiselectfield import MultiSelectField

# Create your models here.

class Servicio(models.Model):
    ServicioID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)
    precio_por_hora = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dias_semana = MultiSelectField(choices=[
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo')
    ], blank=True, null=True)
    is_active = models.BooleanField(default=True)
    #Los servicios pueden ser de interior o exterior, por lo que se puede representar con un booleano
    #Si es exterior se necesita solo la ubicacion GPS
    #Si es interior se puede usar la ubicacion GPS o la ubicacion de alta precisión
    es_exterior = models.BooleanField(default=True)
    #Campo que indica la necesidad de gps
    #Si requiere gps, el dispositibo del usuario debe tenerlo habilitado para poder enviar partes, actividades, etc.
    requiere_gps = models.BooleanField(default=False)
    mail_de_contacto = models.EmailField(blank=True, null=True)

    #Relacion N:1 con el modelo Empresa
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='empresa')
    

    def __str__(self):
        return self.nombre
