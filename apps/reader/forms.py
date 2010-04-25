from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    username = forms.CharField(label=_("Username"), max_length=30,
                               error_messages={'required': 'Please enter a username.'})
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput,
                               error_messages={'required': 'Please enter a password.'})

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_("Whoopsy-daisy. Try again."))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive."))

        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class SignupForm(forms.Form):
    signup_username = forms.RegexField(regex=r'^\w+$',
                                       max_length=30,
                                       widget=forms.TextInput(),
                                       label=_(u'username'),
                                       error_messages={'required': 'Please enter a username.'})
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(maxlength=75)),
                             label=_(u'email address'),
                                error_messages={'required': 'Please enter your email.'})
    signup_password = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                      label=_(u'password'),
                                      error_messages={'required': 'Please enter a password.'})
    
    def clean_signup_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['signup_username'])
        except User.DoesNotExist:
            return self.cleaned_data['signup_username']
        raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))
        return self.cleaned_data['signup_username']

            
    def save(self, profile_callback=None):
        new_user = User(username=self.cleaned_data['signup_username'],
                        email=self.cleaned_data['email'])
        new_user.set_password(self.cleaned_data['signup_password'])
        new_user.is_active = True
        new_user.save()
        new_user = authenticate(username=self.cleaned_data['signup_username'], password=self.cleaned_data['signup_password'])
        
        return new_user
