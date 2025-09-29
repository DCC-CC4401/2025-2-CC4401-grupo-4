from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User

#TODO: add a CSS classes to the input fields
INPUT_CLASS = "w-full px-4 py-2 border border-border rounded-md bg-background text-foreground mb-2 focus:outline-none focus:ring-2 focus:ring-primary transition"

class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': INPUT_CLASS})
        self.fields['email'].widget.attrs.update({'class': INPUT_CLASS})
        self.fields['password1'].widget.attrs.update({'class': INPUT_CLASS})
        self.fields['password2'].widget.attrs.update({'class': INPUT_CLASS})

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ese email ya está registrado.")
        return email

class CustomLoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': INPUT_CLASS, 'autofocus': True})
        self.fields['password'].widget.attrs.update({'class': INPUT_CLASS})