from django.conf.urls import patterns, url
from landingpage import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = patterns('',

    url(r'^$', views.index, name='index'),
    url(r'^make_event/$', views.make_event, name='make_event'),
    url(r'^view_availability/$', views.view_availability, name='view_availability'),
	url(r'^get_availability/$', views.get_availability, name='get_availability'),
)