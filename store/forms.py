from django import forms
from .models import Order
from django.contrib.auth.forms import UserCreationForm # <-- New Import
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    # Add email field to the signup form (optional but recommended)
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap classes to fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'city', 'country']
        
        # Apply Bootstrap styling classes (optional, but good practice)
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
    
    # Optional: Apply Bootstrap classes
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})