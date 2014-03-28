#encoding:UTF-8
from django.shortcuts import render
from django.template import *
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME
from datetime import datetime
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.http import HttpResponseRedirect, QueryDict
from django.template.response import TemplateResponse
from company.forms import UserGroupForms, CompanyForms, UserForms, MyProfileForms, UserEditForms,PasswdForms,EmployerForm, MyProfileUserForms, MyProfileEditForms
from company.models import Company, MyProfile, CompanyInfo, ObjHistory, UsrHistory, GrHistory, CpHistory
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import permission_required
from ebook.views import table_builder
from ebook.decorators import myuser_login_required
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import check_for_language, to_locale, get_language
# Create your views here.
user_perm_models = [

    {'app':'auth','model':'user', },
    {'app':'auth','model':'group', },
    {'app':'company','model':'company', },
    
]
@myuser_login_required
def mprofile(request,template_name=''):
    title = "My profile"
    breadcrumb = []
    breadcrumb.append({'name':title,'url':'/company/mprofile/'})
    us = request.user
    title2 = us.username
    form = MyProfileUserForms(instance=us)
    mpf = MyProfileEditForms(instance=us.myprofile) 
    if request.method == 'POST':
        
        form = MyProfileUserForms(request.POST,instance=us)
        mpf = MyProfileEditForms(request.POST,instance=us.myprofile) 
        if form.is_valid() and mpf.is_valid():
            
            usern = form.save(commit=False)
            u=usern.save()
            if request.POST.get('password1',0):
                usern.set_password(request.POST.get('password1'))
                usern.save()
            #u=usern.save_m2m()
            mpf=mpf.save(commit=False)
            mpf.save()
            ret_mess = []
            tmpm = {}
        lang_code = request.POST.get('lang', None)
        if lang_code and check_for_language(lang_code):
            if hasattr(request, 'session'):
                    
                request.session['django_language'] = lang_code
                
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        
        back_href = request.get_full_path()
        return redirect(back_href)
        mpf = MyProfileEditForms(request.POST)
    mycompany = us.myprofile.company.name
    #form.fields['permissions'].label_from_instance = lambda obj: "%s %s" % (InfoTrans.objects.get(kod=obj.content_type.app_label,cotyp__kod='admin_menu_name').name, split_name_lang(obj.codename),)
    return render(request,template_name,locals())
@myuser_login_required
@permission_required('auth.add_user', login_url='/error_perm/')
def user_add(request,template_name=''):
    title = "Add user"
    activeu = 'lactive'
    breadcrumb = []
    breadcrumb.append({'name':"User add",'url':'/company/user/add/'})
    hist = UsrHistory()
    form = UserForms()
    def_comp = []
    def_comp = Company.objects.filter(cdefault=True)
    if def_comp:
        def_comp = def_comp[0]
    mpfn = MyProfileForms(initial={'lang': 'pl','company': def_comp}) 
    if request.method == 'POST':
        form = UserForms(request.POST)
        mpfn = MyProfileForms(request.POST) 
        if form.is_valid() and mpfn.is_valid():
            
            usern = form.save(commit=False)
      
            usern.set_password(request.POST.get('password1'))
            usern.save()
            
            for i in request.POST.getlist('groups'):
                g =Group.objects.get(id=i)
                usern.groups.add(g)
            
                

            for i in request.POST.getlist('user_permissions'):
                g =Permission.objects.get(id=i)
                usern.user_permissions.add(g)
            usern.save()
        
            
            mpfn=mpfn.save(commit=False)
            mpfn.user=usern
            
            mpfn.save()
            if usern.groups.all():
                pass
            else:
                for y in usern.myprofile.company.u_group.all():
                    usern.groups.add(y)
                    usern.save()
            hist.user = mpfn.user
            hist.content_object = mpfn.user
            hist.save()
            ret_mess = []
            tmpm = {}
            back_href = reverse('user_list')
            return redirect(back_href)
        mpfn = MyProfileForms(request.POST)
    perm = []
    for i in user_perm_models:
        perm.append(ContentType.objects.get(app_label=i['app'], model=i['model']))
    form.fields['user_permissions'].queryset = Permission.objects.filter(content_type__in=perm)
    mpfn.fields['company'].empty_label = None
    mpfn.fields['lang'].empty_label = None
    #form.fields['permissions'].label_from_instance = lambda obj: "%s %s" % (InfoTrans.objects.get(kod=obj.content_type.app_label,cotyp__kod='admin_menu_name').name, split_name_lang(obj.codename),)
    return render(request,template_name,locals())
