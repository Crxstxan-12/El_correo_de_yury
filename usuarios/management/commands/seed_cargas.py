from django.core.management.base import BaseCommand
from usuarios.models import Trabajador, CargaFamiliar
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = "Genera cargas familiares de prueba para Trabajadores"

    def add_arguments(self, parser):
        parser.add_argument('--per-worker', type=int, default=2)
        parser.add_argument('--min', type=int, default=1)
        parser.add_argument('--wipe', action='store_true', default=False)
        parser.add_argument('--max-age', type=int, default=25)
        parser.add_argument('--min-age', type=int, default=1)

    def handle(self, *args, **opts):
        per_worker = max(0, opts['per_worker'])
        min_count = max(0, min(opts['min'], per_worker))
        wipe = opts['wipe']
        max_age = max(1, opts['max_age'])
        min_age = max(0, min(opts['min_age'], max_age))

        parentescos = ["Hijo", "Hija", "Cónyuge", "Padre", "Madre"]

        if wipe:
            deleted = CargaFamiliar.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f"Cargas familiares eliminadas: {deleted}"))

        trabajadores = list(Trabajador.objects.all())
        if not trabajadores:
            self.stdout.write(self.style.WARNING("No hay Trabajadores. Ejecute 'seed_rrhh' o 'seed_demo_org' primero."))
            return

        created = 0
        for t in trabajadores:
            existing = CargaFamiliar.objects.filter(trabajador=t).count()
            target = per_worker if existing == 0 else max(min_count, per_worker - existing)
            for _ in range(target):
                years = random.randint(min_age, max_age)
                days = years * 365 + random.randint(0, 364)
                dob = date.today() - timedelta(days=days)
                nombre = random.choice(["Alex","Sam","Camila","Diego","Valentina","Juan","Sofía","Martín"]) + f" {random.randint(1,99)}"
                CargaFamiliar.objects.create(
                    trabajador=t,
                    nombre=nombre,
                    parentesco=random.choice(parentescos),
                    fecha_nacimiento=dob
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Cargas familiares creadas: {created}"))

