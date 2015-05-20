from django.conf.urls import patterns, url, include
from django.contrib.auth.forms import UserCreationForm
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

from api import views, view_user, view_order, view_vendor, view_consumer, view_area, view_address, view_deliveryguy, view_group, view_vendoragent

from api.view_address import AddressViewSet
from api.view_area import AreaViewSet
from api.view_consumer import ConsumerViewSet
from api.view_order import OrderViewSet
from api.view_deliveryguy import DGViewSet
from api.view_vendor import VendorViewSet
from api.view_vendoragent import VendorAgentViewSet
from api.view_group import GroupViewSet
from api.view_usergroup import UserGroupViewSet

urlpatterns = patterns(
    'api.views',
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^auth/', include('djoser.urls')),
    url(r'^request_vendor_account/', view_user.request_vendor_account,name='Request vendor account'),
    url(r'^register_retail_consumer/', view_user.register_consumer,name='Consumer Registration'),
    url(r'^dg_signin/', view_user.dg_signin,name='Deliveryguy SignIn'),
)


router = DefaultRouter()
router.register(r'area', AreaViewSet)
router.register(r'address', AddressViewSet)
router.register(r'vendor', VendorViewSet, base_name="Vendor")
router.register(r'vendoragent', VendorAgentViewSet)
router.register(r'deliveryguy', DGViewSet)
router.register(r'consumer', ConsumerViewSet, base_name ='consumer')
router.register(r'order', OrderViewSet, base_name ='order')
router.register(r'group', GroupViewSet)
router.register(r'usergroup', UserGroupViewSet)

urlpatterns += router.urls
# urlpatterns = format_suffix_patterns(urlpatterns)

