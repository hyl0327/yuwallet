from django import forms
from django.core import validators


class SendingForm(forms.Form):
    address = forms.CharField(
        label='Address',
        max_length=128,
        validators=[validators.validate_slug])
    amount = forms.DecimalField(
        label='Amount (BTC)',
        min_value=0,
        decimal_places=8)

class ConnCredentialsForm(forms.Form):
    rpcuser = forms.CharField(
        label='Username',
        max_length=128,
        validators=[validators.validate_slug])
    rpcpassword = forms.CharField(
        label='Password',
        max_length=128,
        validators=[validators.validate_slug],
        widget=forms.PasswordInput)
    rpcconnect = forms.GenericIPAddressField(
        label='IP',
        initial='127.0.0.1')
    rpcport = forms.IntegerField(
        label='Port',
        initial=8332,
        min_value=1,
        max_value=65535)
