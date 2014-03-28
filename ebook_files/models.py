from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from datetime import datetime
from company.models import ObjHistory
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.db.models import signals
from django.db.models.signals import pre_delete
import os
FType = (('folder',_('Folder')),('file',_('File')))
RType = (('r',_('read')),('w',_('read + write')),('m',_('read + write + manage')),('s',_('read + write + manage + share')))
accesstype = (('d',_('Download')),('u',_('Upload')))
actiontype = (('add',_('Added')),('download',_('Downloaded')),('edit_perm',_('Changed permissions')),('add_token',_('Added by access token')))
class EFiles(MPTTModel):
    name = models.CharField(max_length=50,verbose_name = _('name'))
    owner = models.ForeignKey(User,verbose_name = _('owner'))
    private = models.BooleanField()
    desc = models.TextField(null=True, blank=True,verbose_name = _('description'))
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children',verbose_name = _('parent'))
    ftype = models.CharField(max_length=6,choices=FType,verbose_name = _('Type'))
    file = models.FileField(upload_to="mfiles", null=True, blank=True, verbose_name = _('file'))
    fsize = models.IntegerField(null=True, blank=True, verbose_name = _('size'))
    class MPTTMeta:
        level_attr = 'mptt_level'
        order_insertion_by=['name']
    def __unicode__(self):
        return self.name
    def get_filename(self):
        return self.file.name.split("/")[-1]
    def have_rights(self,usr,right):
        k=usr 
        r = 0
        s = 0
        if usr.is_superuser:
            r = 1
        elif UsrRightsFile.objects.filter(file=self,user=usr):
            if UsrRightsFile.objects.filter(file=self,user=usr,rtype__in=right):
                r = 1
            else:
                r = 0
        elif UsrRightsFile.objects.filter(file__in=self.get_ancestors(),user=usr,rtype__in=right):
            r = 1
        elif GrRightsFile.objects.filter(file=self,group=usr.groups.all()):
            if GrRightsFile.objects.filter(file=self,group=usr.groups.all(),rtype__in=right):
                r = 1
            else:
                r = 0
        elif GrRightsFile.objects.filter(file__in=self.get_ancestors(),group=usr.groups.all(),rtype__in=right):
            r = 1
        
        else:
            r = 0
   
        return r
   
class CommentFile(models.Model):
    file = models.ForeignKey(EFiles)
    user = models.ForeignKey(User,verbose_name = _('user'))
    comment = models.TextField(null=True, blank=True,verbose_name = _('comment'))
    created = models.DateTimeField(default=datetime.now, blank=True)
    class Meta:
        ordering = ['-created']                                                                   
class HistoryFile(models.Model):
    file = models.ForeignKey(EFiles)
    user = models.ForeignKey(User,verbose_name = _('user'))
    atype = models.CharField(max_length=6,choices=actiontype,verbose_name = _('rights'))
    created = models.DateTimeField(default=datetime.now, blank=True)
    class Meta:
        ordering = ['-created']
class UsrRightsFile(models.Model):
    file = models.ForeignKey(EFiles)
    user = models.ForeignKey(User,verbose_name = _('user'))
    rtype = models.CharField(max_length=6,choices=RType,verbose_name = _('rights'))
class GrRightsFile(models.Model):
    file = models.ForeignKey(EFiles)
    group = models.ForeignKey(Group,verbose_name = _('group'))
    rtype = models.CharField(max_length=6,choices=RType,verbose_name = _('rights'))
class AccessTokens(models.Model):
    access_file = models.ManyToManyField(EFiles,verbose_name = _('Access file'))
    user = models.ForeignKey(User,verbose_name = _('user'))
    email = models.EmailField(max_length=100,null=True, blank=True)
    msg  = models.TextField(verbose_name = _('Message'))
    type = models.CharField(max_length=6,choices=accesstype,verbose_name = _('rights'))
    token = models.TextField(verbose_name = _('description'))
    date_from = models.DateTimeField(verbose_name = _('date_from'),default=datetime.now, blank=True)
    date_to = models.DateTimeField(verbose_name = _('date_to'),default=datetime.now, blank=True)
class FileHistory(models.Model):
    user = models.ForeignKey(User)
    edit = models.DateTimeField(default=datetime.now, blank=True)
    created = models.DateTimeField(default=datetime.now, blank=True)
    content_object = models.ForeignKey(EFiles)
@receiver(models.signals.post_delete, sender=EFiles)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

@receiver(models.signals.pre_save, sender=EFiles)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `MediaFile` object is changed.
    """
    if not instance.pk:
        return False

    try:
        old_file = EFiles.objects.get(pk=instance.pk).file
    except EFiles.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        try:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
        except Exception:
            return False