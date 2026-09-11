from django.contrib import admin

from .models import Ingrediente


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'unidad_medida', 'costo_unitario', 'activo')
    list_filter = ('activo', 'unidad_medida')
    search_fields = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
