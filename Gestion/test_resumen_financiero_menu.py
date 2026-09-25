from django.test import TestCase

from Gestion.models import Ingrediente, IngredientePlatillo, Menu, MenuPlatillo, Platillo


class ObtenerResumenFinancieroTests(TestCase):
    def _crear_platillo_con_receta(self, nombre, ingrediente, cantidad):
        platillo = Platillo.objects.create(nombre=nombre)
        IngredientePlatillo.objects.create(
            platillo=platillo, ingrediente=ingrediente, cantidad=cantidad
        )
        return platillo

    def test_un_platillo_en_un_solo_turno(self):
        arroz = Ingrediente.objects.create(
            nombre='Arroz', unidad_medida='kg', costo_unitario=10
        )
        # cantidad=100 * costo_unitario=10 = 1000; /100 = 10.00 costo unitario por comensal
        platillo = self._crear_platillo_con_receta('Arroz blanco', arroz, 100)

        menu = Menu.objects.create(
            nombre='Menú comida', comensales_desayuno=0, comensales_comida=20, comensales_cena=0
        )
        MenuPlatillo.objects.create(menu=menu, platillo=platillo, tiempo='Comida')

        resumen = menu.obtener_resumen_financiero()

        self.assertEqual(resumen['resumen_tiempos']['Comida']['comensales'], 20)
        self.assertEqual(len(resumen['resumen_tiempos']['Comida']['platillos']), 1)

        linea = resumen['resumen_tiempos']['Comida']['platillos'][0]
        self.assertEqual(linea['nombre'], 'Arroz blanco')
        self.assertAlmostEqual(linea['costo_unitario'], 10.0)
        self.assertAlmostEqual(linea['costo_total_turno'], 200.0)  # 10.0 * 20 comensales

        # Los otros turnos no tienen platillos ni costo.
        self.assertEqual(resumen['resumen_tiempos']['Desayuno']['costo_total'], 0)
        self.assertEqual(resumen['resumen_tiempos']['Cena']['costo_total'], 0)

        self.assertAlmostEqual(resumen['costo_total_menu'], 200.0)

    def test_varios_turnos_con_distintos_comensales(self):
        huevo = Ingrediente.objects.create(
            nombre='Huevo', unidad_medida='pz', costo_unitario=3
        )
        pollo = Ingrediente.objects.create(
            nombre='Pollo', unidad_medida='kg', costo_unitario=60
        )

        desayuno_platillo = self._crear_platillo_con_receta(
            'Huevo revuelto', huevo, 200
        )  # 200*3=600 /100 = 6.00 por comensal
        cena_platillo = self._crear_platillo_con_receta(
            'Pollo asado', pollo, 50
        )  # 50*60=3000 /100 = 30.00 por comensal

        menu = Menu.objects.create(
            nombre='Menú completo',
            comensales_desayuno=10,
            comensales_comida=0,
            comensales_cena=5,
        )
        MenuPlatillo.objects.create(menu=menu, platillo=desayuno_platillo, tiempo='Desayuno')
        MenuPlatillo.objects.create(menu=menu, platillo=cena_platillo, tiempo='Cena')

        resumen = menu.obtener_resumen_financiero()

        # Desayuno: 6.00 * 10 comensales = 60.00
        self.assertAlmostEqual(resumen['resumen_tiempos']['Desayuno']['costo_total'], 60.0)
        # Cena: 30.00 * 5 comensales = 150.00
        self.assertAlmostEqual(resumen['resumen_tiempos']['Cena']['costo_total'], 150.0)
        self.assertEqual(resumen['resumen_tiempos']['Comida']['costo_total'], 0)

        # 60.00 + 150.00 = 210.00
        self.assertAlmostEqual(resumen['costo_total_menu'], 210.0)

    def test_turno_con_cero_comensales_no_suma_costo(self):
        arroz = Ingrediente.objects.create(
            nombre='Arroz', unidad_medida='kg', costo_unitario=10
        )
        platillo = self._crear_platillo_con_receta('Arroz blanco', arroz, 100)

        menu = Menu.objects.create(nombre='Menú sin comensales')
        MenuPlatillo.objects.create(menu=menu, platillo=platillo, tiempo='Comida')

        resumen = menu.obtener_resumen_financiero()

        # comensales_comida por defecto es 0 → costo_total_turno = 0
        self.assertEqual(resumen['resumen_tiempos']['Comida']['comensales'], 0)
        self.assertAlmostEqual(
            resumen['resumen_tiempos']['Comida']['platillos'][0]['costo_total_turno'], 0.0
        )
        self.assertAlmostEqual(resumen['costo_total_menu'], 0.0)

    def test_platillo_sin_receta_no_rompe_el_calculo(self):
        # A diferencia de calcular_costo_platillo (services.py), este método
        # no valida que el platillo tenga receta: simplemente suma sobre una
        # lista vacía y el costo unitario sale en 0.
        platillo_vacio = Platillo.objects.create(nombre='Sin receta')
        menu = Menu.objects.create(nombre='Menú con platillo vacío', comensales_comida=10)
        MenuPlatillo.objects.create(menu=menu, platillo=platillo_vacio, tiempo='Comida')

        resumen = menu.obtener_resumen_financiero()

        linea = resumen['resumen_tiempos']['Comida']['platillos'][0]
        self.assertAlmostEqual(linea['costo_unitario'], 0.0)
        self.assertAlmostEqual(linea['costo_total_turno'], 0.0)
        self.assertAlmostEqual(resumen['costo_total_menu'], 0.0)

    def test_menu_sin_platillos_no_rompe_el_calculo(self):
        # A diferencia de calcular_costo_total_menu (services.py), este
        # método no lanza MenuSinPlatillosError: regresa un resumen vacío
        # con costo_total_menu en 0.
        menu = Menu.objects.create(nombre='Menú vacío')

        resumen = menu.obtener_resumen_financiero()

        self.assertEqual(resumen['resumen_tiempos']['Desayuno']['platillos'], [])
        self.assertEqual(resumen['resumen_tiempos']['Comida']['platillos'], [])
        self.assertEqual(resumen['resumen_tiempos']['Cena']['platillos'], [])
        self.assertAlmostEqual(resumen['costo_total_menu'], 0.0)

    def test_ingredientes_agrupados_por_turno_y_platillo(self):
        arroz = Ingrediente.objects.create(
            nombre='Arroz', unidad_medida='kg', costo_unitario=10
        )
        platillo = self._crear_platillo_con_receta('Arroz blanco', arroz, 2)

        menu = Menu.objects.create(nombre='Menú agrupado', comensales_comida=15)
        MenuPlatillo.objects.create(menu=menu, platillo=platillo, tiempo='Comida')

        resumen = menu.obtener_resumen_financiero()

        insumos = resumen['ingredientes_agrupados']['Comida']['Arroz blanco']
        self.assertEqual(len(insumos), 1)
        self.assertEqual(insumos[0]['nombre'], 'Arroz')
        # cantidad_necesaria = cantidad de la receta (2) * comensales (15) = 30
        self.assertAlmostEqual(insumos[0]['cantidad'], 30.0)
        self.assertEqual(insumos[0]['unidad'], 'Kilogramo (kg)')

    def test_mismo_platillo_en_dos_turnos_distintos(self):
        arroz = Ingrediente.objects.create(
            nombre='Arroz', unidad_medida='kg', costo_unitario=10
        )
        platillo = self._crear_platillo_con_receta('Arroz blanco', arroz, 100)

        menu = Menu.objects.create(
            nombre='Menú repetido', comensales_comida=10, comensales_cena=4
        )
        MenuPlatillo.objects.create(menu=menu, platillo=platillo, tiempo='Comida')
        MenuPlatillo.objects.create(menu=menu, platillo=platillo, tiempo='Cena')

        resumen = menu.obtener_resumen_financiero()

        # Comida: 10.00 * 10 = 100.00 | Cena: 10.00 * 4 = 40.00
        self.assertAlmostEqual(resumen['resumen_tiempos']['Comida']['costo_total'], 100.0)
        self.assertAlmostEqual(resumen['resumen_tiempos']['Cena']['costo_total'], 40.0)
        self.assertAlmostEqual(resumen['costo_total_menu'], 140.0)
