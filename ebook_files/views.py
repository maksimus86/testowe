#encoding:UTF-8
from django.shortcuts import render
from django.template import *
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import simplejson
from django.core import serializers
from django.core.paginator import Paginator
import json
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME
from django.forms.models import model_to_dict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ebook_files.models import EFiles,UsrRightsFile,GrRightsFile,HistoryFile,CommentFile, AccessTokens,FileHistory
from ebook_files.forms import EFileForm, EFolderForm, EFilesForm, EFilesRegularForm,ShareForm, AccessTokensForm, EFilesFtpForm,EditPublicForm, UploadTokensForm
from ebook.decorators import myuser_login_required
from ebook.views import table_builder
from company.models import Company, MyProfile, CompanyInfo, ObjHistory
import os
from ftplib import FTP, error_perm
from django.core.mail import send_mail
from datetime import datetime
from django.core.files import File
import os
import sys
import zipfile
import django
from ebook_files.templatetags.files_tag import humanize_bytes
@myuser_login_required
def share_file(request,nr,template_name=''):
    fol = get_object_or_404(EFiles,id=nr)
    if fol.private:
        activepr = 'lactive'
    else:
        activepu = 'lactive'
    title = "Share private and send to public"
    title2 =  fol.ftype+" "+fol.name
    breadcrumb = []
    breadcrumb.append({'name':'Private files','url':'/files/private/'})
    breadcrumb.append({'name':title,'url':request.get_full_path()})
    if settings.SHARE_IN_GROUP:
        users = User.objects.filter(myprofile__company__main=True,groups__in=request.user.groups.all())
        groups = Group.objects.filter(user__myprofile__company__main=True).distinct()
        exusers = User.objects.filter(myprofile__company__main=False)
        rxgroups = Group.objects.filter(user__myprofile__company__main=False,groups__in=request.user.groups.all()).distinct()
    else:
        users = User.objects.filter(myprofile__company__main=True,)
        groups = Group.objects.filter(user__myprofile__company__main=True).distinct()
        exusers = User.objects.filter(myprofile__company__main=False)
        rxgroups = Group.objects.filter(user__myprofile__company__main=False).distinct()
    form = ShareForm(instance=fol)
    create_rights = 1
    
    urr = UsrRightsFile.objects.filter(file=fol,user__myprofile__company__main=True)
    grr = GrRightsFile.objects.filter(file=fol,group__company__main=True)
    exurr = UsrRightsFile.objects.filter(file=fol,user__myprofile__company__main=False)
    exgrr = GrRightsFile.objects.filter(file=fol,group__company__main=False)
    m_type = ContentType.objects.get_for_model(fol)
    his_obj = FileHistory.objects.get(content_object=fol)
    if request.method == 'POST':
        form = ShareForm(request.POST,instance=fol) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            urr.delete()
            grr.delete()
            exurr.delete()
            exgrr.delete()
            for i in request.POST:
                u=0  
                f = form.save()
                f.private=False
                f.save()
                u=u+1
                HistoryFile.objects.create(file=fol, user=request.user,atype='edit_perm')
                if his_obj:
                    
                    his_obj.edit = datetime.now()
                    his_obj.save()
                else:
                    his_obj = FileHistory()
                    his_obj.user = request.user
                    his_obj.content_object = f
                    his_obj.save()
                if "rght_group_" in i:
                    nr = i.split("_")[2]
                    tg = Group.objects.get(id=nr)
                    ncr = GrRightsFile()
                    ncr.file=fol
                    ncr.group = tg
                    ncr.rtype = request.POST.get(i)
                    ncr.save()
                if "rght_user_" in i:
                    nr = i.split("_")[2]
                    tu = User.objects.get(id=nr)
                    ncr = UsrRightsFile()
                    ncr.file=fol
                    ncr.user = tu
                    ncr.rtype = request.POST.get(i)
                    ncr.save()
            for z in fol.get_descendants():
                urr1 = UsrRightsFile.objects.filter(file=z)
                grr1 = GrRightsFile.objects.filter(file=z)
                HistoryFile.objects.create(file=z, user=request.user,atype='edit_perm')
                urr1.delete()
                grr1.delete()
                z.private=False
                z.save()
                his_obj = FileHistory.objects.filter(content_object=z)
                if his_obj:
                    his_obj = his_obj[0]
                    his_obj.edit = datetime.now()
                    his_obj.save()
                else:
                    his_obj = FileHistory()
                    his_obj.user = request.user
                    his_obj.content_object = z
                    his_obj.save()
                for i in request.POST:
                    
                    if "rght_group_" in i:
                        nr = i.split("_")[2]
                        tg = Group.objects.get(id=nr)
                        ncr = GrRightsFile()
                        ncr.file=z
                        ncr.group = tg
                        ncr.rtype = request.POST.get(i)
                        ncr.save()
                    if "rght_user_" in i:
                        nr = i.split("_")[2]
                        tu = User.objects.get(id=nr)
                        ncr = UsrRightsFile()
                        ncr.file=z
                        ncr.user = tu
                        ncr.rtype = request.POST.get(i)
                        ncr.save()
        if fol.parent and not fol.parent.private:
            parent = "?mparent="+str(fol.parent.id)
        else:
            parent=""
        back_href = '/files/public/'+parent
        return redirect(back_href)
    if request.user.is_superuser: 
        form.fields['parent'].queryset = EFiles.objects.filter(private=False).filter(ftype="folder")
    else:
       
        form.fields['parent'].queryset = EFiles.objects.filter(private=False).filter(ftype="folder").filter(Q(grrightsfile__group__in=request.user.groups.all())&Q(grrightsfile__rtype__in=['w','m','s'])|Q(usrrightsfile__user=request.user)&Q(usrrightsfile__rtype__in=['m','s']))
        form.fields['owner'].queryset = User.objects.filter(id=request.user.id)
        form.fields['parent'].empty_label = None
    
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
@myuser_login_required
def edit_file_public(request,nr,template_name=''):
    fol = EFiles.objects.get(id=nr,private=False)
    activepu = 'lactive'
    create_rights = fol.have_rights(request.user,['s'])
    if fol.have_rights(request.user,['w','m','s']):
        pass
    
    elif not request.user.myprofile.company.main:
        login_url='/error_perm/'
        return redirect(login_url)
    else:
        login_url='/error_perm/'
        return redirect(login_url)
    if fol.ftype == 'file':
        form = EditPublicForm(instance=fol)
    else:
        form = ShareForm(instance=fol)
    title = "Edit public"
    title2 =  fol.ftype+" "+fol.name
    breadcrumb = []
    breadcrumb.append({'name':'Public files','url':'/files/public/'})
    breadcrumb.append({'name':title,'url':request.get_full_path()})
    users = User.objects.filter(myprofile__company__main=True)
    groups = Group.objects.filter(user__myprofile__company__main=True).distinct()
    exusers = User.objects.filter(myprofile__company__main=False)
    rxgroups = Group.objects.filter(user__myprofile__company__main=False).distinct()
    #form = ShareForm(instance=fol, initial={'owner': fol.owner})
    #create_rights = 1
    urr = UsrRightsFile.objects.filter(file=fol,user__myprofile__company__main=True)
    grr = GrRightsFile.objects.filter(file=fol,group__company__main=True)
    exurr = UsrRightsFile.objects.filter(file=fol,user__myprofile__company__main=False)
    exgrr = GrRightsFile.objects.filter(file=fol,group__company__main=False)
    if request.method == 'POST':
        if fol.ftype == 'file':
            form = EditPublicForm(request.POST, request.FILES,instance=fol)
        else:
            form = ShareForm(request.POST, request.FILES,instance=fol)
       
        if form.is_valid(): # All validation rules pass
            if request.user.myprofile.company.main:
                GrRightsFile.objects.filter(file=fol).delete()
                UsrRightsFile.objects.filter(file=fol).delete()
            f = form.save()
            if f.ftype=="file":
                f.fsize=f.file.size
                f.save()
            HistoryFile.objects.create(file=fol, user=request.user,atype='edit_perm')
            m_type = ContentType.objects.get_for_model(fol)
            his_obj = FileHistory.objects.filter(content_object=fol)
            if his_obj:
                his_obj = his_obj[0]
                his_obj.edit = datetime.now()
                his_obj.save()
            else:
                his_obj = FileHistory()
                his_obj.user = request.user
                his_obj.content_object = fol
                his_obj.save()
            for i in request.POST:
                u=0
                if request.user.myprofile.company.main:
                    if "rght_group_" in i:
                        nr = i.split("_")[2]
                        tg = Group.objects.get(id=nr)
                        ncr = GrRightsFile()
                        ncr.file=fol
                        ncr.group = tg
                        ncr.rtype = request.POST.get(i)
                        ncr.save()
                    if "rght_user_" in i:
                        nr = i.split("_")[2]
                        tu = User.objects.get(id=nr)
                        ncr = UsrRightsFile()
                        ncr.file=fol
                        ncr.user = tu
                        ncr.rtype = request.POST.get(i)
                        ncr.save()
            
            if request.user.myprofile.company.main:
                for z in fol.get_descendants():
                    GrRightsFile.objects.filter(file=z).delete()
                    UsrRightsFile.objects.filter(file=z).delete()
                    
                    for i in request.POST:
                        z.private=False
                        z.save()
                        HistoryFile.objects.create(file=z, user=request.user,atype='edit_perm')
                        m_type = ContentType.objects.get_for_model(fol)
                        his_obj = FileHistory.objects.filter(content_object=z)
                        if his_obj:
                            his_obj = his_obj[0]
                            his_obj.edit = datetime.now()
                            his_obj.save()
                        else:
                            his_obj = FileHistory()
                            his_obj.user = request.user
                            his_obj.content_object = z
                            his_obj.save()
                        if "rght_group_" in i:
                            nr = i.split("_")[2]
                            tg = Group.objects.get(id=nr)
                            ncr = GrRightsFile()
                            ncr.file=z
                            ncr.group = tg
                            ncr.rtype = request.POST.get(i)
                            ncr.save()
                        if "rght_user_" in i:
                            nr = i.split("_")[2]
                            tu = User.objects.get(id=nr)
                            ncr = UsrRightsFile()
                            ncr.file=z
                            ncr.user = tu
                            ncr.rtype = request.POST.get(i)
                            ncr.save()
            
            if f.parent and not f.parent.private:
                parent = "?mparent="+str(f.parent.id)
            else:
                parent=""
            back_href = '/files/public/'+parent
            return redirect(back_href)
        
    if request.user.is_superuser: 
        form.fields['parent'].queryset = EFiles.objects.filter(private=False).filter(ftype="folder")
    else:
        if fol.ftype=="folder":
            form.fields['parent'].queryset = EFiles.objects.filter(private=False).filter(ftype="folder").filter(Q(grrightsfile__group__in=request.user.groups.all())&Q(grrightsfile__rtype__in=['m','s'])|Q(usrrightsfile__user=request.user)&Q(usrrightsfile__rtype__in=['m','s']))
        else:
            form.fields['parent'].queryset = EFiles.objects.filter(private=False).filter(ftype="folder").filter(Q(grrightsfile__group__in=request.user.groups.all())&Q(grrightsfile__rtype__in=['w','m','s'])|Q(usrrightsfile__user=request.user)&Q(usrrightsfile__rtype__in=['w','m','s']))
        
        form.fields['parent'].empty_label = None    
    for i in exurr:
        print i.user    
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
@myuser_login_required
def edit_file(request,nr,template_name=''):
    title = "Edit private"
    activepr = 'lactive'
    breadcrumb = []
    breadcrumb.append({'name':'Private files','url':'/files/private/'})
    breadcrumb.append({'name':'Add private directory','url':request.get_full_path()})
    fol = EFiles.objects.get(id=nr)
    title2 =  fol.ftype+" "+fol.name
    if fol.ftype == 'file':
        form = EFileForm(instance=fol)
    else:
        form = EFolderForm(instance=fol)
   
    
    if request.method == 'POST':
        form = EFileForm(request.POST, request.FILES,instance=fol) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            
            f = form.save()
            if f.ftype=="file":
                f.fsize=f.file.size
                f.save()
            m_type = ContentType.objects.get_for_model(fol)
            his_obj = FileHistory.objects.filter(content_object=fol)
            if his_obj:
                his_obj = his_obj[0]
                his_obj.edit = datetime.now()
                his_obj.save()
            else:
                his_obj = FileHistory()
                his_obj.user = request.user
                his_obj.content_object = fol
                his_obj.save()
            HistoryFile.objects.create(file=f, user=request.user,atype='edit_perm')
            if f.parent and f.parent.private:
                parent = "?mparent="+str(f.parent.id)
            else:
                parent=""
            back_href = '/files/private/'+parent
            return redirect(back_href)
        
        fg = EFilesRights.objects.filter(file=fol)
        
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
@myuser_login_required
def download_public(request,nr,template_name=''):
    """                                                                         
    Send a file through Django without loading the whole file into              
    memory at once. The FileWrapper will turn the file object into an           
    iterator for chunks of 8KB.                                                 
    """
    
    fol = EFiles.objects.get(id=nr)
    if fol.private:
        activepr = 'lactive'
    else:
        activepu = 'lactive'
    if fol.have_rights(request.user,['r','w','m','s']):
        pass
    else:
        login_url='/error_perm/'
        return redirect(login_url)
    form = EFolderForm(instance=fol)
    filename = fol.file.name.split('/')[-1]
    HistoryFile.objects.create(file=fol, user=request.user,atype='download')
    response = HttpResponse(fol.file, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
@myuser_login_required
def download(request,nr,template_name=''):
    """                                                                         
    Send a file through Django without loading the whole file into              
    memory at once. The FileWrapper will turn the file object into an           
    iterator for chunks of 8KB.                                                 
    """
    
    fol = EFiles.objects.get(id=nr)
    if fol.private:
        activepr = 'lactive'
    else:
        activepu = 'lactive'
    if fol.have_rights(request.user,['r','w','m','s']):
        pass
    else:
        login_url='/error_perm/'
        return redirect(login_url)
    form = EFolderForm(instance=fol)
    filename = fol.file.name.split('/')[-1]
  
    response = HttpResponse(fol.file, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    HistoryFile.objects.create(file=fol, user=request.user,atype='download')
    return response
@myuser_login_required
def public_upload_file(request,nr,template_name=''):
    title = "Add public file"
    breadcrumb = []
    
    activepu = 'lactive'
    breadcrumb.append({'name':'public files','url':'/files/public/'})
    breadcrumb.append({'name':'Add public file','url':request.get_full_path()})
    users = User.objects.filter(myprofile__company__main=True)
    groups = Group.objects.filter(company__main=True)
    exusers = User.objects.filter(myprofile__company__main=False)
    rxgroups = Group.objects.filter(user__myprofile__company__main=False).distinct()
    if nr < 1:
        parent = None
    else:
        parent = get_object_or_404(EFiles,id=nr)
        urr = UsrRightsFile.objects.filter(file=parent,user__myprofile__company__main=True)
        grr = GrRightsFile.objects.filter(file=parent,group__company__main=True)
        exurr = UsrRightsFile.objects.filter(file=parent,user__myprofile__company__main=False)
        exgrr = GrRightsFile.objects.filter(file=parent,group__company__main=False)
        if parent.have_rights(request.user,['w','m','s']):
            pass
        else:
            login_url='/error_perm/'
            return redirect(login_url)
    mback = parent
    if request.user.is_superuser:  
        form = EFilesForm(initial={'owner': request.user,"parent":parent})
    else:
        form = EFilesForm(initial={'owner': request.user,"parent":parent})
    if parent:
        create_rights = parent.have_rights(request.user,['s'])
    mback = parent
    if request.method == 'POST':
        if request.user.is_superuser:  
            form = EFilesForm(request.POST, request.FILES)
        else:
            form = EFilesRegularForm(request.POST, request.FILES)
        
        if form.is_valid(): # All validation rules pass
            f = form.save(commit=False)
            f.private=False
            f.owner = request.user
            f.ftype='file'
            f.parent = EFiles.objects.get(id=request.POST.get('parent'))
            f.save()
            HistoryFile.objects.create(file=f, user=request.user,atype='add')
            
            his_obj = FileHistory.objects.filter(content_object=f)
            if his_obj:
                his_obj = his_obj[0]
                his_obj.edit = datetime.now()
                his_obj.save()
            else:
                his_obj = FileHistory()
                his_obj.user = request.user
                his_obj.content_object = f
                his_obj.save()
            for i in request.POST:
                u=0
                if request.user.myprofile.company.main:
                    if "rght_group_" in i:
                        nr = i.split("_")[2]
                        tg = Group.objects.get(id=nr)
                        ncr = GrRightsFile()
                        ncr.file=f
                        ncr.group = tg
                        ncr.rtype = request.POST.get(i)
                        ncr.save()
                        u=u+1
                    if "rght_user_" in i:
                        nr = i.split("_")[2]
                        tu = User.objects.get(id=nr)
                        ncr = UsrRightsFile()
                        ncr.file=f
                        ncr.user = tu
                        ncr.rtype = request.POST.get(i)
                        ncr.save()
                        u=u+1
            if u==0:
                urr = UsrRightsFile.objects.filter(file=f.parent)
                grr = GrRightsFile.objects.filter(file=f.parent)
                for i in urr:
                    ncr = UsrRightsFile()
                    ncr.user = i.user
                    ncr.file=f
                    ncr.rtype = i.rtype
                    ncr.save()
                for i in grr:
                    ncr = GrRightsFile()
                    ncr.group = i.group
                    ncr.file=f
                    ncr.rtype = i.rtype
                    ncr.save()
            if f.parent and not f.parent.private:
                parent = "?mparent="+str(f.parent.id)
            else:
                parent=""
            back_href = '/files/public/'+parent
            return redirect(back_href)
    if request.user.is_superuser: 
        form.fields['parent'].queryset = EFiles.objects.filter(private=False).filter(ftype="folder")
    else:
        form.fields['parent'].queryset = EFiles.objects.filter(private=False).filter(ftype="folder").filter(Q(grrightsfile__group__in=request.user.groups.all())&Q(grrightsfile__rtype__in=['w','m','s'])|Q(usrrightsfile__user=request.user)&Q(usrrightsfile__rtype__in=['w','m','s']))
        form.fields['owner'].queryset = User.objects.filter(id=request.user.id)
        form.fields['parent'].empty_label = None
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
@myuser_login_required
def upload_file(request,nr,template_name=''):
    title = "Add private file"
    breadcrumb = []
    
    activepr = 'lactive'
    
    breadcrumb.append({'name':'Private files','url':'/files/private/'})
    breadcrumb.append({'name':'Add private file','url':request.get_full_path()})
    if nr < 1:
        parent = None
    else:
        parent = get_object_or_404(EFiles,id=nr)
    if request.user.is_superuser:  
        form = EFilesForm(initial={'owner': request.user,"parent":parent})
    else:
        form = EFilesForm(initial={'owner': request.user,"parent":parent})
    if parent:
        if parent.owner == request.user:
            pass
        else:
            login_url='/error_perm/'
            return redirect(login_url)
    else:
        if request.user.is_superuser:
            pass
        else:
            login_url='/error_perm/'
            return redirect(login_url)
    if request.method == 'POST':
        if request.user.is_superuser:  
            form = EFilesForm(request.POST, request.FILES)
        else:
            form = EFilesRegularForm(request.POST, request.FILES)
        
        if form.is_valid(): # All validation rules pass
            f = form.save(commit=False)
            f.owner=request.user
            f.private=True
            f.parent=parent
            f.ftype='file'
            f.save()
            his_obj = FileHistory.objects.filter(content_object=f)
            HistoryFile.objects.create(file=f, user=request.user,atype='add')
            if his_obj:
                his_obj = his_obj[0]
                his_obj.edit = datetime.now()
                his_obj.save()
            else:
                his_obj = FileHistory()
                his_obj.user = request.user
                his_obj.content_object = f
                his_obj.save()
            if f.parent and f.parent.private:
                parent = "?mparent="+str(f.parent.id)
            else:
                parent=""
            back_href = '/files/private/'+parent
            return redirect(back_href)
    if request.user.is_superuser: 
        form.fields['parent'].queryset = EFiles.objects.filter(private=True).filter(ftype="folder")
    else:
        form.fields['parent'].queryset = EFiles.objects.filter(private=True).filter(ftype="folder").filter(owner=request.user)
        form.fields['owner'].queryset = User.objects.filter(id=request.user.id)              
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
def add_file(request,template_name=''):
    title = "Add private directory"
    
    activepr = 'lactive'
    
    breadcrumb = []
    breadcrumb.append({'name':'Private files','url':'/files/public/'})
    breadcrumb.append({'name':'Add private directory','url':request.get_full_path()})
    
    if int(request.GET.get('mparent',0))<1:
        parent = None
    else:
        parent = EFiles.objects.get(id=request.GET.get('mparent',None))
    form = EFolderForm(initial={'owner': request.user,"parent":parent})
    
    if request.method == 'POST':
        form = EFolderForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            f = form.save(commit=False)
            fol = f
            f.private=True
            f.ftype='folder'
            f.save()
            if f.ftype=="file":
                f.fsize=f.file.size
                f.save()
            
            his_obj = FileHistory.objects.filter(content_object=fol)
            if his_obj:
                his_obj = his_obj[0]
                his_obj.edit = datetime.now()
                his_obj.save()
            else:
                his_obj = FileHistory()
                his_obj.user = request.user
                his_obj.content_object = fol
                his_obj.save()
            if f.parent and f.parent.private:
                parent = "?mparent="+str(f.parent.id)
            else:
                parent=""
            back_href = '/files/private/'+parent
            return redirect(back_href)
    if request.user.is_superuser: 
        form.fields['parent'].queryset = EFiles.objects.filter(private=True).filter(ftype="folder")
    else:
        form.fields['parent'].queryset = EFiles.objects.filter(private=True).filter(ftype="folder").filter(owner=request.user)
        form.fields['owner'].queryset = User.objects.filter(id=request.user.id)
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
    '''
    print request.POST
    f = EFolder()
    if request.POST.get('id')!='0':
        p=EFolder.objects.get(id=request.POST.get('id'))
    else:
        p=None
    f.name = request.POST.get('title')
    f.owner = request.user
    f.parent=p
    f.private=True
    f.save()
    if f:
        return HttpResponse(1, content_type="application/json")
    else:
        return HttpResponse(0, content_type="application/json")
    '''
def get_xhr_file(request,template_name=''):
    jsons = {}
    r = []
    f = EFolder()
    if request.GET.get('id')!='0':
        print "id"
        print 
        w = EFolder.objects.filter(parent__id=int(request.GET.get('id')))
    else:
        w = EFolder.objects.all()
    for i in w:
        jsons={}
        jsons['attr']={}
        jsons['attr']={"id":"node_"+str(i.id)}
        jsons['data']=i.name
        jsons['state']="closed"
        if i.is_leaf_node():
            jsons['children']=[]
        r.append(jsons)

    return HttpResponse(simplejson.dumps(r), content_type="application/json")
def get_xhr_private_file(request,template_name=''):
    jsons = {}
    r = []
    f = EFiles()
    if request.GET.get('id')!='0':
        w = EFiles.objects.filter(parent__id=int(request.GET.get('id'))).filter(owner=request.user)
    else:
        w = EFiles.objects.filter(owner=request.user).filter(parent__isnull=True).all()
    for i in w:
        jsons={}
        jsons['attr']={}
        jsons['attr']={"id":"node_"+str(i.id)}
        jsons['data']=i.name
        jsons['state']="closed"
        if i.is_leaf_node():
            jsons['children']=[]
        r.append(jsons)

    return HttpResponse(simplejson.dumps(r), content_type="application/json")
@myuser_login_required
def add_public_file(request,template_name=''):
    title = "Add public directory"
    
    activepu = 'lactive'
    breadcrumb = []
    breadcrumb.append({'name':'Public files','url':'/files/public/'})
    breadcrumb.append({'name':'Add public directory','url':request.get_full_path()})
    users = User.objects.filter(myprofile__company__main=True)
    groups = Group.objects.filter(company__main=True)
    exusers = User.objects.filter(myprofile__company__main=False)
    rxgroups = Group.objects.filter(user__myprofile__company__main=False).distinct()
    if int(request.GET.get('mparent',0))<1:
        parent = None
    else:
        parent = EFiles.objects.get(id=request.GET.get('mparent',None))
        urr = UsrRightsFile.objects.filter(file=parent,user__myprofile__company__main=True)
        grr = GrRightsFile.objects.filter(file=parent,group__company__main=True)
        exurr = UsrRightsFile.objects.filter(file=parent,user__myprofile__company__main=False)
        exgrr = GrRightsFile.objects.filter(file=parent,group__company__main=False)
    if int(request.GET.get('mparent',0))<1:
        parent = None
    else:
        parent = EFiles.objects.get(id=request.GET.get('mparent',None))
    if parent:
        if parent.have_rights(request.user,['m','s']):
            pass
        else:
            login_url='/error_perm/'
            return redirect(login_url)
    else:
        if request.user.is_superuser:
            pass
        else:
            login_url='/error_perm/'
            return redirect(login_url)
    if parent:
        create_rights = parent.have_rights(request.user,['s'])
    if request.user.is_superuser:
        create_rights = 1
    mback = parent
    form = EFolderForm(initial={'owner': request.user,"parent":parent})
    ug = Group.objects.all()
    if request.method == 'POST':
        form = EFolderForm(request.POST,initial={'owner': request.user,"parent":parent}) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            f = form.save(commit=False)
            f.private=False
            f.ftype='folder'
            f.save()
            if f.ftype=="file":
                f.fsize=f.file.size
                f.save()
            HistoryFile.objects.create(file=f, user=request.user,atype='add')
            his_obj = FileHistory.objects.filter(content_object=f)
            if his_obj:
                his_obj = his_obj[0]
                his_obj.edit = datetime.now()
                his_obj.save()
            else:
                his_obj = FileHistory()
                his_obj.user = request.user
                his_obj.content_object = f
                his_obj.save()
            for i in request.POST:
                u=0
                if request.user.myprofile.company.main:
                    if "rght_group_" in i:
                        nr = i.split("_")[2]
                        tg = Group.objects.get(id=nr)
                        ncr = GrRightsFile()
                        ncr.file=f
                        ncr.group = tg
                        ncr.rtype = request.POST.get(i)
                        ncr.save()
                        u=u+1
                    if "rght_user_" in i:
                        nr = i.split("_")[2]
                        tu = User.objects.get(id=nr)
                        ncr = UsrRightsFile()
                        ncr.file=f
                        ncr.user = tu
                        ncr.rtype = request.POST.get(i)
                        ncr.save()
                        u=u+1
            if u==0:
                urr = UsrRightsFile.objects.filter(file=f.parent)
                grr = GrRightsFile.objects.filter(file=f.parent)
                for i in urr:
                    ncr = UsrRightsFile()
                    ncr.user = i.user
                    ncr.file=f
                    ncr.rtype = i.rtype
                    ncr.save()
                for i in grr:
                    ncr = GrRightsFile()
                    ncr.group = i.group
                    ncr.file=f
                    ncr.rtype = i.rtype
                    ncr.save()
            if f.parent and not f.parent.private:
                parent = "?mparent="+str(f.parent.id)
            else:
                parent=""
            back_href = '/files/public/'+parent
            return redirect(back_href)
    if request.user.is_superuser: 
        form.fields['parent'].queryset = EFiles.objects.filter(private=False).filter(ftype="folder")
    else:
        form.fields['parent'].queryset = EFiles.objects.filter(private=False).filter(ftype="folder").filter(Q(grrightsfile__group__in=request.user.groups.all())&Q(grrightsfile__rtype__in=['m','s'])|Q(usrrightsfile__user=request.user)&Q(usrrightsfile__rtype__in=['m','s']))
        form.fields['owner'].queryset = User.objects.filter(id=request.user.id)
        form.fields['parent'].empty_label = None
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
@myuser_login_required
def public_file(request,template_name=''):
    ret_mess = []
    
    if int(request.GET.get('mparent',0))<1:
        
        nodes = EFiles.objects.filter(parent__id=int(request.GET.get('mparent',0)))
    else:
        can_add = EFiles.objects.get(id=int(request.GET.get('mparent',0))).have_rights(request.user,['m','s'])
        can_up = EFiles.objects.get(id=int(request.GET.get('mparent',0))).have_rights(request.user,['w','m','s'])
        can_token = EFiles.objects.get(id=int(request.GET.get('mparent',0))).have_rights(request.user,['s'])
    title = "Public files"
    
    activepu = 'lactive'
    breadcrumb = []
    breadcrumb.append({'name':'Public files','url':'/files/private/'})
    ret_mess = []
    apublic=1
    if request.GET.get('mparent',0):
        mback = EFiles.objects.get(id=request.GET.get('mparent',0))
    if request.GET.get('del',None):
        
        mobj = EFiles.objects.filter(id=request.GET.get('del',None))
        if mobj:
            mobj = mobj[0]
            lback = mobj.parent
            if mobj.have_rights(request.user,['m','s']):
                if mobj:
                    mobj.delete()
                else:
                    tmpm = {}
                if lback:
                    back = '/files/public/?mparent='+str(lback.id)
                else:
                    back = '/files/public/'
                return redirect(back)
                
                
    table = {}
    table['head'] = []
    table['head'] = ('name','owner','size','created','edit','option',)
    table['option'] = ['upload','edit','del_comf']
    table['class'] = {'share':'btn btn-default','upload':'btn btn-default','open_p':'btn btn-default','edit':'btn btn-default','del_comf':'btn btn-default'}
    table['sort'] = ['"sClass": "center", "bSortable": false','"sClass": "center", "bSortable": false','"sClass": "center"','"sClass": "center", "bSortable": false','"sClass": "center", "bSortable": false']
    table['option_icon'] = {'share':'<span class="icon16 icomoon-icon-share-2"></span>','upload':'<span class="icon16 icomoon-icon-file-upload"></span>','open_p':'<span class="icon16 icomoon-icon-folder-open"></span>','edit':'<span class="icon16 icomoon-icon-pencil-2"></span>','del_comf':'<span class="icon16 icomoon-icon-remove-5"></span>'}
    if int(request.GET.get('mparent',0))<1:
        pass
    else:
        lback = EFiles.objects.get(id=request.GET.get('mparent',0)).parent
        if lback:
            back = '/files/public/?mparent='+str(lback.id)
        else:
            back = '/files/public/'
        
    tmi = 0
    sort_name = ""
    
    if request.is_ajax():
        kwargs = {'private':False}
        if int(request.GET.get('mparent',0))<1:
            #fparent = EFiles.objects.get(id=request.GET.get('mparent',0))
            
            print "Null"
            #kwargs['parent__isnull'] = True
        else:
           
            print request.GET.get('mparent',0)
            kwargs['parent__id'] = request.GET.get('mparent',0)
        
            
        a = table_builder(table, EFiles,request,**kwargs)
        return HttpResponse(a, content_type="application/json")
    else:
        return render_to_response(template_name,locals(), context_instance=RequestContext(request))
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
@myuser_login_required
def view_file(request,nr,template_name=''):
    fol = EFiles.objects.get(id=nr)
    zip_f = []
    zip=0
    img = 0
    if fol.private:
        activepr = 'lactive'
    else:
        activepu = 'lactive'
    mback = fol.parent
    if fol.file.name.lower().endswith('.zip'):
        zip = 1
        file = zipfile.ZipFile(fol.file, "r")
        for fileinfo in file.infolist():
            name = unicode(fileinfo.filename, "cp437").encode("utf8")
            zip_f.append(name)
    elif fol.file.name.lower().endswith(('.jpg','.jpeg','.gif','.png',)):
        img = 1
    else:
        zip=0
    if fol.private:
        if fol.owner==request.user:
            pass
        else:
            login_url='/error_perm/'
            return redirect(login_url)
    else:
        if fol.have_rights(request.user,['r','w','m','s']):
            pass
        else:
            login_url='/error_perm/'
            return redirect(login_url)
    if fol.have_rights(request.user,['w','m','s']):
        edit = 1
    if fol.have_rights(request.user,['m','s']):
        delf = 1
    if fol.have_rights(request.user,['s']):
        sh = 1
    title = "File "+fol.name
    if fol.ftype=="file":
        title = title + " " + fol.get_filename() + " " + humanize_bytes(fol.fsize)
    breadcrumb = []
    if fol.private:
        breadcrumb.append({'name':'Private files','url':'/files/private/'})
    else:
        breadcrumb.append({'name':'Public files','url':'/files/public/'})
   
    if request.method == 'POST':
        if request.POST.get('comment',None):
            CommentFile.objects.create(file=fol, user=request.user,comment=request.POST.get('comment',None))
        
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
@myuser_login_required
def private_file(request,template_name=''):
    ret_mess = []
    if request.GET.get('mparent',0):
        mback = EFiles.objects.get(id=request.GET.get('mparent',0))
    if request.user.myprofile.company.main:
        pass
    else:
        login_url='/error_perm/'
        return redirect(login_url)
    if int(request.GET.get('mparent',0))<1:
        nodes = EFiles.objects.filter(parent__id=int(request.GET.get('mparent',0)))
    title = "Private files"
  
    activepr = 'lactive'
    
    breadcrumb = []
    breadcrumb.append({'name':'Private files','url':'/files/private/'})
    if request.GET.get('del',None):
        mobj = EFiles.objects.filter(id=request.GET.get('del',None))
        if request.user.is_superuser:
            mobj = EFiles.objects.filter(id=request.GET.get('del',None))
        else:
            mobj = EFiles.objects.filter(id=request.GET.get('del',None),owner=request.user)
        mobj = mobj[0]
        lback = mobj.parent
        if mobj:
            mobj.delete()
        else:
            tmpm = {}
        if lback:
            back = '/files/private/?mparent='+str(lback.id)
        else:
            back = '/files/private/'
        return redirect(back)
        
    table = {}
    table['head'] = []
    table['head'] = ('name','owner','size','created','edit','option',)
    table['option'] = ['share','edit','del_comf']
    table['class'] = {'share':'btn btn-default','upload':'btn btn-default','open_p':'btn btn-default','edit':'btn btn-default','del_comf':'btn btn-default'}
    table['sort'] = ['"sClass": "center", "bSortable": false','"sClass": "center", "bSortable": false','"sClass": "center"','"sClass": "center", "bSortable": false','"sClass": "center", "bSortable": false']
    table['option_icon'] = {'share':'<span class="icon16 icomoon-icon-share-2"></span>','upload':'<span class="icon16 icomoon-icon-file-upload"></span>','open_p':'<span class="icon16 icomoon-icon-folder-open"></span>','edit':'<span class="icon16 icomoon-icon-pencil-2"></span>','del_comf':'<span class="icon16 icomoon-icon-remove-5"></span>'}
    if int(request.GET.get('mparent',0))<1:
        mparent = None
        pass
    else:
        mparent = int(request.GET.get('mparent',0))
        back = EFiles.objects.get(id=request.GET.get('mparent',0)).parent
        if back:
            
            back = '/files/private/?mparent='+str(back.id)
        else:
            back = '/files/private/'
        
    tmi = 0
    sort_name = ""
    if request.is_ajax():
        kwargs = {'owner':request.user}
        kwargs['private'] = True
        if int(request.GET.get('mparent',0))<1:
            pass
            #kwargs['parent__isnull'] = True
        else:
           
            kwargs['parent__id'] = request.GET.get('mparent',0)
        
            
        a = table_builder(table, EFiles,request,**kwargs)
        return HttpResponse(a, content_type="application/json")
    else:
        return render_to_response(template_name,locals(), context_instance=RequestContext(request))
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
@myuser_login_required
def add_token_access(request,template_name=''):
    title = "Add access token for files"
    breadcrumb = []
    
    activet = 'lactive'
   
    breadcrumb.append({'name':'Public files','url':'/files/public/'})
    breadcrumb.append({'name':title,'url':request.get_full_path()})
    if request.GET.get('parent',0):
        mback = EFiles.objects.get(id=request.GET.get('parent',0))
    form = AccessTokensForm(initial={'user': request.user,'msg':u'Witaj. Po kliknięciu w <link> otrzymasz listę plików do pobrania.'})
    if request.method == 'POST':
        form = AccessTokensForm(request.POST) # A form bound to the POST data
        
        if form.is_valid(): # All validation rules pass
            f = form.save(commit=False)
            f.user=request.user
            f.type = 'd'
            f.token = os.urandom(20).encode('hex')
            f.save()
            for i in request.POST.getlist('access_file'):
                mf =EFiles.objects.get(id=i)
                f.access_file.add(mf)
            f.save()
            
            if request.is_secure():
                scheme = 'https://'
            else:
                scheme = 'http://'
            if request.POST.get('send_email',0):
                msg = f.msg.replace("<link>", scheme + request.get_host()+'/files/token/'+f.token);
                send_mail(settings.EMAIL_TITLE, msg, settings.DEFAULT_FROM_EMAIL,[f.email], fail_silently=False)
            back_href = '/files/access_token/edit/'+str(f.id)
            return redirect(back_href)
    if request.user.is_superuser:
        pot = mback.get_descendants().filter(private=False).filter(ftype="file").filter(parent=mback)
        form.fields['access_file'].queryset = pot
    else:
        k = request.user
        pot = mback.get_descendants().filter(private=False).filter(ftype="file").filter(Q(grrightsfile__group__in=request.user.groups.all())&Q(grrightsfile__rtype__in=['s'])|Q(usrrightsfile__user=request.user)&Q(usrrightsfile__rtype__in=['s']))
        #form.fields['access_file'].queryset = EFiles.objects.filter(private=False).filter(ftype="file").filter(Q(grrightsfile__group__in=request.user.groups.all())&Q(grrightsfile__rtype__in=['s'])|Q(usrrightsfile__user=request.user)&Q(usrrightsfile__rtype__in=['s'])).filter(parent=mback)
        form.fields['access_file'].queryset = pot
        #form.fields['owner'].queryset = User.objects.filter(id=request.user.id)
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
@myuser_login_required
def add_token_upload(request,template_name=''):
    title = "Add upload token for files"
    breadcrumb = []
    activet = 'lactive'
    breadcrumb.append({'name':'Public files','url':'/files/public/'})
    breadcrumb.append({'name':title,'url':request.get_full_path()})
    
    mparent = int(request.GET.get('parent'))
    parent = EFiles.objects.get(id=request.GET.get('parent'))
    
    form = UploadTokensForm(initial={'user': request.user,'msg':u'Witaj. Po kliknięciu w <link> otrzymasz możliwość wysłania plików.',"access_file":parent})
    one = 1
    if request.method == 'POST':
        form = UploadTokensForm(request.POST) # A form bound to the POST data
        
        if form.is_valid(): # All validation rules pass
            f = form.save(commit=False)
            f.user=request.user
            f.type = 'u'
            f.token = os.urandom(20).encode('hex')
            f.save()
            for i in request.POST.getlist('access_file'):
                mf =EFiles.objects.get(id=i)
                f.access_file.add(mf)
            f.save()
            
            if request.is_secure():
                scheme = 'https://'
            else:
                scheme = 'http://'
            if request.POST.get('send_email',0):
                msg = f.msg.replace("<link>", scheme + request.get_host()+'/files/token_up/'+f.token);
                send_mail(settings.EMAIL_TITLE, msg, settings.DEFAULT_FROM_EMAIL,[f.email], fail_silently=False)
            back_href = '/files/access_token/edit/'+str(f.id)
            return redirect(back_href)
    if request.user.is_superuser: 
        form.fields['access_file'].queryset = EFiles.objects.filter(private=False).filter(ftype="folder")
        af = EFiles.objects.filter(private=False).filter(ftype="folder")
    else:
        k = request.user
        
        form.fields['access_file'].queryset = EFiles.objects.filter(private=False).filter(ftype="folder").filter(Q(grrightsfile__group__in=request.user.groups.all())&Q(grrightsfile__rtype__in=['s'])|Q(usrrightsfile__user=request.user)&Q(usrrightsfile__rtype__in=['s']))
        af = EFiles.objects.filter(private=False).filter(ftype="folder").filter(Q(grrightsfile__group__in=request.user.groups.all())&Q(grrightsfile__rtype__in=['s'])|Q(usrrightsfile__user=request.user)&Q(usrrightsfile__rtype__in=['s']))
        #form.fields['owner'].queryset = User.objects.filter(id=request.user.id)
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
def edit_token_upload(request,nr,template_name=''):
    title = "Add upload token for files"
    breadcrumb = []
    activet = 'lactive'
    breadcrumb.append({'name':'Public files','url':'/files/public/'})
    breadcrumb.append({'name':"Token list",'url':'/files/access_token/'})
    if request.user.is_superuser: 
        fol = AccessTokens.objects.get(id=nr)
    else:
        fol = AccessTokens.objects.get(id=nr,user=request.user)
    if request.is_secure():
        scheme = 'https://'
    else:
        scheme = 'http://'
    link = scheme + request.get_host()+'/files/token_up/'+fol.token
    
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
def edit_token_access(request,nr,template_name=''):
    title = "Add download token for files"
    breadcrumb = []
    breadcrumb.append({'name':'Public files','url':'/files/public/'})
    breadcrumb.append({'name':"Token list",'url':'/files/access_token/'})
    if request.user.is_superuser: 
        fol = AccessTokens.objects.get(id=nr)
    else:
        fol = AccessTokens.objects.get(id=nr,user=request.user)
    if request.is_secure():
        scheme = 'https://'
    else:
        scheme = 'http://'
    if fol.type == "d":
        link = scheme + request.get_host()+'/files/token/'+fol.token
    else:
        link = scheme + request.get_host()+'/files/token_up/'+fol.token
    
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
@myuser_login_required
def add_token_access_list(request,template_name=''):
    title = "Token list"
    token = 1
    activet = 'lactive'
    breadcrumb = []
    hide_head = 1
    acsh = 1
    breadcrumb.append({'name':'Public files','url':'/files/public/'})
    breadcrumb.append({'name':title,'url':request.get_full_path()})
    if request.GET.get('del',None):
        if request.user.has_perm('auth.delete_user'):
            obj = AccessTokens.objects.filter(id=request.GET.get('del',None))
            if obj:
                obj = obj[0]
                obj.delete()
              
        else:
            tmpm = {}
            
    table = {}
    table['head'] = []
    table['head'] = ('id','email','user','type','date_from','date_to','option',)
    table['option'] = ['edit','del_comf']
    table['class'] = {'edit':'btn btn-default','del_comf':'btn btn-default'}
    table['sort'] = ['"sClass": "center", "bSortable": false','"sClass": "center", "bSortable": false','"sClass": "center"','"sClass": "center", "bSortable": false','"sClass": "center", "bSortable": false']
    table['option_icon'] = {'edit':'<span class="icon16 icomoon-icon-pencil-2"></span>','del_comf':'<span class="icon16 icomoon-icon-remove-5"></span>'}
    tmi = 0
    sort_name = ""
    if request.is_ajax():
        a = table_builder(table, AccessTokens,request)
        return HttpResponse(a, content_type="application/json")
    else:
        return render_to_response(template_name,locals(), context_instance=RequestContext(request))

def token_upload_list(request,nr,template_name=''):
    fol = AccessTokens.objects.filter(token=nr,date_to__gt=datetime.now(),date_from__lt=datetime.now())
    hide_head = 1
    activet = 'lactive'
    if fol:
        fol = fol[0]
    else:
        login_url='/error_token/'
        return redirect(login_url)
    title = ""
    inv_info = 1
    breadcrumb = []
    breadcrumb.append({'name':'Public files','url':'/files/public/'})
    breadcrumb.append({'name':"Token list",'url':'/files/access_token/'})

    if request.method == 'POST':
        for filename, file in request.FILES.iteritems():
            print  filename
            if 'file_' in filename:
                f = EFiles()
                f.name = request.POST.get('name_'+filename.split('_')[1])
                f.private=False
                f.ftype='file'
                f.owner = fol.user
                f.parent = fol.access_file.all()[0]
                f.file=request.FILES[filename]
                f.save()
                HistoryFile.objects.create(file=f, user=fol.user,atype='add_token')
                
                his_obj = FileHistory.objects.filter(content_object=f)
                if his_obj:
                    his_obj = his_obj[0]
                    his_obj.edit = datetime.now()
                    his_obj.save()
                else:
                    his_obj = FileHistory()
                    his_obj.user = fol.user
                    his_obj.content_object = f
                    his_obj.save()
                urr = UsrRightsFile.objects.filter(file=f.parent)
                grr = GrRightsFile.objects.filter(file=f.parent)
                for i in urr:
                    ncr = UsrRightsFile()
                    ncr.user = i.user
                    ncr.file=f
                    ncr.rtype = i.rtype
                    ncr.save()
                for i in grr:
                    ncr = GrRightsFile()
                    ncr.group = i.group
                    ncr.file=f
                    ncr.rtype = i.rtype
                    ncr.save()
        
        login_url='/upload_ok/'
        return redirect(login_url)
        
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))
def token_download_list(request,nr,template_name=''):
    fol = AccessTokens.objects.filter(token=nr,date_to__gt=datetime.now(),date_from__lt=datetime.now())
    title = ""
    inv_info = 1
    if fol:
        fol = fol[0]
    else:
        login_url='/error_perm/'
        return redirect(login_url)
    
    breadcrumb = []

    if request.method == 'POST':
        if request.POST.get('comment',None):
            CommentFile.objects.create(file=fol, user=request.user,comment=request.POST.get('comment',None))
        
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))

