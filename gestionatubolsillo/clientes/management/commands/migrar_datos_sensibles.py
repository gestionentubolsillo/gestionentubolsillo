from django.core.management.base import BaseCommand
from clientes.models import Cliente
class Command(BaseCommand):
    help = "Migra datos sensibles de usuario a su versión encriptada"

    def handle(self, *args, **options):
        clientes = Cliente.objects.all()
        total = clientes.count()

        for i, cliente in enumerate(clientes,1):
            cliente.telefono_enc = cliente.telefono
            cliente.cif_enc = cliente.cif
            cliente.email_enc = cliente.email
            cliente.direccion_enc = cliente.direccion

            cliente.save()
            self.stdout.write(f'[{i}/{total}] Cliente {cliente.nombre} migrado')

        self.stdout.write(self.style.SUCCESS('Migración completada'))