from django.conf.urls import patterns, url

urlpatterns = patterns('company.views',
    (r'^group/$', 'group_list',{'template_name':'simple_list.html'},'group_list'),
    (r'^group/add/$', 'group_add',{'template_name':'simple_add.html'},'group_add'),
    (r'^group/edit/(?P<nr>[\d]+)/$', 'group_edit',{'template_name':'simple_add.html'},'group_edit'),
    (r'^$', 'company_list',{'template_name':'simple_list.html'},'company_list'),
    (r'^add/$', 'company_add',{'template_name':'simple_add.html'},'company_add'),
    (r'^edit/(?P<nr>[\d]+)/$', 'company_edit',{'template_name':'simple_add.html'},'company_edit'),
    (r'^user/add/$', 'user_add',{'template_name':'simple_add.html'},'user_add'),
    (r'^user/$', 'user_list',{'template_name':'simple_list.html'},'user_list'),
    (r'^mprofile/$', 'mprofile',{'template_name':'simple_add.html'},'mprofile'),
    (r'^user/edit/(?P<nr>[\d]+)/$', 'user_edit',{'template_name':'simple_add.html'},'user_edit'),
    (r'^passwd/$', 'pass_edit',{'template_name':'simple_add.html'},'pass_edit'),
    
    
)