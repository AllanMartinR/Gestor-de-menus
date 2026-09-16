from decimal import Decimal

from django.test import TestCase

from Gestion.models import Ingrediente, IngredientePlatillo, Menu, MenuPlatillo, Platillo
from Gestion.services import (
    MenuSinPlatillosError,
    NumeroComensalesInvalidoError,
    PlatilloSinIngredientesError,
    calcular_costo_por_comensal,
    calcular_costo_total_menu,
)


class CalcularCostoTotalMenuTests(TestCase):
    def test_un_platillo(self):
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
        menu = Menu.objects.create(nombre='Menú sencillo')
        MenuPlatillo.objects.create(menu=menu, platillo=platillo)

        costo = calcular_costo_total_menu(menu)
        self.assertEqual(costo, Decimal('20.00'))
        self.assertIsInstance(costo, Decimal)

    def test_varios_platillos_suma_correctamente(self):
        arroz = Ingrediente.objects.create(
            nombre='Arroz', unidad_medida='kg', costo_unitario=Decimal('10.00')
        )
        pollo = Ingrediente.objects.create(
            nombre='Pollo', unidad_medida='kg', costo_unitario=Decimal('60.00')
        )

        platillo_arroz = Platillo.objects.create(nombre='Arroz blanco')
        IngredientePlatillo.objects.create(
            platillo=platillo_arroz, ingrediente=arroz, cantidad=Decimal('1.000')
        )  # 10.00

        platillo_pollo = Platillo.objects.create(nombre='Pollo asado')
        IngredientePlatillo.objects.create(
            platillo=platillo_pollo, ingrediente=pollo, cantidad=Decimal('0.500')
        )  # 30.00

        menu = Menu.objects.create(nombre='Menú combinado')
        MenuPlatillo.objects.create(menu=menu, platillo=platillo_arroz)
        MenuPlatillo.objects.create(menu=menu, platillo=platillo_pollo)

        # 10.00 + 30.00 = 40.00
        self.assertEqual(calcular_costo_total_menu(menu), Decimal('40.00'))

    def test_menu_sin_platillos(self):
        menu = Menu.objects.create(nombre='Menú vacío')
        with self.assertRaises(MenuSinPlatillosError) as ctx:
            calcular_costo_total_menu(menu)
        self.assertIn('Menú vacío', str(ctx.exception))

    def test_propaga_platillo_sin_ingredientes(self):
        platillo = Platillo.objects.create(nombre='Sin receta')
        menu = Menu.objects.create(nombre='Menú con platillo vacío')
        MenuPlatillo.objects.create(menu=menu, platillo=platillo)
        with self.assertRaises(PlatilloSinIngredientesError) as ctx:
            calcular_costo_total_menu(menu)
        self.assertIn('Sin receta', str(ctx.exception))


class CalcularCostoPorComensalTests(TestCase):
    def _crear_menu_con_costo(self, costo_total):
        """Menú con un solo platillo/ingrediente cuyo costo total es `costo_total`."""
        platillo = Platillo.objects.create(nombre='Platillo comensal')
        ingrediente = Ingrediente.objects.create(
            nombre='Insumo', unidad_medida='kg', costo_unitario=costo_total
        )
        IngredientePlatillo.objects.create(
            platillo=platillo, ingrediente=ingrediente, cantidad=Decimal('1.000')
        )
        menu = Menu.objects.create(nombre='Menú comensal')
        MenuPlatillo.objects.create(menu=menu, platillo=platillo)
        return menu

    def test_division_correcta(self):
        menu = self._crear_menu_con_costo(Decimal('2530.25'))
        # 2530.25 / 50 = 50.605 → ROUND_HALF_UP → 50.61
        # (mismo resultado que el ejemplo real de "discada de res" entre 50 comensales)
        self.assertEqual(calcular_costo_por_comensal(menu, 50), Decimal('50.61'))

    def test_numero_comensales_cero(self):
        menu = self._crear_menu_con_costo(Decimal('100.00'))
        with self.assertRaises(NumeroComensalesInvalidoError):
            calcular_costo_por_comensal(menu, 0)

    def test_numero_comensales_negativo(self):
        menu = self._crear_menu_con_costo(Decimal('100.00'))
        with self.assertRaises(NumeroComensalesInvalidoError):
            calcular_costo_por_comensal(menu, -10)

    def test_numero_comensales_no_entero(self):
        menu = self._crear_menu_con_costo(Decimal('100.00'))
        with self.assertRaises(NumeroComensalesInvalidoError):
            calcular_costo_por_comensal(menu, 10.5)

    def test_menu_sin_platillos_propaga_error(self):
        menu = Menu.objects.create(nombre='Menú vacío para comensal')
        with self.assertRaises(MenuSinPlatillosError):
            calcular_costo_por_comensal(menu, 20)
