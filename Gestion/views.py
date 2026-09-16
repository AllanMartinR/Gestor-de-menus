import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, UpdateView

from .forms import IngredienteForm, IngredientePlatilloFormSet, PlatilloForm
from .models import Ingrediente, Platillo, Menu, MenuPlatillo


def _ingredientes_data_json():
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
    ingrediente = get_object_or_404(Ingrediente, pk=pk, activo=True)
    ingrediente.activo = False
    ingrediente.save(update_fields=['activo'])
    messages.success(request, f'El ingrediente "{ingrediente.nombre}" se dio de baja.')
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
            return self.render_to_response(self.get_context_data(form=form, receta_formset=receta_formset))
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
                context['receta_formset'] = IngredientePlatilloFormSet(self.request.POST, instance=self.object, prefix='receta')
            else:
                context['receta_formset'] = IngredientePlatilloFormSet(instance=self.object, prefix='receta')
        return context

    def form_valid(self, form):
        receta_formset = IngredientePlatilloFormSet(self.request.POST, instance=self.object, prefix='receta')
        if not receta_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, receta_formset=receta_formset))
        self.object = form.save()
        receta_formset.instance = self.object
        receta_formset.save()
        messages.success(self.request, self.get_success_message(form.cleaned_data))
        return HttpResponseRedirect(self.get_success_url())


@login_required
@require_POST
def platillo_baja(request, pk):
    platillo = get_object_or_404(Platillo, pk=pk, activo=True)
    platillo.activo = False
    platillo.save(update_fields=['activo'])
    messages.success(request, f'El platillo "{platillo.nombre}" se dio de baja.')
    return redirect('platillo_list')


@login_required
def armado_menu(request):
    menu_id = request.GET.get('editar')
    menu_a_editar = None

    if menu_id:
        menu_a_editar = get_object_or_404(Menu, pk=menu_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre_menu')
        desayuno_id = request.POST.get('platillo_desayuno')
        comida_id = request.POST.get('platillo_comida')
        cena_id = request.POST.get('platillo_cena')
        editando_id = request.POST.get('menu_id_oculto')

        try:
            if editando_id:
                menu_obj = get_object_or_404(Menu, pk=editando_id)
                menu_obj.nombre = nombre
                menu_obj.save()
                MenuPlatillo.objects.filter(menu=menu_obj).delete()
            else:
                menu_obj = Menu.objects.create(nombre=nombre)

            # Guardamos cada platillo asignado con su respectivo tiempo
            if desayuno_id:
                p_des = Platillo.objects.filter(pk=desayuno_id).first()
                if p_des:
                    MenuPlatillo.objects.create(menu=menu_obj, platillo=p_des, tiempo='Desayuno')
            
            if comida_id:
                p_com = Platillo.objects.filter(pk=comida_id).first()
                if p_com:
                    MenuPlatillo.objects.create(menu=menu_obj, platillo=p_com, tiempo='Comida')

            if cena_id:
                p_cen = Platillo.objects.filter(pk=cena_id).first()
                if p_cen:
                    MenuPlatillo.objects.create(menu=menu_obj, platillo=p_cen, tiempo='Cena')

            messages.success(request, f'¡El menú "{nombre}" se guardó con éxito!')
        except Exception as e:
            messages.error(request, f'Error al procesar el menú: {e}')
            
        return redirect('armado_menu')

    try:
        lista_menus = Menu.objects.all()
    except:
        lista_menus = []
        
    lista_platillos = Platillo.objects.filter(activo=True)
    
    context = {
        'menus': lista_menus,
        'platillos': lista_platillos,
        'menu_a_editar': menu_a_editar,
    }
    
    return render(request, 'gestion/armado_menu.html', context)


@login_required
@require_POST
def menu_eliminar(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    nombre_menu = menu.nombre
    menu.delete()
    messages.success(request, f'El menú "{nombre_menu}" se ha eliminado correctamente.')
    return redirect('armado_menu')