from django import forms


class UserForm(forms.Form):
    search = forms.CharField()
