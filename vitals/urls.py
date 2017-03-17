from django.conf.urls import url
from .views import VitalsJSONView

urlpatterns = [
    url(r'^$', VitalsJSONView.as_view(), name='vitals'),
]
