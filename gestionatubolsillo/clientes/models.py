from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from users.models import User, tiene_acceso
from encrypted_fields import EncryptedCharField,EncryptedEmailField

# Create your models here.

class Cliente(models.Model):
    ClienteID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)

    #Datos sensibles
    direccion = EncryptedCharField(max_length=255,blank=True,null=True)
    telefono = EncryptedCharField(max_length=20,blank=True,null=True)
    cif = EncryptedCharField(max_length=20,blank=True,null=True)
    email = EncryptedEmailField(blank=True,null=True)
    
    persona_contacto = models.CharField(max_length=100, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    #Campos que necesitan de API de localización para su funcionamiento
    provincia = models.CharField(max_length=100, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    #Relacion N:N con el modelo servicio
    servicios = models.ManyToManyField('servicios.Servicio', related_name='clientes')
    #Relacion N:1 con empresa
    empresa = models.ForeignKey('empresas.Empresa',on_delete=models.CASCADE,related_name='clientes')
    
    def __str__(self):
        return self.nombre
    

class user_client(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128) #Hashed
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey('clientes.Cliente',on_delete=models.CASCADE,related_name='organizacion')
    is_active = models.BooleanField(default=True)
    servicios = models.ManyToManyField('servicios.Servicio',related_name='usuarios_cliente')

    def set_password(self,raw_password):
        self.password = make_password(raw_password)

    def check_password(self,raw_password)->bool:
        return check_password(password=raw_password,encoded=self.password)


def can_view_clientes(user: User)-> bool:
    return tiene_acceso(user, 'CLI')

def can_CRUD_clientes(user: User)-> bool:
    return tiene_acceso(user, 'CLI', nivel_min='2')