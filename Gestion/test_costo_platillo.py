from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from Gestion.models import Ingrediente, IngredientePlatillo, Platillo
from Gestion.services import (
    EquivalenciaNoDefinidaError,
    PlatilloSinIngredientesError,
    UnidadNoConvertibleError,
    calcular_costo_platillo,
)


class CalcularCostoPlatilloTests(TestCase):
    def test_un_ingrediente(self):
        platillo = Platillo.objects.create(nombre='Arroz blanco')
        arroz = Ingrediente.objects.create(
            nombre='Arroz',
            unidad_medida='kg',
            costo_unitario=Decimal('10.00'),
        )
        IngredientePlatillo.objects.create(
            platillo=platillo,
            ingrediente=arroz,
            cantidad=Decimal('2.000'),
        )
        costo = calcular_costo_platillo(platillo)
        self.assertEqual(costo, Decimal('20.00'))
        self.assertIsInstance(costo, Decimal)

    def test_varios_ingredientes_distintas_unidades_base(self):
        platillo = Platillo.objects.create(nombre='Guisado')
        arroz = Ingrediente.objects.create(
            nombre='Arroz',
            unidad_medida='kg',
            costo_unitario=Decimal('20.00'),
        )
        aceite = Ingrediente.objects.create(
            nombre='Aceite',
            unidad_medida='lt',
            costo_unitario=Decimal('40.00'),
        )
        huevo = Ingrediente.objects.create(
            nombre='Huevo',
            unidad_medida='pz',
            costo_unitario=Decimal('2.50'),
        )
        IngredientePlatillo.objects.create(
            platillo=platillo,
            ingrediente=arroz,
            cantidad=Decimal('1.500'),
        )
        IngredientePlatillo.objects.create(
            platillo=platillo,
            ingrediente=aceite,
            cantidad=Decimal('0.250'),
        )
        IngredientePlatillo.objects.create(
            platillo=platillo,
            ingrediente=huevo,
            cantidad=Decimal('4.000'),
        )
        # 1.5×20 + 0.250×40 + 4×2.50 = 30 + 10 + 10 = 50.00
        self.assertEqual(calcular_costo_platillo(platillo), Decimal('50.00'))

    def test_platillo_sin_ingredientes(self):
        platillo = Platillo.objects.create(nombre='Sin receta')
        with self.assertRaises(PlatilloSinIngredientesError) as ctx:
            calcular_costo_platillo(platillo)
        self.assertIn('Sin receta', str(ctx.exception))

    def test_redondeo_half_up_a_dos_decimales(self):
        platillo = Platillo.objects.create(nombre='Redondeo')
        insumo = Ingrediente.objects.create(
            nombre='Sal',
            unidad_medida='kg',
            costo_unitario=Decimal('1.00'),
        )
        IngredientePlatillo.objects.create(
            platillo=platillo,
            ingrediente=insumo,
            cantidad=Decimal('0.015'),
        )
        # 0.015 × 1.00 = 0.015 → ROUND_HALF_UP → 0.02
        self.assertEqual(calcular_costo_platillo(platillo), Decimal('0.02'))

    def test_propaga_equivalencia_no_definida(self):
        platillo = Platillo.objects.create(nombre='Guisado')
        cebolla = Ingrediente.objects.create(
            nombre='Cebolla',
            unidad_medida='kg',
            costo_unitario=Decimal('8.00'),
        )
        IngredientePlatillo.objects.create(
            platillo=platillo,
            ingrediente=cebolla,
            cantidad=Decimal('0.200'),
        )
        error = EquivalenciaNoDefinidaError(
            'No hay equivalencia por pieza definida para el ingrediente "Cebolla".'
        )
        with patch(
            'Gestion.services.convertir_a_unidad_base',
            side_effect=error,
        ):
            with self.assertRaises(EquivalenciaNoDefinidaError) as ctx:
                calcular_costo_platillo(platillo)
        self.assertIs(ctx.exception, error)
        self.assertIn('Cebolla', str(ctx.exception))

    def test_propaga_unidad_no_convertible(self):
        platillo = Platillo.objects.create(nombre='Guisado')
        aceite = Ingrediente.objects.create(
            nombre='Aceite',
            unidad_medida='lt',
            costo_unitario=Decimal('40.00'),
        )
        IngredientePlatillo.objects.create(
            platillo=platillo,
            ingrediente=aceite,
            cantidad=Decimal('0.100'),
        )
        error = UnidadNoConvertibleError(
            'No se puede convertir kg a lt para el ingrediente "Aceite".'
        )
        with patch(
            'Gestion.services.convertir_a_unidad_base',
            side_effect=error,
        ):
            with self.assertRaises(UnidadNoConvertibleError) as ctx:
                calcular_costo_platillo(platillo)
        self.assertIs(ctx.exception, error)
        self.assertIn('Aceite', str(ctx.exception))
