from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from usuarios.models import Area, Departamento, Cargo, Trabajador
from datetime import date

class Command(BaseCommand):
    help = "Crea datos de ejemplo: Áreas, Departamentos, Cargos y Trabajadores vinculados a usuarios de prueba"

    def handle(self, *args, **options):
        # Áreas
        areas = {
            'Operaciones': ['Bodega', 'Despacho'],
            'Finanzas': ['Contabilidad', 'Tesorería'],
            'TI': ['Desarrollo', 'Infraestructura'],
        }
        area_objs = {}
        for area_nombre, deptos in areas.items():
            area_obj, _ = Area.objects.get_or_create(nombre=area_nombre)
            area_objs[area_nombre] = area_obj
            self.stdout.write(self.style.SUCCESS(f"Área '{area_nombre}' lista"))
            for d in deptos:
                depto_obj, _ = Departamento.objects.get_or_create(nombre=d, area=area_obj)
                self.stdout.write(self.style.SUCCESS(f"  Departamento '{d}' en '{area_nombre}' listo"))

        # Cargos
        cargos = ['Administrador', 'Jefe RR.HH.', 'Desarrollador', 'Analista', 'Operario']
        cargo_objs = {}
        for c in cargos:
            cargo_obj, _ = Cargo.objects.get_or_create(nombre=c)
            cargo_objs[c] = cargo_obj
            self.stdout.write(self.style.SUCCESS(f"Cargo '{c}' listo"))

        # Vincular usuarios de prueba a Trabajador
        mapping = [
            ('admin_user', 'Operaciones', 'Bodega', 'Administrador', 'M'),
            ('manager_user', 'Finanzas', 'Contabilidad', 'Jefe RR.HH.', 'F'),
            ('dev_user', 'TI', 'Desarrollo', 'Desarrollador', 'M'),
            ('viewer_user', 'Operaciones', 'Despacho', 'Analista', 'O'),
        ]

        User = get_user_model()
        for username, area_n, depto_n, cargo_n, sexo in mapping:
            try:
                u = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Usuario '{username}' no existe. Ejecuta 'python manage.py seed_users' primero."))
                continue

            # Si ya existe registro Trabajador para este usuario, saltar
            if Trabajador.objects.filter(user=u).exists():
                self.stdout.write(self.style.WARNING(f"Trabajador para '{username}' ya existe"))
                continue

            area = area_objs.get(area_n)
            depto = Departamento.objects.get(nombre=depto_n, area=area)
            cargo = cargo_objs.get(cargo_n)

            t = Trabajador.objects.create(
                user=u,
                nombres=username.replace('_', ' ').title(),
                apellidos='Demo',
                sexo=sexo,
                fecha_ingreso=date(2024, 1, 15),
                area=area,
                departamento=depto,
                cargo=cargo,
                telefono='555-0101',
                direccion='Dirección Demo 123'
            )
            self.stdout.write(self.style.SUCCESS(f"Trabajador vinculado a '{username}': id={t.id}"))

        self.stdout.write(self.style.SUCCESS("Datos de ejemplo creados correctamente"))
