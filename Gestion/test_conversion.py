from decimal import Decimal

from django.test import SimpleTestCase

from Gestion.models import Ingrediente
from Gestion.services import (
    EquivalenciaNoDefinidaError,
    UnidadNoConvertibleError,
    convertir_a_unidad_base,
    unidades_son_compatibles,
)


def _ingrediente(**kwargs) -> Ingrediente:
    datos = {
        'nombre': 'Ingrediente',
        'unidad_medida': 'kg',
        'costo_unitario': Decimal('10.00'),
    }
    datos.update(kwargs)
    return Ingrediente(**datos)


class UnidadesCompatiblesTests(SimpleTestCase):
    def test_misma_unidad(self):
        self.assertTrue(unidades_son_compatibles('kg', 'kg'))

    def test_masa_y_volumen_internos(self):
        self.assertTrue(unidades_son_compatibles('kg', 'g'))
        self.assertTrue(unidades_son_compatibles('lt', 'ml'))

    def test_pz_con_metrica(self):
        self.assertTrue(unidades_son_compatibles('pz', 'kg'))
        self.assertTrue(unidades_son_compatibles('g', 'pz'))
        self.assertTrue(unidades_son_compatibles('pz', 'lt'))

    def test_kg_no_es_compatible_con_lt(self):
        self.assertFalse(unidades_son_compatibles('kg', 'lt'))
        self.assertFalse(unidades_son_compatibles('g', 'ml'))


class ConvertirAUnidadBaseTests(SimpleTestCase):
    def test_misma_unidad_no_convierte(self):
        huevo = _ingrediente(nombre='Huevo', unidad_medida='kg')
        resultado = convertir_a_unidad_base(huevo, Decimal('2'), 'kg')
        self.assertEqual(resultado, Decimal('2'))
        self.assertIsInstance(resultado, Decimal)

    def test_gramos_a_kilogramos(self):
        arroz = _ingrediente(nombre='Arroz', unidad_medida='kg')
        self.assertEqual(
            convertir_a_unidad_base(arroz, Decimal('500'), 'g'),
            Decimal('0.5'),
        )

    def test_kilogramos_a_gramos(self):
        cilantro = _ingrediente(nombre='Cilantro', unidad_medida='g')
        self.assertEqual(
            convertir_a_unidad_base(cilantro, Decimal('0.5'), 'kg'),
            Decimal('500'),
        )

    def test_mililitros_a_litros(self):
        aceite = _ingrediente(nombre='Aceite', unidad_medida='lt')
        self.assertEqual(
            convertir_a_unidad_base(aceite, Decimal('250'), 'ml'),
            Decimal('0.25'),
        )

    def test_pz_a_kg_con_equivalencia(self):
        huevo = _ingrediente(
            nombre='Huevo',
            unidad_medida='kg',
            equivalencia_pza=Decimal('0.060'),
        )
        self.assertEqual(
            convertir_a_unidad_base(huevo, Decimal('3'), 'pz'),
            Decimal('0.180'),
        )

    def test_pz_a_lt_con_equivalencia(self):
        crema = _ingrediente(
            nombre='Crema',
            unidad_medida='lt',
            equivalencia_pza=Decimal('0.250'),
        )
        self.assertEqual(
            convertir_a_unidad_base(crema, Decimal('2'), 'pz'),
            Decimal('0.500'),
        )

    def test_pz_sin_equivalencia_lanza_error_con_nombre(self):
        cebolla = _ingrediente(nombre='Cebolla', equivalencia_pza=None)
        with self.assertRaises(EquivalenciaNoDefinidaError) as ctx:
            convertir_a_unidad_base(cebolla, Decimal('1'), 'pz')
        self.assertIn('Cebolla', str(ctx.exception))

    def test_equivalencia_cero_se_trata_como_faltante(self):
        cebolla = _ingrediente(nombre='Cebolla', equivalencia_pza=Decimal('0'))
        with self.assertRaises(EquivalenciaNoDefinidaError) as ctx:
            convertir_a_unidad_base(cebolla, Decimal('1'), 'pz')
        self.assertIn('Cebolla', str(ctx.exception))

    def test_kg_a_lt_lanza_error_con_nombre(self):
        aceite = _ingrediente(nombre='Aceite', unidad_medida='lt')
        with self.assertRaises(UnidadNoConvertibleError) as ctx:
            convertir_a_unidad_base(aceite, Decimal('1'), 'kg')
        self.assertIn('Aceite', str(ctx.exception))

    def test_base_pz_con_captura_metrica_no_se_inventa_factor(self):
        huevo = _ingrediente(
            nombre='Huevo',
            unidad_medida='pz',
            equivalencia_pza=Decimal('0.060'),
        )
        with self.assertRaises(UnidadNoConvertibleError) as ctx:
            convertir_a_unidad_base(huevo, Decimal('0.12'), 'kg')
        self.assertIn('Huevo', str(ctx.exception))
