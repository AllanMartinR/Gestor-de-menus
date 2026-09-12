from django.db import models
from django.core.validators import MinValueValidator

# --- TICKET SCRUM-12 (Insumos) ---
class Ingrediente(models.Model):
    UNIDADES = [
        ('kg', 'Kilogramo (kg)'),
        ('lt', 'Litro (lt)'),
        ('pz', 'Pieza (pz)'),
        ('g', 'Gramo (g)'),
        ('ml', 'Mililitro (ml)'),
    ]
    
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre")
    unidad_medida = models.CharField(max_length=50, choices=UNIDADES, verbose_name="Unidad de medida")
    costo_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        verbose_name="Costo unitario"
    )
    # Opción A (SCRUM-16): un Decimal por ingrediente en lugar de una tabla
    # EquivalenciaUnidad. "pz" no tiene peso/volumen universal (un huevo ≠ una
    # cebolla). equivalencia_pza = cuántas unidades de unidad_medida equivalen
    # a 1 pieza. Vacío si no aplica. No se adivina densidad kg↔lt.
    equivalencia_pza = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Equivalencia por pieza",
        help_text=(
            "Cuántas unidades de la unidad base equivalen a 1 pieza. "
            "Ej. 0.060 si 1 huevo = 0.060 kg. Vacío si no aplica."
        ),
    )
    activo = models.BooleanField(default=True, verbose_name="Estatus")

    def __str__(self):
        return self.nombre


# --- TICKET SCRUM-15 (Platillos y Recetas) ---
class Platillo(models.Model):
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre del platillo")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class IngredientePlatillo(models.Model):
    platillo = models.ForeignKey(Platillo, on_delete=models.CASCADE, related_name='receta')
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.RESTRICT)
    cantidad = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        validators=[MinValueValidator(0.001)],
        help_text="Cantidad requerida del ingrediente"
    )

    class Meta:
        unique_together = ('platillo', 'ingrediente')
        verbose_name = "Ingrediente de platillo"
        verbose_name_plural = "Ingredientes de platillos"

    def __str__(self):
        return f"{self.cantidad} de {self.ingrediente.nombre} en {self.platillo.nombre}"