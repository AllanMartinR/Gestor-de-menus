
import json
 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, UpdateView
 
from .forms import IngredienteForm, IngredientePlatilloFormSet, PlatilloForm
from .models import Ingrediente, Platillo
 
 
def _ingredientes_data_json():
    """Costo unitario y unidad de cada ingrediente activo, para el costeo en vivo del platillo."""
    datos = {
        str(ingrediente.pk): {
            'nombre': ingrediente.nombre,
            'unidad': ingrediente.get_unidad_medida_display(),
            'costo': float(ingrediente.costo_unitario),
        }
        for ingrediente in Ingrediente.objects.filter(activo=True)
    }
    return json.dumps(datos)
 
 
class IngredienteListView(LoginRequiredMixin, ListView):
    model = Ingrediente
    template_name = 'gestion/ingrediente_list.html'
    context_object_name = 'ingredientes'
 
    def get_queryset(self):
        queryset = Ingrediente.objects.filter(activo=True)
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
        return Ingrediente.objects.filter(activo=True)
 
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
    ingrediente.save(update_fields=['activo'])
    messages.success(
        request,
        f'El ingrediente "{ingrediente.nombre}" se dio de baja.',
    )
    return redirect('ingrediente_list')
 
 
class PlatilloListView(LoginRequiredMixin, ListView):
    model = Platillo
    template_name = 'gestion/platillo_list.html'
    context_object_name = 'platillos'
 
    def get_queryset(self):
        queryset = Platillo.objects.filter(activo=True)
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(nombre__icontains=q)
        return queryset
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '').strip()
        return context
 
 
class PlatilloCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Platillo
    form_class = PlatilloForm
    template_name = 'gestion/platillo_form.html'
    success_url = reverse_lazy('platillo_list')
    success_message = 'Platillo "%(nombre)s" registrado correctamente.'
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo platillo'
        context['ingredientes_data_json'] = _ingredientes_data_json()
        if 'receta_formset' not in context:
            if self.request.method == 'POST':
                context['receta_formset'] = IngredientePlatilloFormSet(self.request.POST, prefix='receta')
            else:
                context['receta_formset'] = IngredientePlatilloFormSet(prefix='receta')
        return context
 
    def form_valid(self, form):
        receta_formset = IngredientePlatilloFormSet(self.request.POST, prefix='receta')
        if not receta_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, receta_formset=receta_formset)
            )
        self.object = form.save()
        receta_formset.instance = self.object
        receta_formset.save()
        messages.success(self.request, self.get_success_message(form.cleaned_data))
        return HttpResponseRedirect(self.get_success_url())
 
 
class PlatilloUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Platillo
    form_class = PlatilloForm
    template_name = 'gestion/platillo_form.html'
    success_url = reverse_lazy('platillo_list')
    success_message = 'Platillo "%(nombre)s" actualizado correctamente.'
 
    def get_queryset(self):
        return Platillo.objects.filter(activo=True)
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar platillo'
        context['ingredientes_data_json'] = _ingredientes_data_json()
        if 'receta_formset' not in context:
            if self.request.method == 'POST':
                context['receta_formset'] = IngredientePlatilloFormSet(
                    self.request.POST, instance=self.object, prefix='receta'
                )
            else:
                context['receta_formset'] = IngredientePlatilloFormSet(
                    instance=self.object, prefix='receta'
                )
        return context
 
    def form_valid(self, form):
        receta_formset = IngredientePlatilloFormSet(
            self.request.POST, instance=self.object, prefix='receta'
        )
        if not receta_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, receta_formset=receta_formset)
            )
        self.object = form.save()
        receta_formset.instance = self.object
        receta_formset.save()
        messages.success(self.request, self.get_success_message(form.cleaned_data))
        return HttpResponseRedirect(self.get_success_url())
 
 
@login_required
@require_POST
def platillo_baja(request, pk):
    """Baja lógica: activo=False. No usa .delete() ni DeleteView."""
    platillo = get_object_or_404(Platillo, pk=pk, activo=True)
    platillo.activo = False
    platillo.save(update_fields=['activo'])
    messages.success(
        request,
        f'El platillo "{platillo.nombre}" se dio de baja.',
    )
    return redirect('platillo_list')
