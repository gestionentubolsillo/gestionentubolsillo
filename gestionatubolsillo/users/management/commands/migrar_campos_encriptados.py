from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = "Migra datos sensibles de usuario a su versión encriptada"

    def handle(self, *args, **options):
        users = User.objects.all()
        total = users.count()

        for i, user in enumerate(users,1):
            user.telefono_enc = user.telefono
            user.nif_enc = user.nif
            plain_mail = user.email
            user.email = plain_mail
            user.direccion_enc = user.direccion

            user.save()
            self.stdout.write(f'[{i}/{total}] Usuario {user.username} migrado')

        self.stdout.write(self.style.SUCCESS('Migración completada'))