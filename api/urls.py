from django.conf.urls import patterns, url, include
from django.contrib.auth.forms import UserCreationForm
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

from api import view_user
from api import view_dashboard
from api import view_freshdesk

from api.view_address import AddressViewSet
from api.view_area import AreaViewSet
from api.view_consumer import ConsumerViewSet
from api.view_order import OrderViewSet
from api.view_deliveryguy import DGViewSet
from api.view_vendor import VendorViewSet
from api.view_vendoragent import VendorAgentViewSet
from api.view_industry import IndustryViewSet
from api.view_product import ProductViewSet
from api.view_productcategory import ProductCategoryViewSet

urlpatterns = patterns(
    'api.views',
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^auth/', include('djoser.urls')),
    url(r'^register/', view_user.register,name='Registration'),
    url(r'^vendor_dashboard/', view_dashboard.vendor_dashboard, name='vendor_dashboard'),
	url(r'^freshdesk/all_tickets', view_freshdesk.all_tickets, name='freshdesk_all_tickets'),
	url(r'^freshdesk/groups', view_freshdesk.groups, name='freshdesk_groups'),
	url(r'^freshdesk/create_ticket', view_freshdesk.create_ticket, name='freshdesk_create_ticket'),
	url(r'^freshdesk/get_ticket', view_freshdesk.get_ticket, name='freshdesk_get_ticket'),
	url(r'^freshdesk/add_note', view_freshdesk.add_note, name='freshdesk_add_note'),
	url(r'^freshdesk/resolve', view_freshdesk.resolve, name='freshdesk_resolve'),
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
router.register(r'product', ProductViewSet)
router.register(r'productcategory', ProductCategoryViewSet)


urlpatterns += router.urls
# urlpatterns = format_suffix_patterns(urlpatterns)

