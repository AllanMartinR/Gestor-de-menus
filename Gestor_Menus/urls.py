
"""
URL configuration for Gestor_Menus project.
"""
from django.contrib import admin
from django.urls import include, path
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    # Módulo de Gestion (Gestion/urls.py) — ya define sus propios prefijos:
    # /ingredientes/, /ingredientes/nuevo/, /ingredientes/<pk>/editar/, /ingredientes/<pk>/baja/
    # /platillos/, /platillos/nuevo/, /platillos/<pk>/editar/, /platillos/<pk>/baja/
    path('', include('Gestion.urls')),
]
 
