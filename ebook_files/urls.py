from django.conf.urls import patterns, url

urlpatterns = patterns('ebook_files.views',
    (r'^public/$', 'public_file',{'template_name':'file_manager.html'},'public_file'),
    (r'^private/share/(?P<nr>[\d]+)/$', 'share_file',{'template_name':'simple_add.html'},'share_file'),
    (r'^private/$', 'private_file',{'template_name':'file_manager.html'},'private_file'),
    (r'^private/edit/(?P<nr>[\d]+)/$', 'edit_file',{'template_name':'simple_add.html'},'edit_file'),
    (r'^private/upload/(?P<nr>[\d]+)/$', 'upload_file',{'template_name':'simple_add.html'},'upload_file'),
    (r'^public/upload/(?P<nr>[\d]+)/$', 'public_upload_file',{'template_name':'simple_add.html'},'public_upload_file'),
    (r'^private/download/(?P<nr>[\d]+)/$', 'download',{'template_name':'simple_add.html'},'download'),
    (r'^public/download/(?P<nr>[\d]+)/$', 'download_public',{'template_name':'simple_add.html'},'download_public'),
    (r'^add/$', 'add_file',{'template_name':'simple_add.html'},'add_file'),
    (r'^public/add/$', 'add_public_file',{'template_name':'simple_add.html'},'add_public_file'),
    (r'^edit/(?P<nr>[\d]+)/$', 'edit_file',{'template_name':'simple_add.html'},'edit_file'),
    (r'^public/edit/(?P<nr>[\d]+)/$', 'edit_file_public',{'template_name':'simple_add.html'},'edit_file_public'),
    (r'^get_xhr_file/$', 'get_xhr_file',{'template_name':'invoice/file_add.html'},'get_xhr_file'),
    (r'^get_xhr_private_file/$', 'get_xhr_private_file',{'template_name':'invoice/file_add.html'},'get_xhr_private_file'),
    (r'^view/(?P<nr>[\d]+)/$', 'view_file',{'template_name':'simple_view_file.html'},'view_file'),
    (r'^access_token/add/$', 'add_token_access',{'template_name':'simple_add.html'},'add_token_access'),
    (r'^upload_token/add/$', 'add_token_upload',{'template_name':'simple_add.html'},'add_token_upload'),
    (r'^access_token/edit/(?P<nr>[\d]+)/$', 'edit_token_access',{'template_name':'token_edit.html'},'edit_token_access'),
    (r'^upload_token/edit/(?P<nr>[\d]+)/$', 'edit_token_upload',{'template_name':'token_edit.html'},'edit_token_upload'),
    (r'^access_token/$', 'add_token_access_list',{'template_name':'simple_list.html'},'add_token_access_list'),
    (r'^token_up/(?P<nr>[\w\d]+)/$', 'token_upload_list',{'template_name':'token_up.html'},'token_upload_list'),
    (r'^token/(?P<nr>[\w\d]+)/$', 'token_download_list',{'template_name':'token_view.html'},'token_download_list'),
    (r'^token/download/(?P<nr>[\d]+)/(?P<token>[\w\d]+)/$', 'download_token',{'template_name':'simple_add.html'},'download_token'),
    (r'^ftp/$', 'ftp_list',{'template_name':'ftp_list.html'},'ftp_list'),
    
)