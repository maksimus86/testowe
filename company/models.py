from django.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
class Company(models.Model):
    name= models.CharField(max_length=150, unique=True,verbose_name = _('Name'))
    post_code = models.CharField(max_length=6,verbose_name = _('Post code'), null=True, blank=True)
    city = models.CharField(max_length=150, verbose_name = _('City'), null=True, blank=True)
    street = models.CharField(max_length=150,verbose_name = _('Street'), null=True, blank=True)
    county = models.CharField(max_length=150,verbose_name = _('County'), null=True, blank=True)
    tel = models.CharField(max_length=20,verbose_name = _('Tel'), null=True, blank=True)
    nip = models.CharField(max_length=20, unique=True, verbose_name = _('Nip'), null=True, blank=True)
    www_site = models.CharField(max_length=150, verbose_name = _('WWW site'), null=True, blank=True)
    u_group = models.ManyToManyField(Group, null=True, blank=True, verbose_name = _('Groups'))
    main = models.BooleanField(default=False, verbose_name = _('Main'))
    cdefault = models.BooleanField(default=False, verbose_name = _('Default'))
    def __unicode__(self):
        if self.main:
            return self.name + " [MAIN]"
        else:
            return self.name
class MyPerson(User):
    class Meta:
        proxy = True
    def __unicode__(self):
        return self.username+ " / "+self.first_name + " " + self.last_name + " - "+self.email
class UsrHistory(models.Model):
    user = models.ForeignKey(User)
    edit = models.DateTimeField(default=datetime.now, blank=True)
    created = models.DateTimeField(default=datetime.now, blank=True)
    content_object = models.ForeignKey(User, related_name="user_h")
class GrHistory(models.Model):
    user = models.ForeignKey(User)
    edit = models.DateTimeField(default=datetime.now, blank=True)
    created = models.DateTimeField(default=datetime.now, blank=True)
    content_object = models.ForeignKey(Group)
class CpHistory(models.Model):
    user = models.ForeignKey(User)
    edit = models.DateTimeField(default=datetime.now, blank=True)
    created = models.DateTimeField(default=datetime.now, blank=True)
    content_object = models.ForeignKey(Company)
class ObjHistory(models.Model):
    user = models.ForeignKey(User)
    edit = models.DateTimeField(default=datetime.now, blank=True)
    created = models.DateTimeField(default=datetime.now, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
class CompanyInfo(models.Model):
    company = models.ForeignKey(Company,verbose_name = _('Company'))
    user = models.ForeignKey(User)
    date = models.DateTimeField(default=datetime.now, blank=True)
class MyProfile(models.Model):  
    user = models.OneToOneField(User)
    adminaccess = models.BooleanField(default=False,verbose_name = _('admina ccess'))
    company = models.ForeignKey(Company,verbose_name = _('Company'))
    lang = models.CharField(max_length=6,choices=settings.LANGUAGE_CODE_TABLE,verbose_name = _('Language'))
    main = models.BooleanField(default=False,verbose_name = _('Main user'))
class GrSetting(models.Model):
    main = models.BooleanField(User)
    group = models.ForeignKey(Group)
