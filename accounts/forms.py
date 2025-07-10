from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, NativeLanguage
from django.contrib.auth.forms import UserChangeForm



class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'affiliation']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'native_languages': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

class CustomUserCreationForm(UserCreationForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    native_languages = forms.ModelMultipleChoiceField(
        queryset=NativeLanguage.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=True,
        label="Native Language(s)"
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password1', 'password2',
            'date_of_birth', 'affiliation', 'native_languages',
        ]
