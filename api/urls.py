from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns

from django.contrib.auth.forms import UserCreationForm
from api import views, view_user, view_order, view_vendor, view_consumer, view_address, view_deliveryguy, view_group

from api.view_address import AddressViewSet
from api.view_consumer import ConsumerViewSet
from api.view_order import OrderViewSet

from api.view_deliveryguy import DGViewSet
from api.view_vendor import VendorViewSet

from api.view_group import GroupViewSet
from api.view_usergroup import UserGroupViewSet

from rest_framework.routers import DefaultRouter


urlpatterns = patterns(
    'api.views',
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^auth/', include('djoser.urls')),
    url(r'^request_vendor_account/', views.request_vendor_account,name='Request vendor account'),
    url(r'^register_consumer/', views.register_consumer,name='Consumer Registration'),
    url(r'^dg_signin/', views.dg_signin,name='Deliveryguy SignIn'),
    url(r'^create_vendor_agent/', views.create_vendor_agent,name='Create vendor agent'),
)


router = DefaultRouter()
router.register(r'vendor', VendorViewSet)
router.register(r'deliveryguy', DGViewSet)
router.register(r'consumer', ConsumerViewSet, base_name ='consumer')
router.register(r'address', AddressViewSet)
router.register(r'order', OrderViewSet, base_name ='order')
router.register(r'group', GroupViewSet)
router.register(r'usergroup', UserGroupViewSet)

urlpatterns += router.urls
# urlpatterns = format_suffix_patterns(urlpatterns)

