from django import forms

from .models import Ingrediente


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
            *Ingrediente.UnidadMedida.choices,
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
