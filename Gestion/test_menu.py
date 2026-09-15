from django.db import IntegrityError
from django.db.models import RestrictedError
from django.test import TestCase

from Gestion.models import Menu, MenuPlatillo, Platillo


class MenuModeloTests(TestCase):
    def test_crear_menu(self):
        menu = Menu.objects.create(nombre='Menú ejecutivo')
        self.assertEqual(menu.nombre, 'Menú ejecutivo')
        self.assertTrue(menu.activo)
        self.assertIsNone(menu.descripcion)

    def test_asociar_varios_platillos(self):
        menu = Menu.objects.create(nombre='Menú del día')
        sopa = Platillo.objects.create(nombre='Sopa de fideo')
        guisado = Platillo.objects.create(nombre='Guisado de res')
        MenuPlatillo.objects.create(menu=menu, platillo=sopa)
        MenuPlatillo.objects.create(menu=menu, platillo=guisado)
        platillos = list(menu.composicion.values_list('platillo__nombre', flat=True))
        self.assertEqual(sorted(platillos), ['Guisado de res', 'Sopa de fideo'])

    def test_no_duplicar_platillo_en_el_mismo_menu(self):
        menu = Menu.objects.create(nombre='Menú único')
        platillo = Platillo.objects.create(nombre='Enchiladas')
        MenuPlatillo.objects.create(menu=menu, platillo=platillo)
        with self.assertRaises(IntegrityError):
            MenuPlatillo.objects.create(menu=menu, platillo=platillo)

    def test_eliminar_platillo_asociado_esta_restringido(self):
        menu = Menu.objects.create(nombre='Menú restrict')
        platillo = Platillo.objects.create(nombre='Arroz a la mexicana')
        MenuPlatillo.objects.create(menu=menu, platillo=platillo)
        with self.assertRaises(RestrictedError):
            platillo.delete()
        self.assertTrue(Platillo.objects.filter(pk=platillo.pk).exists())
        self.assertTrue(MenuPlatillo.objects.filter(menu=menu, platillo=platillo).exists())

    def test_baja_logica_de_platillo_conserva_la_asociacion(self):
        menu = Menu.objects.create(nombre='Menú histórico')
        platillo = Platillo.objects.create(nombre='Gelatina')
        MenuPlatillo.objects.create(menu=menu, platillo=platillo)
        platillo.activo = False
        platillo.save(update_fields=['activo'])
        platillo.refresh_from_db()
        self.assertFalse(platillo.activo)
        self.assertTrue(MenuPlatillo.objects.filter(menu=menu, platillo=platillo).exists())

    def test_eliminar_menu_elimina_la_composicion(self):
        menu = Menu.objects.create(nombre='Menú temporal')
        platillo = Platillo.objects.create(nombre='Agua de jamaica')
        MenuPlatillo.objects.create(menu=menu, platillo=platillo)
        menu.delete()
        self.assertFalse(Menu.objects.filter(nombre='Menú temporal').exists())
        self.assertFalse(MenuPlatillo.objects.filter(platillo=platillo).exists())
        self.assertTrue(Platillo.objects.filter(pk=platillo.pk).exists())