@myuser_login_required
@permission_required('auth.change_user', login_url='/error_perm/')
def user_edit(request,nr,template_name=''):
    title = "User edit"
    breadcrumb = []
    activeu = 'lactive'
    breadcrumb.append({'name':"User list",'url':'/company/user/'})
    breadcrumb.append({'name':title,'url':request.get_full_path()})
    
    u = get_object_or_404(User,id=nr)
    title2 = u.username
    his_obj = UsrHistory.objects.filter(content_object=u)
    if his_obj:
        his_obj = his_obj[0]
    else:
        his_obj = UsrHistory()
        his_obj.user = request.user
        his_obj.content_object = u
        his_obj.save()
    form = UserEditForms(instance=u)
    mpfn = MyProfileForms(instance=u.myprofile) 
    if request.method == 'POST':
        form = UserEditForms(request.POST,instance=u)
        mpfn = MyProfileForms(request.POST,instance=u.myprofile) 
        if form.is_valid() and mpfn.is_valid():
            
            usern = form.save(commit=False)
            usern.groups.clear()
            for i in request.POST.getlist('groups'):
                g =Group.objects.get(id=i)
                usern.groups.add(g)
            usern.user_permissions.clear()
            for i in request.POST.getlist('user_permissions'):
                g =Permission.objects.get(id=i)
                usern.user_permissions.add(g)
            u=usern.save()
            #u=usern.save_m2m()
            mpfn=mpfn.save(commit=False)
            mpfn.save()
            ret_mess = []
            tmpm = {}
            his_obj.edit = datetime.now()
            his_obj.save()
            back_href = reverse('user_list')
            return redirect(back_href)
        mpfn = MyProfileForms(request.POST)
    perm = []
    for i in user_perm_models:
        perm.append(ContentType.objects.get(app_label=i['app'], model=i['model']))
    form.fields['user_permissions'].queryset = Permission.objects.filter(content_type__in=perm)
    mpfn.fields['company'].empty_label = None
    mpfn.fields['lang'].empty_label = None
    #form.fields['permissions'].label_from_instance = lambda obj: "%s %s" % (InfoTrans.objects.get(kod=obj.content_type.app_label,cotyp__kod='admin_menu_name').name, split_name_lang(obj.codename),)
    return render(request,template_name,locals())
@myuser_login_required
@permission_required('company.add_company', login_url='/error_perm/')
def company_add(request,template_name=''):
    ret_mess = []
    title = "Add company"
    activec = 'lactive'
    breadcrumb = []
    breadcrumb.append({'name':title,'url':request.get_full_path()})
    form = CompanyForms()
    if request.method == 'POST':
        form = CompanyForms(request.POST)
        if form.is_valid():
            usern = form.save()
           
            hist = CpHistory()
            hist.user = request.user
            hist.content_object = usern
            hist.save()
            ret_mess = []
            tmpm = {}
            back_href = '/company/'
            return redirect(back_href)
    #form.fields['permissions'].label_from_instance = lambda obj: "%s %s" % (InfoTrans.objects.get(kod=obj.content_type.app_label,cotyp__kod='admin_menu_name').name, split_name_lang(obj.codename),)
    return render(request,template_name,locals())
@myuser_login_required
@permission_required('auth.change_group', login_url='/error_perm/')
def group_list(request,template_name=''):
    ret_mess = []
    activeg = 'lactive'
    title = "Groups list"
    if request.user.has_perm('auth.add_group'):
        add_url = '/company/group/add/'
        add_name= 'Add group'
    breadcrumb = []
    breadcrumb.append({'name':title,'url':'/company/group/'})
    if request.GET.get('del',None):
        if request.user.has_perm('auth.delete_group'):
            obj = Group.objects.filter(id=request.GET.get('del',None))
            if obj:
                obj = obj[0]
                
                obj.delete()
                tmpm = {}
                tmpm["typ"] = u"st-success"
                tmpm["mess"] = u"Elementy usunięte."
                ret_mess.append(tmpm)
        else:
            tmpm = {}
            tmpm["typ"] = u"st-error"
            tmpm["mess"] = u"Nie masz prawa."
            ret_mess.append(tmpm)
    table = {}
    table['head'] = []
    table['head'] = ('id','name','author','created','edit','option',)
    table['option'] = ['edit','del_comf']
    table['class'] = {'edit':'btn btn-default','del_comf':'btn btn-default'}
    table['sort'] = ['"sClass": "center", "bSortable": false','"sClass": "center", "bSortable": false','"sClass": "center"','"sClass": "center", "bSortable": false','"sClass": "center", "bSortable": false']
    table['option_icon'] = {'edit':'<span class="icon16 icomoon-icon-pencil-2"></span>','del_comf':'<span class="icon16 icomoon-icon-remove-5"></span>'}
    tmi = 0
    sort_name = ""
    if request.is_ajax():
        a = table_builder(table, Group,request)
        return HttpResponse(a, content_type="application/json")
    else:
        return render_to_response(template_name,locals(), context_instance=RequestContext(request))
