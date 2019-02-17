from django.contrib.auth import get_user_model
from django.contrib.auth import forms as authforms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms
User = get_user_model()


class UserChangeForm(authforms.UserChangeForm):

    class Meta(authforms.UserChangeForm.Meta):
        model = User


class UserCreationForm(authforms.UserCreationForm):

    error_message = authforms.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    class Meta(authforms.UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages["duplicate_username"])


class SignUpForm(UserCreationForm):
    name = forms.CharField(help_text='Name')
    gender = forms.CharField(help_text='Gender')
    email = forms.CharField(help_text='Email')

    class Meta:
        model = User
        fields = ('username', 'gender', 'name', 'email', 'password1', 'password2', )
