"""Enrutamiento raíz del proyecto: admin y app `usuarios`."""
from usuarios import views as usuarios_views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', usuarios_views.root_redirect, name='root'),
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
]
