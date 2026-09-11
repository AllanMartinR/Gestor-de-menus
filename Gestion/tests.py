from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from Gestion.forms import IngredienteForm
from Gestion.models import Ingrediente


class IngredienteCRUDTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='gerente', password='clave-segura')
        self.client.login(username='gerente', password='clave-segura')

    def test_listado_solo_activos_y_busqueda(self):
        Ingrediente.objects.create(nombre='Arroz', unidad_medida='kg', costo_unitario='10.00')
        Ingrediente.objects.create(
            nombre='Sal',
            unidad_medida='kg',
            costo_unitario='5.00',
            activo=False,
        )
        response = self.client.get(reverse('ingrediente_list'))
        nombres = list(response.context['ingredientes'].values_list('nombre', flat=True))
        self.assertEqual(nombres, ['Arroz'])

        response = self.client.get(reverse('ingrediente_list'), {'q': 'rro'})
        nombres = list(response.context['ingredientes'].values_list('nombre', flat=True))
        self.assertEqual(nombres, ['Arroz'])

    def test_crear_ingrediente(self):
        response = self.client.post(
            reverse('ingrediente_create'),
            {'nombre': 'Aceite', 'unidad_medida': 'l', 'costo_unitario': '25.50'},
        )
        self.assertRedirects(response, reverse('ingrediente_list'))
        self.assertTrue(Ingrediente.objects.filter(nombre='Aceite', activo=True).exists())

    def test_costo_cero_o_negativo_no_guarda(self):
        form = IngredienteForm(
            data={'nombre': 'Azucar', 'unidad_medida': 'kg', 'costo_unitario': '0'}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('mayor a cero', form.errors['costo_unitario'][0])

        form = IngredienteForm(
            data={'nombre': 'Azucar', 'unidad_medida': 'kg', 'costo_unitario': '-1'}
        )
        self.assertFalse(form.is_valid())

    def test_nombre_duplicado_case_insensitive(self):
        Ingrediente.objects.create(nombre='Arroz', unidad_medida='kg', costo_unitario='10.00')
        form = IngredienteForm(
            data={'nombre': 'arroz', 'unidad_medida': 'kg', 'costo_unitario': '12.00'}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('Ya existe un ingrediente con este nombre.', form.errors['nombre'])

    def test_editar_sin_cambiar_nombre_no_es_falso_positivo(self):
        ingrediente = Ingrediente.objects.create(
            nombre='Arroz',
            unidad_medida='kg',
            costo_unitario='10.00',
        )
        form = IngredienteForm(
            data={'nombre': 'Arroz', 'unidad_medida': 'kg', 'costo_unitario': '11.00'},
            instance=ingrediente,
        )
        self.assertTrue(form.is_valid())

    def test_baja_logica_no_elimina_y_sale_del_listado(self):
        ingrediente = Ingrediente.objects.create(
            nombre='Arroz',
            unidad_medida='kg',
            costo_unitario='10.00',
        )
        get_response = self.client.get(reverse('ingrediente_baja', args=[ingrediente.pk]))
        self.assertEqual(get_response.status_code, 405)

        response = self.client.post(reverse('ingrediente_baja', args=[ingrediente.pk]))
        self.assertRedirects(response, reverse('ingrediente_list'))
        ingrediente.refresh_from_db()
        self.assertFalse(ingrediente.activo)
        self.assertTrue(Ingrediente.objects.filter(pk=ingrediente.pk).exists())
        self.assertNotIn(ingrediente, Ingrediente.objects.activos())

    def test_manager_activos_reutilizable(self):
        Ingrediente.objects.create(nombre='Arroz', unidad_medida='kg', costo_unitario='10.00')
        Ingrediente.objects.create(
            nombre='Sal',
            unidad_medida='kg',
            costo_unitario='5.00',
            activo=False,
        )
        self.assertEqual(Ingrediente.objects.activos().count(), 1)
        self.assertEqual(Ingrediente.objects.activos().get().nombre, 'Arroz')
