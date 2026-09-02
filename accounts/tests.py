from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LoginAccessTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='gerente', password='clave-segura')

    def test_dashboard_redirige_a_login_si_no_hay_sesion(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_login_ok_redirige_al_dashboard(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'gerente', 'password': 'clave-segura'},
        )
        self.assertRedirects(response, reverse('dashboard'))

    def test_credenciales_incorrectas_muestran_error(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'gerente', 'password': 'incorrecta'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].non_field_errors())

    def test_no_existe_ruta_de_registro_publico(self):
        for path in ('/signup/', '/register/', '/registro/', '/accounts/signup/'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 404)
