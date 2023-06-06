from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.hashers import make_password
User = get_user_model()
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend

class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserSignupForm(forms.ModelForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Username
        self.fields['password'].widget.attrs['type'] = 'password'
    class Meta:
        model = User
        fields = ['email','username']
    password = forms.CharField(widget=forms.PasswordInput())
    metadata = forms.CharField(widget=forms.Textarea)
    def save(self, request):
        User.objects.create_user(username=self.cleaned_data['username'],email=self.cleaned_data['email'],password=make_password(self.cleaned_data['password']),metadata=self.cleaned_data['metadata'])

        



