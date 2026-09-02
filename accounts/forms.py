from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión con clases Bootstrap 5."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {
                'class': 'form-control',
                'required': 'required',
                'autocomplete': 'username',
                'placeholder': 'Usuario',
            }
        )
        self.fields['password'].widget.attrs.update(
            {
                'class': 'form-control',
                'required': 'required',
                'autocomplete': 'current-password',
                'placeholder': 'Contraseña',
            }
        )
