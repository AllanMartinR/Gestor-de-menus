
from django import forms
from django.forms import inlineformset_factory
 
from .models import Ingrediente, IngredientePlatillo, Platillo
 
 
class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = ('nombre', 'unidad_medida', 'costo_unitario')
        labels = {
            'nombre': 'Nombre',
            'unidad_medida': 'Unidad de medida',
            'costo_unitario': 'Costo unitario',
        }
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej. Arroz',
                    'autocomplete': 'off',
                }
            ),
            'unidad_medida': forms.Select(attrs={'class': 'form-select'}),
            'costo_unitario': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '0.00',
                    'step': '0.01',
                    'min': '0.01',
                }
            ),
        }
        error_messages = {
            'unidad_medida': {
                'required': 'Seleccione una unidad de medida.',
            },
            'nombre': {
                'required': 'El nombre es obligatorio.',
            },
            'costo_unitario': {
                'required': 'El costo unitario es obligatorio.',
            },
        }
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unidad_medida'].required = True
        self.fields['unidad_medida'].choices = [
            ('', 'Seleccione una unidad'),
            *Ingrediente.UNIDADES,
        ]
 
    def full_clean(self):
        super().full_clean()
        for name in self.fields:
            if self.errors.get(name):
                css = self.fields[name].widget.attrs.get('class', '')
                if 'is-invalid' not in css.split():
                    self.fields[name].widget.attrs['class'] = f'{css} is-invalid'.strip()
 
    def clean_nombre(self):
        nombre = (self.cleaned_data.get('nombre') or '').strip()
        if not nombre:
            raise forms.ValidationError('El nombre es obligatorio.')
        duplicados = Ingrediente.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)
        if duplicados.exists():
            raise forms.ValidationError('Ya existe un ingrediente con este nombre.')
        return nombre
 
    def clean_costo_unitario(self):
        costo = self.cleaned_data.get('costo_unitario')
        if costo is None:
            raise forms.ValidationError('El costo unitario es obligatorio.')
        if costo <= 0:
            raise forms.ValidationError('El costo unitario debe ser mayor a cero.')
        return costo
 
 
class PlatilloForm(forms.ModelForm):
    class Meta:
        model = Platillo
        fields = ('nombre', 'descripcion')
        labels = {
            'nombre': 'Nombre del platillo',
            'descripcion': 'Descripción',
        }
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej. Enchiladas verdes',
                    'autocomplete': 'off',
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Descripción breve del platillo (opcional)',
                    'rows': 3,
                }
            ),
        }
        error_messages = {
            'nombre': {
                'required': 'El nombre del platillo es obligatorio.',
            },
        }
 
    def full_clean(self):
        super().full_clean()
        for name in self.fields:
            if self.errors.get(name):
                css = self.fields[name].widget.attrs.get('class', '')
                if 'is-invalid' not in css.split():
                    self.fields[name].widget.attrs['class'] = f'{css} is-invalid'.strip()
 
    def clean_nombre(self):
        nombre = (self.cleaned_data.get('nombre') or '').strip()
        if not nombre:
            raise forms.ValidationError('El nombre del platillo es obligatorio.')
        duplicados = Platillo.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)
        if duplicados.exists():
            raise forms.ValidationError('Ya existe un platillo con este nombre.')
        return nombre
 
 
class IngredientePlatilloForm(forms.ModelForm):
    class Meta:
        model = IngredientePlatillo
        fields = ('ingrediente', 'cantidad')
        widgets = {
            'ingrediente': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Cantidad',
                    'step': '0.001',
                    'min': '0.001',
                }
            ),
        }
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingrediente'].queryset = Ingrediente.objects.filter(activo=True)
        self.fields['ingrediente'].empty_label = 'Seleccione un ingrediente'
        self.fields['ingrediente'].required = False
        self.fields['cantidad'].required = False
 
    def clean(self):
        cleaned_data = super().clean()
        ingrediente = cleaned_data.get('ingrediente')
        cantidad = cleaned_data.get('cantidad')
        if ingrediente and not cantidad:
            self.add_error('cantidad', 'Indique la cantidad para este ingrediente.')
        if cantidad and not ingrediente:
            self.add_error('ingrediente', 'Seleccione el ingrediente.')
        return cleaned_data
 
 
IngredientePlatilloFormSet = inlineformset_factory(
    Platillo,
    IngredientePlatillo,
    form=IngredientePlatilloForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)
 
