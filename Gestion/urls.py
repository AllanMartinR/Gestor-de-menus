from django.urls import path

from .views import (
    IngredienteCreateView,
    IngredienteListView,
    IngredienteUpdateView,
    ingrediente_baja,
    PlatilloCreateView,
    PlatilloListView,
    PlatilloUpdateView,
    platillo_baja,
    armado_menu,
    menu_eliminar,
)

# Este urls.py ya define los prefijos completos. Inclúyelo en la raíz
# del proyecto (Gestor_Menus/urls.py):
#   path('', include('Gestion.urls')),
#
# Rutas resultantes:
#   /ingredientes/              -> ingrediente_list
#   /ingredientes/nuevo/        -> ingrediente_create
#   /ingredientes/<pk>/editar/  -> ingrediente_update
#   /ingredientes/<pk>/baja/    -> ingrediente_baja (solo POST)
#   /platillos/                 -> platillo_list
#   /platillos/nuevo/           -> platillo_create
#   /platillos/<pk>/editar/     -> platillo_update
#   /platillos/<pk>/baja/       -> platillo_baja (solo POST)
#   /armar-menu/                -> armado_menu
#   /menu/eliminar/<pk>/        -> menu_eliminar (solo POST)

urlpatterns = [
    # Ingredientes
    path('ingredientes/', IngredienteListView.as_view(), name='ingrediente_list'),
    path('ingredientes/nuevo/', IngredienteCreateView.as_view(), name='ingrediente_create'),
    path('ingredientes/<int:pk>/editar/', IngredienteUpdateView.as_view(), name='ingrediente_update'),
    path('ingredientes/<int:pk>/baja/', ingrediente_baja, name='ingrediente_baja'),

    # Platillos
    path('platillos/', PlatilloListView.as_view(), name='platillo_list'),
    path('platillos/nuevo/', PlatilloCreateView.as_view(), name='platillo_create'),
    path('platillos/<int:pk>/editar/', PlatilloUpdateView.as_view(), name='platillo_update'),
    path('platillos/<int:pk>/baja/', platillo_baja, name='platillo_baja'),
    
    # Menús
    path('armar-menu/', armado_menu, name='armado_menu'),
    path('menu/eliminar/<int:pk>/', menu_eliminar, name='menu_eliminar'),
]