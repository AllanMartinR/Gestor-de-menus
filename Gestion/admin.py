from django.contrib import admin
from .models import Ingrediente, Platillo, IngredientePlatillo, Menu, MenuPlatillo

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'unidad_medida', 'costo_unitario', 'activo')
    list_filter = ('activo', 'unidad_medida')
    search_fields = ('nombre',)

class IngredientePlatilloInline(admin.TabularInline):
    model = IngredientePlatillo
    extra = 1

@admin.register(Platillo)
class PlatilloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    inlines = [IngredientePlatilloInline]

class MenuPlatilloInline(admin.TabularInline):
    model = MenuPlatillo
    extra = 1

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    inlines = [MenuPlatilloInline]