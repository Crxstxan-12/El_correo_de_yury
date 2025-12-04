"""Registro de modelos en el admin de Django para gestión interna."""
from django.contrib import admin
from .models import Area, Departamento, Cargo, Trabajador, ContactoEmergencia, CargaFamiliar

# Register your models here.

admin.site.register(Area)
admin.site.register(Departamento)
admin.site.register(Cargo)
admin.site.register(Trabajador)
admin.site.register(ContactoEmergencia)
admin.site.register(CargaFamiliar)