@myuser_login_required
@permission_required('auth.change_user', login_url='/error_perm/')
def user_list(request,template_name=''):
    ret_mess = []
    activeu = 'lactive'
    title = "User list"
    breadcrumb = []
    if request.user.has_perm('auth.add_user'):
        add_url = '/company/user/add/'
        add_name= 'Add user'
    breadcrumb.append({'name':title,'url':'/company/user/'})
    if request.GET.get('del',None):
        if request.user.has_perm('auth.delete_user'):
            obj = User.objects.get(id=request.GET.get('del',None))
            if obj:
                obj.is_active = False
                obj.save()
        else:
            tmpm = {}
            tmpm["typ"] = u"st-error"
            tmpm["mess"] = u"Nie masz prawa."
            ret_mess.append(tmpm)
    table = {}
    table['head'] = []
    table['head'] = ('id','email','username','full_name','author','created','edit','option',)
    table['option'] = ['edit','del_comf']
    table['class'] = {'edit':'btn btn-default','del_comf':'btn btn-default'}
    table['sort'] = ['"sClass": "center", "bSortable": false','"sClass": "center", "bSortable": false','"sClass": "center"','"sClass": "center", "bSortable": false','"sClass": "center", "bSortable": false']
    table['option_icon'] = {'edit':'<span class="icon16 icomoon-icon-pencil-2"></span>','del_comf':'<span class="icon16 icomoon-icon-remove-5"></span>'}
    tmi = 0
    sort_name = ""
    if request.is_ajax():
        a = table_builder(table, User,request)
        return HttpResponse(a, content_type="application/json")
    else:
        return render_to_response(template_name,locals(), context_instance=RequestContext(request))
@myuser_login_required
@permission_required('company.change_company', login_url='/error_perm/')
def company_list(request,template_name=''):
    ret_mess = []
    activec = 'lactive'
    title = "Company list"
    breadcrumb = []
    breadcrumb.append({'name':title,'url':'/company/'})
    if request.user.has_perm('company.add_company'):
        add_url = '/company/add/'
        add_name= 'Add company'
    if request.GET.get('del',None):
        if request.user.has_perm('auth.delete_user'):
            obj = Company.objects.filter(id=request.GET.get('del',None))
            if MyProfile.objects.filter(company=obj).all():
                f_error = _(u"BŁĄD - firma ma pracowników! Przenieś pracowników do innej firmy.")
            else:
                if obj:
                    obj = obj[0]
                    obj.delete()
                    tmpm = {}
                    tmpm["typ"] = u"st-success"
                    tmpm["mess"] = u"Elementy usunięte."
                    ret_mess.append(tmpm)
        else:
            tmpm = {}
            tmpm["typ"] = u"st-error"
            tmpm["mess"] = u"Nie masz prawa."
            ret_mess.append(tmpm)
    table = {}
    table['head'] = []
    table['head'] = ('id','name','author','created','edit','option',)
    table['option'] = ['edit','del_comf']
    table['class'] = {'edit':'btn btn-default','del_comf':'btn btn-default'}
    table['sort'] = ['"sClass": "center", "bSortable": false','"sClass": "center", "bSortable": false','"sClass": "center"','"sClass": "center", "bSortable": false','"sClass": "center", "bSortable": false']
    table['option_icon'] = {'edit':'<span class="icon16 icomoon-icon-pencil-2"></span>','del_comf':'<span class="icon16 icomoon-icon-remove-5"></span>'}
    tmi = 0
    sort_name = ""
    if request.is_ajax():
        a = table_builder(table, Company,request)
        return HttpResponse(a, content_type="application/json")
    else:
        return render_to_response(template_name,locals(), context_instance=RequestContext(request))
