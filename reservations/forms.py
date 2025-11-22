from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove help text (password rules)
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""
        self.fields["username"].help_text = ""

        # Add placeholders
        self.fields["username"].widget.attrs.update({"placeholder": "Choose username"})
        self.fields["email"].widget.attrs.update({"placeholder": "your@email.com"})
        self.fields["first_name"].widget.attrs.update({"placeholder": "Your first name"})
        self.fields["last_name"].widget.attrs.update({"placeholder": "Your last name"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Create password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Confirm password"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class BookingForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    seats = forms.IntegerField(min_value=1, initial=1)