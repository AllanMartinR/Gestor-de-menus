from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    """Pantalla de inicio tras el login (listados de menús aún no existen)."""
    return render(request, 'accounts/dashboard.html')
