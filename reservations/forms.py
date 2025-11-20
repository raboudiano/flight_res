from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove help text (password rules)
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""
        self.fields["username"].help_text = ""

        # Optional: placeholders
        self.fields["username"].widget.attrs.update({"placeholder": "Choose username"})
        self.fields["email"].widget.attrs.update({"placeholder": "Your email"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Confirm password"})


class BookingForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    seats = forms.IntegerField(min_value=1, initial=1)
