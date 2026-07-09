from django.db import models
from allauth.account.utils import get_next_redirect_url
from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from encrypted_fields.fields import EncryptedEmailField, EncryptedCharField
from Crypto.Random import get_random_bytes
import base64

from django.db import models
from collections import namedtuple

Cipher = namedtuple('Cipher',['HMAC','Nonce','Ciphertext'])

# Create your models here.

class Cuenta(models.Model):
    #Clave usada para encriptar los archivos de una cuenta. Tamaño necesario 32 Bytes (AES-GCM 256)
    file_key_encription = EncryptedCharField(blank=True)
    is_active = models.BooleanField(default=True)


    def save(self, force_insert = False, force_update = False, using = None, update_fields = None):
        
        if not self.file_key_encription:
            self.create()
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)    
    def create(self):
        self.file_key_encription = base64.b64encode(get_random_bytes(32)).decode()

    def get_key(self)->bytes:
        return base64.b64decode(self.file_key_encription)

class User(AbstractUser):

    PERMISSIONS_CHOICES = [
        ('no_access', 'Sin acceso'),
        ('view_only', 'Puede ver'),
        ('create_modify', 'Puede crear y modificar')
    ]
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('inspector', 'Inspector'),
        ('inspector_parte_trabajo', 'Inspector Parte Trabajo'),
        ('user', 'User')
    ]
    CATEGORIA_CHOICES = [
        ('ejecutivo', 'Ejecutivo'),
        ('comercial', 'Comercial'),
        ('operario', 'Operario'),
        ('administrativo', 'Administrativo')
    ]
    
    UserID = models.AutoField(primary_key=True)

    # You can add additional fields here if needed
    provincia = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)


    #Datos que necesitan encriptacion
    email = EncryptedEmailField(null=True, blank=True)
    telefono = EncryptedCharField(max_length=20,blank=True,null=True)
    direccion = EncryptedCharField(max_length=255,blank=True,null=True)
    nif = EncryptedCharField(max_length=20,blank=True,null=True)

    #Campos que necesitan la implementación de otros modelos para su funcionamiento
    #delegacion = ForeignKey(delegaciones models.delegacionID)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='ejecutivo')

    esInspector = models.BooleanField(default=False)
    esInspector_parteTrabajo = models.BooleanField(default=False)
    has_login_access = models.BooleanField(default=True)
    has_dashboard_access = models.BooleanField(default=False)
    

    can_view_own_partes_trabajo = models.BooleanField(default=False)  # Permiso adicional para ver solo sus propios registros
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='usuarios', null=True, blank=True)
    always_track_GPS = models.BooleanField(default=False)
    precio_hora = models.FloatField(default=0.)
    comentarios = models.TextField(blank=True,null=True)
    is_admin = models.BooleanField(default=False)

    #Relacion N:N el modelo servicio
    servicios = models.ManyToManyField('servicios.Servicio', related_name='users')
    delegacion = models.ForeignKey('delegaciones.Delegacion', on_delete=models.SET_NULL,related_name='usuarios', null=True, blank=True)

    cuenta = models.ForeignKey(Cuenta,on_delete=models.SET_NULL,related_name='usuarios',null=True,blank=True)

    @property
    def calcular_horas_totales(self, minutos_redondeo:int | None = None)->dict | None:
        total_horas = getattr(self, 'total_horas', None)
        if total_horas is None:
            return None
        
        total_seconds = int(total_horas.total_seconds())
        if minutos_redondeo is not None:
            total_seconds = (total_seconds // (minutos_redondeo * 60)) * minutos_redondeo * 60

        horas = total_seconds // 3600
        minutos = (total_seconds % 3600) // 60

        return {'horas': horas, 'minutos': minutos}

class PermisosModulo(models.Model):
    MODULOS = [
        ('USR', 'Usuarios'),
        ('TAR', 'Tareas'),
        ('CLI', 'Clientes'),
        ('NFC', 'Servicios NFC'),
        ('CEN', 'Central Receptora'),
        ('MED', 'Medios Auxiliares'),
        ('SUG', 'Sugerencias'),
        ('PAR', 'Partes Trabajo'),
        ('INC', 'Partes Incidencias'),
        ('ACU', 'Informes Acuda'),
        ('INS', 'Partes Inspección'),
        ('MAN', 'Mantenimientos'),
        ('ALM', 'Almacén'),
        ('INF', 'Informes'),
        ('EMP', 'Empresas'),
        ('CON', 'Configuración'),
    ]
    
    NIVELES = [
        ('0', 'Sin acceso'),
        ('1', 'Lectura'),
        ('2', 'Escritura'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permisos')
    modulo  = models.CharField(max_length=3, choices=MODULOS)
    nivel   = models.CharField(max_length=1, choices=NIVELES, default='0')

    def __str__(self):
        return f"{self.user.username}: {self.get_modulo_display()}"

def set_upload_path(instance:Cuadrante,filename:str)->str:
    return f'users{instance.user.UserID}/cuadrantes/{filename}'


class EncryptedFilePDF(models.Model):
    nonce = models.CharField()
    tag = models.CharField()
    file = models.FileField()

    @classmethod
    def from_cipher(cls,cipher_result:Cipher,upload_path:str) -> EncryptedFilePDF:
        instance = cls(nonce=base64.b64encode(cipher_result.Nonce).decode(),
                       tag=base64.b64encode(cipher_result.HMAC).decode())
        instance.file.save(upload_path,ContentFile(cipher_result.Ciphertext),save=False)
        return instance

class Cuadrante(models.Model):
    nombre = models.CharField(max_length=20)
    file = models.OneToOneField(EncryptedFilePDF,on_delete=models.SET_NULL,null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='cuadrantes')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_borrado = models.DateTimeField(blank=True,null=True)



def can_access_backoffice(user:User)-> bool:
    return user.has_login_access

def can_view_users(user:User)-> bool:
    return tiene_acceso(user,'USR')

def can_CRUD_users(user:User)-> bool:
    return tiene_acceso(user,'USR',nivel_min='2')


def get_permiso(usuario:User,modulo:str):
    try:
        return PermisosModulo.objects.get(user=usuario, modulo=modulo).nivel
    except PermisosModulo.DoesNotExist:
        return '0'

def tiene_acceso(usuario:User,modulo:str,nivel_min='1'):
    return get_permiso(usuario, modulo) >= nivel_min