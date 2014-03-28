#encoding:UTF-8
from django import forms
from django.core import validators
from django.contrib.auth.models import User
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.forms import formsets
from django.forms.models import BaseInlineFormSet
from django.forms.models import BaseModelFormSet
from django.forms.models import modelformset_factory
from ebook_files.models import EFiles,UsrRightsFile,GrRightsFile, AccessTokens
from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField
from django.utils.translation import ugettext_lazy as _
from mptt.forms import TreeNodeChoiceField
import datetime
### testowy koment
class EFileForm(forms.ModelForm):
    class Meta:
        model = EFiles
        exclude=('ftype','private','fsize')
class EFolderForm(forms.ModelForm):
    class Meta:
        model = EFiles
        exclude=('ftype','file','private','desc','fsize')
class ShareForm(forms.ModelForm):
    class Meta:
        model = EFiles
        exclude=('file','ftype','private','fsize')
class EditPublicForm(forms.ModelForm):
    class Meta:
        model = EFiles
        exclude=('ftype','owner','private','fsize')
class EFilesRegularForm(forms.ModelForm):
    class Meta:
        model = EFiles
        exclude=('id','ftype','owner','parent','private','desc','fsize')
class EFilesForm(forms.ModelForm):
    class Meta:
        model = EFiles
        exclude=('ftype','private','fsize')
class EFilesFtpForm(forms.ModelForm):
    class Meta:
        model = EFiles
        exclude=('id','ftype','owner','private','name','desc','fsize','file')
class AccessTokensForm(forms.ModelForm):
    send_email = forms.BooleanField(required=False, label=_("Send email"))
    date_from = forms.DateField(initial=datetime.date.today, label=_("Date from"))
    date_to = forms.DateField(initial=datetime.date.today, label=_("Date to"))
    class Meta:
        model = AccessTokens
        exclude=('token','user','type',)
    def __init__(self, *args, **kwargs):
        super(AccessTokensForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'email',
            
            'msg',
            'date_from',
            'date_to',
            'access_file',
            'send_email'
            ]
class UploadTokensForm(forms.ModelForm):
    send_email = forms.BooleanField(required=False, label=_("Send email"))
    access_file = TreeNodeChoiceField(queryset=EFiles.objects.all(),label=_("Access folder"))
    date_from = forms.DateField(initial=datetime.date.today, label=_("Date from"))
    date_to = forms.DateField(initial=datetime.date.today, label=_("Date to"))
    class Meta:
        model = AccessTokens
        exclude=('token','user','type',)
    def __init__(self, *args, **kwargs):
        super(UploadTokensForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'email',
            
            'msg',
            'date_from',
            'date_to',
            'access_file',
            'send_email'
            ]
