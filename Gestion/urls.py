from django.urls import path

from .views import (
    IngredienteCreateView,
    IngredienteListView,
    IngredienteUpdateView,
    ingrediente_baja,
)

# Ejemplo de inclusión en Gestor_Menus/urls.py:
#   path('ingredientes/', include('Gestion.urls')),
#
# Rutas resultantes:
#   /ingredientes/                  -> ingrediente_list
#   /ingredientes/nuevo/            -> ingrediente_create
#   /ingredientes/<pk>/editar/      -> ingrediente_update
#   /ingredientes/<pk>/baja/        -> ingrediente_baja (solo POST)

urlpatterns = [
    path('', IngredienteListView.as_view(), name='ingrediente_list'),
    path('nuevo/', IngredienteCreateView.as_view(), name='ingrediente_create'),
    path('<int:pk>/editar/', IngredienteUpdateView.as_view(), name='ingrediente_update'),
    path('<int:pk>/baja/', ingrediente_baja, name='ingrediente_baja'),
]