@myuser_login_required
@permission_required('company.change_company', login_url='/error_perm/')
def company_edit(request,nr,template_name=''):
    ret_mess = []
    activec = 'lactive'
    title = "Company edit"
    breadcrumb = []
    breadcrumb.append({'name':"Company list",'url':'/company/'})
    breadcrumb.append({'name':title,'url':request.get_full_path()})
    u = get_object_or_404(Company,id=nr)
    title2 = u.name
    mpf = EmployerForm(initial={'employer': User.objects.filter(id__in=u.myprofile_set.all().values_list('user_id',flat=True)).values_list('id',flat=True)})
    form = CompanyForms(instance=u)
    m_type = ContentType.objects.get_for_model(u)
    his_obj = CpHistory.objects.filter(content_object=u)
    if his_obj:
        print "jest"
        print his_obj
        his_obj = his_obj[0]
    else:
        print "ronior"
        his_obj = CpHistory()
        his_obj.user = request.user
        his_obj.content_object = u
        his_obj.save()
    if request.method == 'POST':
        form = CompanyForms(request.POST,instance=u)
        if form.is_valid():
            if request.POST.getlist('main'):
                    for i in Company.objects.all():
                        i.main = False
                        i.save()
            usern = form.save()
            his_obj.edit = datetime.now()
            his_obj.save()
            for i in request.POST.getlist('employer'):
                
                uc = MyProfile.objects.get(user__id=i)
                uc.company = u
                uc.save()
            back_href = '/company/'
            return redirect(back_href)
                        
            ret_mess = []
            
    return render(request,template_name,locals())
@myuser_login_required
@permission_required('auth.change_add', login_url='/error_perm/')
def group_add(request,template_name=''):
    title = "Add group"
    breadcrumb = []
    activeg = 'lactive'
    breadcrumb.append({'name':title,'url':'/company/add/'})
    form = UserGroupForms()
    if request.method == 'POST':
        form = UserGroupForms(request.POST)
        if form.is_valid():
            usern = form.save()
            hist = GrHistory()
            hist.user = request.user
            hist.content_object = usern
            hist.save()
            grst = GrSetting()
            grst.group = usern
            
            ret_mess = []
            tmpm = {}
            back_href = '/company/group/'
            return redirect(back_href)
            
    perm = []
    for i in user_perm_models:
        perm.append(ContentType.objects.get(app_label=i['app'], model=i['model']))
    form.fields['permissions'].queryset = Permission.objects.filter(content_type__in=perm)
    #form.fields['permissions'].label_from_instance = lambda obj: "%s %s" % (InfoTrans.objects.get(kod=obj.content_type.app_label,cotyp__kod='admin_menu_name').name, split_name_lang(obj.codename),)
    return render(request,template_name,locals())
@myuser_login_required
@permission_required('auth.change_group', login_url='/error_perm/')
def group_edit(request,nr,template_name=''):
    title = "Group edit"
    breadcrumb = []
    activeg = 'lactive'
    breadcrumb.append({'name':'Groups list','url':'/company/group/'})
    breadcrumb.append({'name':title,'url':request.get_full_path()})
    u = get_object_or_404(Group,id=nr)
    title2 = u.name
    m_type = ContentType.objects.get_for_model(u)
    his_obj = GrHistory.objects.filter(content_object=u)
    if his_obj:
        his_obj = his_obj[0]
    else:
        his_obj = GrHistory()
        his_obj.user = request.user
        his_obj.content_object = u
        his_obj.save()
    form = UserGroupForms(instance=u)
    if request.method == 'POST':
        form = UserGroupForms(request.POST,instance=u)
        if form.is_valid():
            usern = form.save()
            his_obj.edit = datetime.now()
            his_obj.save()
            ret_mess = []
            back_href = '/company/group/'
            return redirect(back_href)
            
    perm = []
    for i in user_perm_models:
        perm.append(ContentType.objects.get(app_label=i['app'], model=i['model']))
    #form.fields['permissions'].queryset = Permission.objects.filter(content_type__in=perm)       
    return render(request,template_name,locals())
@myuser_login_required
def pass_edit(request,template_name=''):
    title = "Change password"
    breadcrumb = []
    breadcrumb.append({'name':title,'url':'/company/passwd/'})
    u = request.user
    form = PasswdForms(instance=u)
    if request.method == 'POST':
   
        form = PasswdForms(request.POST,instance=u)
        if form.is_valid():
         
            form.save()
            back_href = reverse('mprofile')
            return redirect(back_href)
            ret_mess = []   
    return render(request,template_name,locals())
