"""Modelos principales de la app Usuarios.

Define el catálogo organizacional (Áreas, Departamentos, Cargos) y las
entidades de negocio relacionadas con las personas: Trabajador y sus
contactos/cargas familiares. Los modelos usan claves foráneas con
comportamientos seguros (SET_NULL donde corresponde) y ordenamientos
predeterminados para facilitar listados.
"""
from django.db import models
from django.conf import settings

# Create your models here.
# ==============================
# MODELOS DEL PROYECTO EL_CORREO
# ==============================

class Area(models.Model):
    """Unidad organizacional de alto nivel.

    Única por `nombre`. Relaciona con `Departamento` mediante
    `Area.departamentos`.
    """
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Departamento(models.Model):
    """Subunidad dentro de un `Area`.

    El par (`nombre`, `area`) es único para evitar duplicados por área.
    """
    nombre = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='departamentos')

    class Meta:
        unique_together = ('nombre', 'area')
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.area.nombre})"


class Cargo(models.Model):
    """Rol laboral o posición dentro de la organización.

    Única por `nombre`.
    """
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Trabajador(models.Model):
    """Persona trabajadora vinculada a `User`.

    Incluye datos personales y relaciones opcionales a `Area`,
    `Departamento` y `Cargo`. El vínculo con `User` es obligatorio
    (OneToOne) y sirve para permisos y autenticación.
    """
    # Conexión con el usuario de autenticación
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trabajador'
    )

    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    # Campo RUT (opcional), indexado para búsquedas
    rut = models.CharField(max_length=12, null=True, blank=True, db_index=True)
    sexo = models.CharField(
        max_length=20,
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')]
    )
    fecha_ingreso = models.DateField(null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True)
    cargo = models.ForeignKey(Cargo, on_delete=models.SET_NULL, null=True, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Trabajador"
        verbose_name_plural = "Trabajadores"
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class ContactoEmergencia(models.Model):
    """Contacto de emergencia asociado a un `Trabajador`."""
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='contactos_emergencia')
    nombre = models.CharField(max_length=120)
    parentesco = models.CharField(max_length=80)
    telefono = models.CharField(max_length=30)

    class Meta:
        verbose_name = "Contacto de Emergencia"
        verbose_name_plural = "Contactos de Emergencia"

    def __str__(self):
        return f"{self.nombre} ({self.parentesco})"


class CargaFamiliar(models.Model):
    """Carga familiar asociada a un `Trabajador`."""
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='cargas_familiares')
    nombre = models.CharField(max_length=120)
    parentesco = models.CharField(max_length=80)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Carga Familiar"
        verbose_name_plural = "Cargas Familiares"

    def __str__(self):
        return f"{self.nombre} - {self.parentesco}"

