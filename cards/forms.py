from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

INPUT_STYLE = (
    "background:var(--bg-elevated);border:1px solid var(--border);color:var(--text-primary);"
    "padding:11px 14px;border-radius:10px;font-size:15px;font-family:inherit;outline:none;width:100%;"
)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'style': INPUT_STYLE}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'style': INPUT_STYLE}),
            'first_name': forms.TextInput(attrs={'style': INPUT_STYLE}),
            'last_name': forms.TextInput(attrs={'style': INPUT_STYLE}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'style': INPUT_STYLE})
        self.fields['password2'].widget.attrs.update({'style': INPUT_STYLE})