def download_token(request,nr,token,template_name=''):
    fol = EFiles.objects.get(id=nr)
    inv_info = 1
    activet = 'lactive'
    if AccessTokens.objects.filter(access_file__in=[fol],token=token,date_to__gt=datetime.now(),date_from__lt=datetime.now()).all():
        pass
    else:
        login_url='/error_token/'
        return redirect(login_url)
    t = AccessTokens.objects.get(access_file__in=[fol],token=token,date_to__gt=datetime.now(),date_from__lt=datetime.now())
    form = EFolderForm(instance=fol)
    filename = fol.file.name.split('/')[-1]
    response = HttpResponse(fol.file, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    HistoryFile.objects.create(file=fol, user=t.user, atype='download')
    return response
def callback(line):
    pattern = r'.* ([A-Z|a-z].. .. .....) (.*)'
    ret = []
    found = re.match(pattern, line)
    if (found is not None):
        ret = found.groups()
    return ret
def is_file(path,ftp):
    #ftp = FTP("e-workflow.pl")
    #ftp.login("test@e-workflow.pl", "Test1234")
    ftp.cwd('/')
    try:
        ftp.cwd(path)
        
        return 0
    except error_perm:
       
        return 1
@myuser_login_required    
def ftp_list(request,template_name=''):
    title = "FTP"
    breadcrumb = []
    
    breadcrumb.append({'name':'Public files','url':'/files/public/'})
    breadcrumb.append({'name':title,'url':request.get_full_path()})
    ftp = FTP("e-workflow.pl")
    ftp.login("test@e-workflow.pl", "Test1234")
    filenames = []
    ret = []
    parent = EFiles.objects.get(id=request.GET.get('parent'))
    if parent.private:
        activepr = 'lactive'
    else:
        activepu = 'lactive'
    form = EFilesFtpForm(initial={"parent":parent})
    print ftp.nlst('')
    try:
        if request.GET.get('uftp',0):
            
            ftp.cwd(request.GET.get('uftp',0))
        
        ftp.retrlines('LIST', lambda line: filenames.append(line.split()[-1]))
    except error_perm:
        pass
    del filenames[0]
    for i in filenames:
        if request.GET.get('uftp',0):
            ret.append({'name':i,'type':is_file(request.GET.get('uftp',0)+"/"+i,ftp)})
        else:
            ret.append({'name':i,'type':is_file(i,ftp)})
    if request.user.is_superuser: 
        form.fields['parent'].queryset = EFiles.objects.filter(private=False).filter(ftype="folder")
    else:
        form.fields['parent'].queryset = EFiles.objects.filter(private=False).filter(ftype="folder").filter(Q(grrightsfile__group__in=request.user.groups.all())&Q(grrightsfile__rtype__in=['w','m','s'])|Q(usrrightsfile__user=request.user)&Q(usrrightsfile__rtype__in=['w','m','s']))
        form.fields['parent'].empty_label = None
    if request.method == 'POST':
        path = settings.MEDIA_ROOT+"mfiles/"
        print "wysylam"
        print request.POST
        for i in request.POST.getlist('ftp_file'):
            print i
            ftp.cwd("/")
            filename = i
            ftp.cwd(request.GET.get('uftp',0))
            local_filename = os.path.join(path, filename)
            lf = open(local_filename, "wb")
            ftp.retrbinary("RETR " + filename ,lf.write, 8*1024)
            lf.close()
            f = EFiles()
            f.name = filename
            f.private=False
            f.ftype='file'
            f.owner = request.user
            parent = EFiles.objects.get(id=request.POST.get('parent'))
            f.parent = parent
            file = open(path+filename)
            djangofile = File(file)
            
            
            f.file=djangofile
            f.save()
            HistoryFile.objects.create(file=f, user=request.user,atype='add')
            file.close()  
            his_obj = FileHistory.objects.filter(content_object=f)
            if his_obj:
                his_obj = his_obj[0]
                his_obj.edit = datetime.now()
                his_obj.save()
            else:
                his_obj = FileHistory()
                his_obj.user = request.user
                his_obj.content_object = f
                his_obj.save()
                urr = UsrRightsFile.objects.filter(file=f.parent)
                grr = GrRightsFile.objects.filter(file=f.parent)
                for i in urr:
                    ncr = UsrRightsFile()
                    ncr.user = i.user
                    ncr.file=f
                    ncr.rtype = i.rtype
                    ncr.save()
                for i in grr:
                    ncr = GrRightsFile()
                    ncr.group = i.group
                    ncr.file=f
                    ncr.rtype = i.rtype
                    ncr.save()
        done =1
            
            
    ftp.quit()
    return render_to_response(template_name,locals(), context_instance=RequestContext(request))