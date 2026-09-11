"""
URL configuration for Gestor_Menus project.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    # Módulo de ingredientes (Gestion/urls.py):
    # /ingredientes/, /ingredientes/nuevo/, /ingredientes/<pk>/editar/, /ingredientes/<pk>/baja/
    path('ingredientes/', include('Gestion.urls')),
]
