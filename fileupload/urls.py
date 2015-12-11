from django.conf.urls import *
from fileupload.views import PictureCreateView, PictureDeleteView, MultiUploderView


urlpatterns = patterns('',
    (r'^new/$', PictureCreateView.as_view(), {}, 'upload-new'),
    (r'^new/add/$', MultiUploderView.as_view(), {}, 'upload-add'),
    (r'^delete/(?P<pk>\d+)$', PictureDeleteView.as_view(), {}, 'upload-delete'),
)

