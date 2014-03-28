from django import forms
from django.core import validators
from django.contrib.auth.models import User,Group
from django.forms.util import flatatt
from django.template import loader
from django.utils.datastructures import SortedDict
from django.utils.html import format_html, format_html_join
from django.utils.http import int_to_base36
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.template.loader import render_to_string
from company.models import Company, MyProfile, MyPerson
USERNAME_RE = r'^[\.\w]+$'
attrs_dict = {'class': 'required'}
class UserGroupForms(forms.ModelForm):
    main = forms.BooleanField(required=False, label = _('Main'))
    class Meta:
        exclude = ('permissions',)
        model = Group

class UserForms(forms.ModelForm):
    """
Form for creating a new user account.

Validates that the requested username and e-mail is not already in use.
Also requires the password to be entered twice.

"""
    username = forms.RegexField(regex=USERNAME_RE,
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_("Username"),
                                error_messages={'invalid': _('Username must contain only letters, numbers, dots and underscores.')})
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("Email"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_("Create password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_("Repeat password"))
    class Meta:
        model = User
        fields = ['username','password1','password2','email','first_name', 'last_name', 'groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser']
    def __init__(self, *args, **kwargs):
        super(UserForms, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'username',
            'password1',
            'password2',
            'first_name',
            'last_name',
            'email',
            
            'groups',
            'user_permissions',
            'is_active']
    def clean_username(self):
        """
Validate that the username is alphanumeric and is not already in use.
Also validates that the username is not listed in
``USERENA_FORBIDDEN_USERNAMES`` list.

"""
        try:
            user = get_user_model().objects.get(username__iexact=self.cleaned_data['username'])
            raise forms.ValidationError(_('This username is already in use.'))
        except get_user_model().DoesNotExist:
            pass

            
        return self.cleaned_data['username']

    def clean_email(self):
        """ Validate that the e-mail address is unique. """
        if get_user_model().objects.filter(email__iexact=self.cleaned_data['email']):
            
            raise forms.ValidationError(_('This email is already in use. Please supply a different email.'))
        return self.cleaned_data['email']
    

    def clean(self):
            if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
                if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                    raise forms.ValidationError(_('The two password fields didn\'t match.'))
            return self.cleaned_data
class UserEditForms(forms.ModelForm):
    """
Form for creating a new user account.

Validates that the requested username and e-mail is not already in use.
Also requires the password to be entered twice.

"""
    username = forms.RegexField(regex=USERNAME_RE,
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_("Username"),
                                error_messages={'invalid': _('Username must contain only letters, numbers, dots and underscores.')})
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("Email"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_("New password"),required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_("Confirm password"),required=False)

    class Meta:
        model = User
        fields = ['username','email','first_name', 'last_name', 'groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser']
    def __init__(self, *args, **kwargs):
        super(UserEditForms, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'groups',
            'user_permissions',
            'is_active',
            'is_superuser'
            ]
    def clean_username(self):
        """
Validate that the username is alphanumeric and is not already in use.
Also validates that the username is not listed in
``USERENA_FORBIDDEN_USERNAMES`` list.

"""
        try:
            if self.cleaned_data['username'] != self.instance.username:
                user = get_user_model().objects.get(username__iexact=self.cleaned_data['username'])
                raise forms.ValidationError(_('This username is already in use.'))
        except get_user_model().DoesNotExist:
            pass
        
        return self.cleaned_data['username']

    def clean_email(self):
        """ Validate that the e-mail address is unique. """
        if self.cleaned_data['email'] != self.instance.email:
            if get_user_model().objects.filter(email__iexact=self.cleaned_data['email']):
                
                raise forms.ValidationError(_('This email is already in use. Please supply a different email.'))
        return self.cleaned_data['email']

    def clean(self):
        """
Validates that the values entered into the two password fields match.
Note that an error here will end up in ``non_field_errors()`` because
it doesn't apply to a single field.

"""
        
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_('The two password fields didn\'t match.'))
        return self.cleaned_data
    
class CompanyForms(forms.ModelForm):
    
    class Meta:
        exclude = ('u_group',)
        model = Company
class MyProfileUserForms(forms.ModelForm):
    username = forms.RegexField(regex=USERNAME_RE,
                                max_length=30,
                                widget=forms.TextInput(attrs={'readonly':'readonly'}),
                                label=_("Username"),
                                error_messages={'invalid': _('Username must contain only letters, numbers, dots and underscores.')})
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_("New password"),required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_("Confirm password"),required=False)
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("Email"))
    

    class Meta:
        model = User
        fields = ['username','email','first_name', 'last_name']
    def clean_username(self):
        """
Validate that the username is alphanumeric and is not already in use.
Also validates that the username is not listed in
``USERENA_FORBIDDEN_USERNAMES`` list.

"""
        try:
            if self.cleaned_data['username'] != self.instance.username:
                user = get_user_model().objects.get(username__iexact=self.cleaned_data['username'])
                raise forms.ValidationError(_('This username is already in use.'))
        except get_user_model().DoesNotExist:
            pass
        
        return self.cleaned_data['username']

    def clean_email(self):
        """ Validate that the e-mail address is unique. """
        if self.cleaned_data['email'] != self.instance.email:
            if get_user_model().objects.filter(email__iexact=self.cleaned_data['email']):
                
                raise forms.ValidationError(_('This email is already in use. Please supply a different email.'))
        return self.cleaned_data['email']

    def clean(self):
        """
Validates that the values entered into the two password fields match.
Note that an error here will end up in ``non_field_errors()`` because
it doesn't apply to a single field.

"""
        
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_('The two password fields didn\'t match.'))
        return self.cleaned_data
        
class MyProfileForms(forms.ModelForm):
    
    class Meta:
        model = MyProfile
        fields = ['company','lang']
class MyProfileEditForms(forms.ModelForm):
    
    class Meta:
        model = MyProfile
        fields = ['lang']
class PasswdForms(forms.ModelForm):
    """
Form for creating a new user account.

Validates that the requested username and e-mail is not already in use.
Also requires the password to be entered twice.

"""
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_("Create password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_("Repeat password"))

    class Meta:
        model = User
        fields = ['password1','password2']
    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_('The two password fields didn\'t match.'))
        return self.cleaned_data
class EmployerForm(forms.Form):
    enpt= {}
    attrs = ['id', 'attr1']
    employer = forms.ModelMultipleChoiceField(queryset=MyPerson.objects.all(),label=_("Employees"))

