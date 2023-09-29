from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.forms.widgets import HiddenInput, ClearableFileInput

from django.contrib.auth.forms import PasswordResetForm
from loanerlist.gmail import sendingMessage  # Import your sendingMessage function

class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2') #TODO: Add serialization table here
        #TODO: add email verification

    def clean(self):
        email = self.cleaned_data.get('email')
        # if User.objects.filter(email=email).exists():
        #     raise ValidationError("Email already exists. Please use a different email.")
        return self.cleaned_data

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            widget = self.fields[field].widget
            if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.URLInput, forms.NumberInput, forms.Textarea)):
                widget.attrs.update({'class': 'form-control mb-4'})
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.update({'class': 'form-check-input mb-4'})
            elif isinstance(widget, forms.RadioSelect):
                widget.attrs.update({'class': 'form-check-input mb-4'})
            elif isinstance(widget, forms.Select):
                widget.attrs.update({'class': 'form-select mb-4'})

from django.template import loader
class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Custom send email using gmail API service account
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        sendingMessage(from_email, to_email, subject, body)

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [ 'public_email']

    # Add Bootstrap styling to form fields
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['public_email'].label='Show email on public profile'
        self.fields['public_email'].widget.attrs.update({'class': 'form-select mb-4'})
