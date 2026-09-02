from django.shortcuts import render

# Cuando se agreguen vistas de ingredientes, platillos o menús:
# - FBV: @login_required (django.contrib.auth.decorators)
# - CBV: LoginRequiredMixin como primera clase base
# LoginRequiredMiddleware en settings.py ya exige autenticación por defecto.
