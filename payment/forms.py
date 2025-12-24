from django import forms
from .models import ShippingAddress
 
class ShippingForm(forms.ModelForm):
    shipping_full_name = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'UserName'}),required=False)
    shipping_email = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'Email'}),required=False)
    shipping_address1 = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'Address1'}),required=False)
    shipping_address2 = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'Address2'}),required=True)
    shipping_city = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'City'}),required=False)
    shipping_state = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'State'}),required=True)
    shipping_pincode = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'Pincode'}),required=True)
    shipping_country = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'Country'}),required=True)
	


	
    class Meta:
        model = ShippingAddress
        fields = ['shipping_full_name', 'shipping_email', 'shipping_address1', 'shipping_address2', 'shipping_city', 'shipping_state', 'shipping_pincode', 'shipping_country']
        exclude = ('user',)


class PaymentForm(forms.Form):
    card_name = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'Card Name'}),required=True)
    card_number = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'Card Number'}),required=True)
    card_exp_date = forms.DateField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'Card Date'}),required=True)
    card_cvv_number = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'CVV Number'}),required=True)
    card_address1 = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'Billing Address1'}),required=True)
    card_address2 = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'Billing Address2'}),required=False)
    card_city = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'City'}),required=True)
    card_state = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'State'}),required=True)
    card_pincode = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'Pincode'}),required=True)
    card_country = forms.CharField(label="", widget=forms.TextInput({'class':'form-control','placeholder':'Country'}),required=True)
	
