from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError
from django.contrib.auth.models import User

from bis.models import *

class UserFormCompanies(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 
            'first_name', 
            'last_name', 
            'email', 
        ]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'bio',
            'numero',
            'photo',
        ]

class PassengerSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_passenger = True
        if commit:
            user.save()
        return user


class CompanySignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_company = True
        if commit:
            user.save()
        return user


class ContactusForm(forms.ModelForm):
 
    class Meta:
        model = Contactus
        fields = '__all__'


PAYMENT_CHOICES = (
    ('M', 'Moncash'),
    ('P', 'PayPal et Carte debit'),
    # ('C', 'Carte-de-débit'),
    # ('B', 'Portefeuille'),
)

CHOICES_TYPE_ID = (
    ('C', 'CIN'),
    ('P', 'Passport'),
    ('N', 'NIF'),
)

class CheckoutForm(forms.Form):
    id_type = forms.ChoiceField(widget=forms.Select(attrs={
        'required':'required'
    }), choices=CHOICES_TYPE_ID)
    id_number = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'ID Number',
        'class': 'form-control',
        'required':'required'
    }))
    nom = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Nom',
        'class': 'form-control',
        'required':'required'
    }))
    prenom = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Prenom',
        'class': 'form-control',
        'required':'required'
    }))
    payment_option = forms.ChoiceField(widget=forms.RadioSelect(attrs={
        'class': 'input-text',
        'required':'required'
    }), choices=PAYMENT_CHOICES)
    # captcha = ReCaptchaField()


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()
    

class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        exclude = ('slug',)
        fields = [
            'name',
            'source',
            'destination',
            'prix',
            'date_depart',
            'nombre_place',
            'description',
            'image',
            'photo_1',
            'photo_2',
            'photo_3',
            'photo_4',
            'is_active'
        ]
        
class TaxiForm(forms.ModelForm):
    class Meta:
        model = Bus
        exclude = ('slug',)
        fields = [
            'name',
            'source',
            'destination',
            'prix',
            'description',
            'image',
            'photo_1',
            'photo_2',
            'photo_3',
            'photo_4',
            'is_taxi'
        ]
        
from ckeditor.widgets import CKEditorWidget

class BroadCast_EmailAdminForm(forms.ModelForm):
    message = forms.CharField(widget=CKEditorWidget(config_name='default'))
    class Meta:
        model = BroadCast_Email
        fields = '__all__'