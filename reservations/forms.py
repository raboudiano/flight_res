from django import forms


class BookingForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    seats = forms.IntegerField(min_value=1, initial=1)