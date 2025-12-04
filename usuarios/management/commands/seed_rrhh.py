from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from usuarios.models import Area, Departamento, Cargo, Trabajador

class Command(BaseCommand):
    help = "Crea usuarios, grupos RR.HH. y trabajadores vinculados (idempotente y robusto)"

    def handle(self, *args, **options):
        # Asegurar roles base
        try:
            call_command("init_roles")
        except Exception:
            pass

        # Garantizar existencia de grupos
        g_admin, _ = Group.objects.get_or_create(name="Administrador")
        g_rrhh, _ = Group.objects.get_or_create(name="Jefe RR.HH.")
        g_trab, _ = Group.objects.get_or_create(name="Trabajador")

        # Usuarios base
        User = get_user_model()
        admin, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@ejemplo.cl"})
        if not admin.has_usable_password():
            admin.set_password("admin123")
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        leo, _ = User.objects.get_or_create(username="leo", defaults={"email": "leo@ejemplo.cl"})
        if not leo.has_usable_password():
            leo.set_password("leo123")
        # Dar acceso al admin site si se requiere gestión
        leo.is_staff = True
        leo.save()

        # Asignación de grupos
        admin.groups.set([g_admin])
        leo.groups.set([g_rrhh])

        # Catálogo RR.HH.
        area_rrhh, _ = Area.objects.get_or_create(nombre="RR.HH.")
        depto_gestion, _ = Departamento.objects.get_or_create(nombre="Gestión", area=area_rrhh)
        cargo_jefe, _ = Cargo.objects.get_or_create(nombre="Jefe RR.HH.")
        cargo_admin, _ = Cargo.objects.get_or_create(nombre="Administrador")

        # Trabajadores vinculados
        t_admin, created_admin = Trabajador.objects.get_or_create(
            user=admin,
            defaults={
                "nombres": "Admin",
                "apellidos": "Sistema",
                "sexo": "O",
                "area": area_rrhh,
                "departamento": depto_gestion,
                "cargo": cargo_admin,
            }
        )
        if not created_admin:
            # Actualizar campos clave si estuvieran vacíos
            t_admin.nombres = t_admin.nombres or "Admin"
            t_admin.apellidos = t_admin.apellidos or "Sistema"
            t_admin.sexo = t_admin.sexo or "O"
            t_admin.area = t_admin.area or area_rrhh
            t_admin.departamento = t_admin.departamento or depto_gestion
            t_admin.cargo = t_admin.cargo or cargo_admin
            t_admin.save()

        t_leo, created_leo = Trabajador.objects.get_or_create(
            user=leo,
            defaults={
                "nombres": "Leo",
                "apellidos": "RRHH",
                "sexo": "M",
                "area": area_rrhh,
                "departamento": depto_gestion,
                "cargo": cargo_jefe,
            }
        )
        if not created_leo:
            t_leo.nombres = t_leo.nombres or "Leo"
            t_leo.apellidos = t_leo.apellidos or "RRHH"
            t_leo.sexo = t_leo.sexo or "M"
            t_leo.area = t_leo.area or area_rrhh
            t_leo.departamento = t_leo.departamento or depto_gestion
            t_leo.cargo = t_leo.cargo or cargo_jefe
            t_leo.save()

        self.stdout.write(self.style.SUCCESS(
            f"RR.HH. listo: Areas={Area.objects.count()} Deptos={Departamento.objects.count()} "
            f"Cargos={Cargo.objects.count()} Trabajadores={Trabajador.objects.count()}"
        ))
