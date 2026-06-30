from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import PermisosModulo, User


MAPA_CAMPOS = {
    'USR': 'permisos_usuario',
    'TAR': 'permisos_tareas',
    'CLI': 'permisos_clientes',
    'NFC': 'permisos_servicios_NFC',
    'CEN': 'permisos_central_receptora',
    'MED': 'permisos_medios_auxiliares',
    'SUG': 'permisos_sugerencias',
    'PAR': 'permisos_partes_trabajo',
    'INC': 'permisos_partes_incidencias',
    'ACU': 'permisos_informes_acuda',
    'INS': 'permisos_partes_inspeccion',
    'MAN': 'permisos_mantenimientos',
    'ALM': 'permisos_almacen',
    'INF': 'permisos_informes',
    'EMP': 'permisos_empresas',
    'CON': 'permisos_configuracion',
}

MAPA_VALORES = {
    'no_access':     '0',
    'view_only':     '1',
    'create_modify': '2',
}

class Command(BaseCommand):
    help = 'Migra permisos de campos individuales al modelo ModuloPermiso'
    
    def handle(self, *args, **options):
        users = User.objects.all()
        total = users.count()

        for i, user in enumerate(users,1):
            for code, field in MAPA_CAMPOS.items():
                value_to_migrate = getattr(user,field,'no_access')
                PermisosModulo.objects.get_or_create(
                    user = user,
                    modulo = code,
                    defaults={'nivel':MAPA_VALORES.get(value_to_migrate,'0')}
                )
            self.stdout.write(f'[{i}/{total}] Usuario {user.username} migrado')
        self.stdout.write(self.style.SUCCESS('Migración completada'))