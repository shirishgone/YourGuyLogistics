from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns

from django.contrib.auth.forms import UserCreationForm
from api import views, view_user, view_order, view_vendor, view_consumer, view_address, view_deliveryguy, view_group

from api.view_address import AddressViewSet
from api.view_consumer import ConsumerViewSet
from api.view_order import OrderViewSet

from api.view_deliveryguy import DGViewSet
from api.view_vendor import VendorViewSet
from api.view_user import UserViewSet

from api.view_group import GroupViewSet
from api.view_usergroup import UserGroupViewSet


from rest_framework.routers import DefaultRouter


urlpatterns = patterns(
    'api.views',
    url(r'^docs/', include('rest_framework_swagger.urls')),
)


router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'vendor', VendorViewSet)
router.register(r'deliveryguy', DGViewSet)
router.register(r'consumer', ConsumerViewSet, base_name ='consumer')
router.register(r'address', AddressViewSet)
router.register(r'order', OrderViewSet, base_name ='order')
router.register(r'group', GroupViewSet)
router.register(r'usergroup', UserGroupViewSet)

urlpatterns += router.urls
# urlpatterns = format_suffix_patterns(urlpatterns)

