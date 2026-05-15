from django.db import models
from allauth.account.utils import get_next_redirect_url
from django.contrib.auth.models import AbstractUser

from django.db import models

# Create your models here.
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
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    nif = models.CharField(max_length=20, blank=True, null=True)

    #Campos que necesitan la implementación de otros modelos para su funcionamiento
    #empresa = ForeignKey(empresas models.empresaID)
    #delegacion = ForeignKey(delegaciones models.delegacionID)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='ejecutivo')

    #Roles admin, inspector, inspector_parte_trabajo, user
    role = AbstractUser.choices = [
        ('admin', 'Admin'), 
        ('inspector', 'Inspector'), 
        ('inspector_parte_trabajo', 'Inspector Parte Trabajo'), 
        ('user', 'User')
    ]
    has_login_access = models.BooleanField(default=True)
    has_dashboard_access = models.BooleanField(default=False)
    # Permisos de usuario para cada sección del sistema
    # Sin permiso/Puede ver/Puede crear y modificar/En el caso de partes de trabajo, habilitar la opción de solo ver sus propios registros
    permisos_usuario = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    permisos_tareas = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    permisos_clientes = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    permisos_servicios_NFC = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    permisos_central_receptora = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    permisos_medios_auxiliares = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    permisos_sugerencias = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    permisos_partes_trabajo = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    can_view_own_partes_trabajo = models.BooleanField(default=False)  # Permiso adicional para ver solo sus propios registros
    permisos_partes_incidencias = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    permisos_informes_acuda = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    permisos_partes_inspeccion = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    permisos_mantenimientos = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    permisos_almacen = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    permisos_informes = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    permisos_empresas = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')
    permisos_configuracion = models.CharField(max_length=20, choices=PERMISSIONS_CHOICES, default='no_access')


