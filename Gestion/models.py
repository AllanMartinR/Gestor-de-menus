from django.db import models
from django.core.validators import MinValueValidator

class IngredienteQuerySet(models.QuerySet):
    """Queryset reutilizable: platillos deben usar .activos() al seleccionar ingredientes."""

    def activos(self):
        return self.filter(activo=True)


class Ingrediente(models.Model):
    class UnidadMedida(models.TextChoices):
        KG = 'kg', 'Kilogramo (kg)'
        L = 'l', 'Litro (l)'
        PZA = 'pza', 'Pieza (pza)'

    nombre = models.CharField('nombre', max_length=120, unique=True)
    unidad_medida = models.CharField(
        'unidad de medida',
        max_length=3,
        choices=UnidadMedida.choices,
    )
    costo_unitario = models.DecimalField(
        'costo unitario',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    activo = models.BooleanField('activo', default=True)
    fecha_creacion = models.DateTimeField('fecha de creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('fecha de actualización', auto_now=True)

    objects = IngredienteQuerySet.as_manager()

    class Meta:
        verbose_name = 'ingrediente'
        verbose_name_plural = 'ingredientes'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
    