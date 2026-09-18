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
from .models import Ingrediente, Platillo, Menu, MenuPlatillo, IngredientePlatillo


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
    menu_desayuno_ids = []
    menu_comida_ids = []
    menu_cena_ids = []

    if menu_id:
        menu_a_editar = get_object_or_404(Menu, pk=menu_id)
        # Consulta directa a MenuPlatillo
        for mp in MenuPlatillo.objects.filter(menu=menu_a_editar):
            if mp.tiempo == 'Desayuno':
                menu_desayuno_ids.append(mp.platillo.id)
            elif mp.tiempo == 'Comida':
                menu_comida_ids.append(mp.platillo.id)
            elif mp.tiempo == 'Cena':
                menu_cena_ids.append(mp.platillo.id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre_menu')
        
        desayuno_ids = request.POST.getlist('platillo_desayuno')
        comida_ids = request.POST.getlist('platillo_comida')
        cena_ids = request.POST.getlist('platillo_cena')
        
        try:
            comensales_desayuno = int(request.POST.get('comensales_desayuno') or 0)
            comensales_comida = int(request.POST.get('comensales_comida') or 0)
            comensales_cena = int(request.POST.get('comensales_cena') or 0)
        except ValueError:
            comensales_desayuno = comensales_comida = comensales_cena = 0
        
        editando_id = request.POST.get('menu_id_oculto')

        try:
            if editando_id:
                menu_obj = get_object_or_404(Menu, pk=editando_id)
                menu_obj.nombre = nombre
                menu_obj.comensales_desayuno = comensales_desayuno
                menu_obj.comensales_comida = comensales_comida
                menu_obj.comensales_cena = comensales_cena
                menu_obj.save()
                MenuPlatillo.objects.filter(menu=menu_obj).delete()
            else:
                menu_obj = Menu.objects.create(
                    nombre=nombre,
                    comensales_desayuno=comensales_desayuno,
                    comensales_comida=comensales_comida,
                    comensales_cena=comensales_cena
                )

            for d_id in desayuno_ids:
                p = Platillo.objects.filter(pk=d_id).first()
                if p: MenuPlatillo.objects.create(menu=menu_obj, platillo=p, tiempo='Desayuno')
            
            for c_id in comida_ids:
                p = Platillo.objects.filter(pk=c_id).first()
                if p: MenuPlatillo.objects.create(menu=menu_obj, platillo=p, tiempo='Comida')

            for c_id in cena_ids:
                p = Platillo.objects.filter(pk=c_id).first()
                if p: MenuPlatillo.objects.create(menu=menu_obj, platillo=p, tiempo='Cena')

            messages.success(request, f'¡El menú "{nombre}" se guardó con éxito!')
        except Exception as e:
            messages.error(request, f'Error al procesar el menú: {e}')
            
        return redirect('armado_menu')

    menus_procesados = []
    for menu in Menu.objects.all():
        fin = menu.obtener_resumen_financiero()
        
        insumos_separados = {'Desayuno': {}, 'Comida': {}, 'Cena': {}}
        
        # Consulta directa a MenuPlatillo y a IngredientePlatillo
        for mp in MenuPlatillo.objects.filter(menu=menu):
            turno = mp.tiempo
            comensales = getattr(menu, f'comensales_{turno.lower()}', 0)
            if comensales > 0:
                try:
                    for receta in IngredientePlatillo.objects.filter(platillo=mp.platillo):
                        ing_nombre = receta.ingrediente.nombre
                        unidad = receta.ingrediente.get_unidad_medida_display()
                        cant = float(receta.cantidad) * comensales
                        
                        if ing_nombre not in insumos_separados[turno]:
                            insumos_separados[turno][ing_nombre] = {'cantidad': 0, 'unidad': unidad}
                        insumos_separados[turno][ing_nombre]['cantidad'] += cant
                except Exception:
                    pass

        menus_procesados.append({
            'menu': menu,
            'fin': fin,
            'insumos_separados': insumos_separados
        })
        
    lista_platillos = Platillo.objects.filter(activo=True)
    
    context = {
        'menus_procesados': menus_procesados,
        'platillos': lista_platillos,
        'menu_a_editar': menu_a_editar,
        'menu_desayuno_ids': menu_desayuno_ids,
        'menu_comida_ids': menu_comida_ids,
        'menu_cena_ids': menu_cena_ids,
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


@login_required
def reporte_menu(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)
    return render(request, 'gestion/reporte_menu.html', {'menu': menu})