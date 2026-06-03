from django.db import models

# Create your models here.
class AuditLog(models.Model):
    APARTADOS = [
        ('TAREA','Tarea'),
        ('LOGIN','Login'),
        ('USER','Usuario'),
        ('EMPRESA','Empresa'),
        ('SERVICIO','Servicio'),
        ('ALMACEN','Almacen'),
        ('CENTRAL','Central Receptora'),
        ('CLIENTE','Cliente'),
        ('PARTE','Parte'),
        ('DELEGACION','Delegacion'),
        ('MANTENIMIENTO','Mantenimiento'),
        ('MEDIO-AUX','Medios auxiliares'),
        ('SUGERENCIA','Sugerencia')


    ]

    ACCIONES = [
        ('CREATE','Crear'),
        ('REMOVE','Borrar')
        ('UPDATE','Editar'),
        ('DELETE','Eliminar'),
        ('AUTH','Autenticacion')
    ]

    apartado = models.CharField(max_length=20,choices=APARTADOS)
    accion = models.CharField(max_length=20,choices=ACCIONES)
    fecha = models.DateTimeField(auto_now_add=True)

    #Operaciones realizadas por el usuario logeado
    id_usuario_cuenta = models.IntegerField(null=True,blank=True)
    #Operaciones realizadas por el cliente con cuenta
    id_usuario_cliente = models.IntegerField(null=True,blank=True)

    #Empresa determina quien puede ver el registro de actividad de la empresa
    #IMPORTANTE: si un usuario perteneciente a dicha empresa crea otra, las actividades que se realicen en la empresa hija, deben ser mostradas en la empresa padre
    empresa_id = models.IntegerField(null=True,blank=True)
    #Informacion relativa al dispositivo de la sesion
    ip_sesion = models.GenericIPAddressField(null=True,blank=True)
    device_name = models.CharField(max_length=30,null=True,blank=True)
    browser_name_version = models.CharField(max_length=40,null=True,blank=True)

    
