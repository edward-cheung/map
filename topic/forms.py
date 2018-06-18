from django import forms


class UserForm(forms.Form):
    username = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
