from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'auth-input',
                'placeholder': 'Choose a username',
                'autocomplete': 'username',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'auth-input',
                'placeholder': 'First name',
                'autocomplete': 'given-name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'auth-input',
                'placeholder': 'Last name',
                'autocomplete': 'family-name',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'auth-input',
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'auth-input',
            'placeholder': 'Repeat your password',
            'autocomplete': 'new-password',
        })