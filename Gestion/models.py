from django.core.validators import MinValueValidator
from django.db import models


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
    unidad_medida = models.CharField(
        max_length=50, choices=UNIDADES, verbose_name="Unidad de medida"
    )
    costo_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Costo unitario",
    )
    equivalencia_pza = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Equivalencia por pieza",
    )
    activo = models.BooleanField(default=True, verbose_name="Estatus")

    def __str__(self):
        return self.nombre


# --- TICKET SCRUM-15 (Platillos y Recetas) ---
class Platillo(models.Model):
    nombre = models.CharField(
        max_length=150, unique=True, verbose_name="Nombre del platillo"
    )
    descripcion = models.TextField(
        blank=True, null=True, verbose_name="Descripción"
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class IngredientePlatillo(models.Model):
    platillo = models.ForeignKey(
        Platillo, on_delete=models.CASCADE, related_name='receta'
    )
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.RESTRICT)
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0.001)],
        help_text="Cantidad requerida del ingrediente",
    )

    class Meta:
        unique_together = ('platillo', 'ingrediente')
        verbose_name = 'Ingrediente de platillo'
        verbose_name_plural = 'Ingredientes de platillos'

    def __str__(self):
        return f'{self.cantidad} de {self.ingrediente.nombre} en {self.platillo.nombre}'


# --- TICKET SCRUM-19 & NUEVOS CÁLCULOS (Menús) ---
class Menu(models.Model):
    nombre = models.CharField(
        max_length=150, unique=True, verbose_name='Nombre del menú'
    )
    descripcion = models.TextField(
        blank=True, null=True, verbose_name='Descripción'
    )

    # Comensales por turno
    comensales_desayuno = models.PositiveIntegerField(
        default=0, verbose_name='Comensales Desayuno'
    )
    comensales_comida = models.PositiveIntegerField(
        default=0, verbose_name='Comensales Comida'
    )
    comensales_cena = models.PositiveIntegerField(
        default=0, verbose_name='Comensales Cena'
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    def obtener_resumen_financiero(self):
        """Calcula costos unitarios, totales por turno, insumos globales y costo general del menú."""
        resumen = {
            'Desayuno': {
                'comensales': self.comensales_desayuno,
                'costo_total': 0,
                'platillos': [],
            },
            'Comida': {
                'comensales': self.comensales_comida,
                'costo_total': 0,
                'platillos': [],
            },
            'Cena': {
                'comensales': self.comensales_cena,
                'costo_total': 0,
                'platillos': [],
            },
        }

        ingredientes_totales = {}

        for mp in self.composicion.all():
            tiempo = mp.tiempo
            platillo = mp.platillo
            comensales = getattr(self, f'comensales_{tiempo.lower()}', 0)

            # Costo unitario por porción del platillo
            costo_platillo_unitario = sum(
                float(item.cantidad) * float(item.ingrediente.costo_unitario)
                for item in platillo.receta.all()
            )
            costo_turno_total = costo_platillo_unitario * comensales

            if tiempo in resumen:
                resumen[tiempo]['platillos'].append(
                    {
                        'nombre': platillo.nombre,
                        'costo_unitario': costo_platillo_unitario,
                        'costo_total_turno': costo_turno_total,
                    }
                )
                resumen[tiempo]['costo_total'] += costo_turno_total

            # Acumular ingredientes totales necesarios para el menú completo
            for item in platillo.receta.all():
                ing_nombre = item.ingrediente.nombre
                ing_unidad = item.ingrediente.get_unidad_medida_display()
                cantidad_necesaria = float(item.cantidad) * comensales

                if ing_nombre not in ingredientes_totales:
                    ingredientes_totales[ing_nombre] = {
                        'cantidad': 0,
                        'unidad': ing_unidad,
                    }
                ingredientes_totales[ing_nombre]['cantidad'] += cantidad_necesaria

        costo_total_menu = sum(r['costo_total'] for r in resumen.values())

        return {
            'resumen_tiempos': resumen,
            'ingredientes_totales': ingredientes_totales,
            'costo_total_menu': costo_total_menu,
        }


class MenuPlatillo(models.Model):
    menu = models.ForeignKey(
        Menu, on_delete=models.CASCADE, related_name='composicion'
    )
    platillo = models.ForeignKey(Platillo, on_delete=models.RESTRICT)

    TIEMPOS = [
        ('Desayuno', 'Desayuno'),
        ('Comida', 'Comida'),
        ('Cena', 'Cena'),
    ]
    tiempo = models.CharField(
        max_length=20,
        choices=TIEMPOS,
        default='Comida',
        verbose_name='Tiempo de comida',
    )

    class Meta:
        unique_together = ('menu', 'platillo', 'tiempo')
        verbose_name = 'Platillo de menú'
        verbose_name_plural = 'Platillos de menú'

    def __str__(self):
        return f'{self.platillo.nombre} ({self.tiempo}) en {self.menu.nombre}'