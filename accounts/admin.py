# El modelo User de django.contrib.auth ya está registrado en el admin
# (UserAdmin): al crear un usuario se pide contraseña y se guarda hasheada.
# No se re-registra aquí para no duplicar ni alterar ese flujo por defecto.
#
# Futuro: si se necesita distinguir "gerente" y "subgerente" como roles
# distintos, usar grupos de Django o un campo de rol en un perfil. Por ahora
# todos los usuarios autenticados tienen el mismo nivel de acceso.
