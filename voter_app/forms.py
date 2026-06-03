# voter_app/forms.py

from django import forms
from .models import Voters, Families, PollingStations, Users
from django.contrib.auth.hashers import make_password


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )


class VoterForm(forms.ModelForm):
    class Meta:
        model  = Voters
        fields = ['cnic', 'full_name', 'age', 'gender', 'family', 'station']
        widgets = {
            'cnic':      forms.TextInput(attrs={'placeholder': 'e.g. 12345-1234567-1'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Full name'}),
            'age':       forms.NumberInput(attrs={'min': 18, 'max': 120}),
            'gender':    forms.Select(),
            'family':    forms.Select(),
            'station':   forms.Select(),
        }

    def clean_cnic(self):
        cnic = self.cleaned_data.get('cnic', '').strip()
        # Basic CNIC format check: 13 digits, optionally with dashes
        digits = cnic.replace('-', '')
        if not digits.isdigit() or len(digits) != 13:
            raise forms.ValidationError("CNIC must contain exactly 13 digits.")
        return cnic


class FamilyForm(forms.ModelForm):
    class Meta:
        model  = Families
        fields = ['head_name', 'permanent_address']
        widgets = {
            'head_name':         forms.TextInput(attrs={'placeholder': 'Head of household name'}),
            'permanent_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Full permanent address'}),
        }


class PollingStationForm(forms.ModelForm):
    class Meta:
        model  = PollingStations
        fields = ['name', 'location_code', 'city', 'capacity']
        widgets = {
            'name':          forms.TextInput(attrs={'placeholder': 'Station name'}),
            'location_code': forms.TextInput(attrs={'placeholder': 'e.g. KP-KOH-01'}),
            'city':          forms.TextInput(attrs={'placeholder': 'City'}),
            'capacity':      forms.NumberInput(attrs={'min': 1}),
        }


class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Set password'}),
        required=False,
        help_text="Leave blank to keep existing password."
    )

    class Meta:
        model  = Users
        fields = ['username', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        raw_pw = self.cleaned_data.get('password')
        if raw_pw:
            user.password_hash = make_password(raw_pw)
        if commit:
            user.save()
        return user
