from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, UpdateView

from .forms import IngredienteForm
from .models import Ingrediente


class IngredienteListView(LoginRequiredMixin, ListView):
    model = Ingrediente
    template_name = 'gestion/ingrediente_list.html'
    context_object_name = 'ingredientes'

    def get_queryset(self):
        queryset = Ingrediente.objects.activos()
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(nombre__icontains=q)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '').strip()
        return context


class IngredienteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Ingrediente
    form_class = IngredienteForm
    template_name = 'gestion/ingrediente_form.html'
    success_url = reverse_lazy('ingrediente_list')
    success_message = 'Ingrediente "%(nombre)s" registrado correctamente.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo ingrediente'
        return context


class IngredienteUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Ingrediente
    form_class = IngredienteForm
    template_name = 'gestion/ingrediente_form.html'
    success_url = reverse_lazy('ingrediente_list')
    success_message = 'Ingrediente "%(nombre)s" actualizado correctamente.'

    def get_queryset(self):
        return Ingrediente.objects.activos()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar ingrediente'
        return context


@login_required
@require_POST
def ingrediente_baja(request, pk):
    """Baja lógica: activo=False. No usa .delete() ni DeleteView."""
    ingrediente = get_object_or_404(Ingrediente, pk=pk, activo=True)
    ingrediente.activo = False
    ingrediente.save(update_fields=['activo', 'fecha_actualizacion'])
    messages.success(
        request,
        f'El ingrediente "{ingrediente.nombre}" se dio de baja.',
    )
    return redirect('ingrediente_list')
