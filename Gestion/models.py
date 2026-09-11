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