from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import transaction
from usuarios.models import Trabajador
from datetime import date

class Command(BaseCommand):
    help = "Ejecuta migraciones, inicializa roles, crea usuarios y datos demo, y sanea inconsistencias"

    def handle(self, *args, **options):
        call_command("migrate")
        call_command("init_roles")
        call_command("seed_users")
        call_command("seed_demo_org")

        User = get_user_model()
        with transaction.atomic():
            for u in User.objects.all():
                if not Trabajador.objects.filter(user=u).exists():
                    Trabajador.objects.create(user=u, nombres=u.username, apellidos="Demo", sexo="O", rut="SIN-RUT", fecha_ingreso=date.today())
            for t in Trabajador.objects.all():
                if not t.nombres:
                    t.nombres = "SinNombre"
                if not t.apellidos:
                    t.apellidos = "SinApellido"
                if not t.sexo:
                    t.sexo = "O"
                if not t.rut:
                    t.rut = "SIN-RUT"
                if not t.fecha_ingreso:
                    t.fecha_ingreso = date.today()
                t.save(update_fields=["nombres","apellidos","sexo","rut","fecha_ingreso"])
        self.stdout.write(self.style.SUCCESS("Bootstrap y saneo completados"))
