from django.conf.urls import patterns, url, include
from django.contrib.auth.forms import UserCreationForm
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

from api import view_user
#from api import view_dashboard

from api.view_address import AddressViewSet
from api.view_area import AreaViewSet
from api.view_consumer import ConsumerViewSet
from api.view_order import OrderViewSet
from api.view_deliveryguy import DGViewSet
from api.view_vendor import VendorViewSet
from api.view_vendoragent import VendorAgentViewSet
from api.view_group import GroupViewSet
from api.view_industry import IndustryViewSet
from api.view_product import ProductViewSet
from api.view_productcategory import ProductCategoryViewSet

urlpatterns = patterns(
    'api.views',
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^auth/', include('djoser.urls')),
    url(r'^register/', view_user.register,name='Registration'),
    url(r'^all_vendor_emails/', view_user.all_vendor_emails,name='all_vendor_emails'),
    #url(r'^vendor_dashboard/', view_dashboard.vendor_dashboard, name='vendor_dashboard'),
)


router = DefaultRouter()
router.register(r'area', AreaViewSet)
router.register(r'address', AddressViewSet)
router.register(r'industry', IndustryViewSet)
router.register(r'vendor', VendorViewSet)
router.register(r'vendoragent', VendorAgentViewSet)
router.register(r'deliveryguy', DGViewSet)
router.register(r'consumer', ConsumerViewSet)
router.register(r'order', OrderViewSet, base_name = 'orders')
router.register(r'group', GroupViewSet)
router.register(r'product', ProductViewSet)
router.register(r'productcategory', ProductCategoryViewSet)


urlpatterns += router.urls
# urlpatterns = format_suffix_patterns(urlpatterns)

