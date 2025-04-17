from django import forms
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Add email field

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)