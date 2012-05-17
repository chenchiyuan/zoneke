from django.conf.urls import patterns, include, url
from profiles.views import weibo_login, weibo_callback, weibo_logout, weibo_history

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'zoneke.views.home', name='home'),
    # url(r'^zoneke/', include('zoneke.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'profile/weibo-login/$', weibo_login, name='weibo_login'),
    url(r'profile/weibo-callback/$', weibo_callback, name='weibo_callback'),
    url(r'profile/weibo-logout/$', weibo_logout, name='weibo_logout'),
    url(r'profile/weibo-history/$', weibo_history, name='weibo_history')
)
