from django.conf.urls import url, patterns, include
from rest_framework.routers import DefaultRouter

from api_v3 import utils, views, view_user, view_freshdesk, view_address, view_dashboard, report
from api_v3.view_consumer import ConsumerViewSet
from api_v3.view_dg import DGViewSet
from api_v3.view_product import ProductViewSet
from api_v3.view_vendor import VendorViewSet
from api_v3.view_vendoragent import VendorAgentViewSet
from api_v3.view_order import OrderViewSet

urlpatterns = patterns(
    'api_v3.views',
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^auth/', include('djoser.urls')),
    url(r'^register/', view_user.register, name='Registration'),
    url(r'^fill_full_address/', view_address.fill_full_address, name='fill_full_address'),
    url(r'^add_address/', view_address.add_address, name='add_address'),
    url(r'^remove_address', view_address.remove_address, name='remove_address'),
    # url(r'^dashboard_report/', view_dashboard.report, name='dashboard_report'),
    url(r'^excel_download/', view_dashboard.excel_download, name='excel_download'),
    url(r'^freshdesk/all_tickets', view_freshdesk.all_tickets, name='freshdesk_all_tickets'),
    url(r'^freshdesk/groups', view_freshdesk.groups, name='freshdesk_groups'),
    url(r'^freshdesk/create_ticket', view_freshdesk.create_ticket, name='freshdesk_create_ticket'),
    url(r'^freshdesk/get_ticket', view_freshdesk.get_ticket, name='freshdesk_get_ticket'),
    url(r'^freshdesk/add_note', view_freshdesk.add_note, name='freshdesk_add_note'),
    url(r'^freshdesk/resolve', view_freshdesk.resolve, name='freshdesk_resolve'),
    #url(r'^cron_trial/', cron.cron_trial, name='cron_trial'),
    #url(r'^cron_auto_assign/', cron.auto_assign, name='cron_auto_assign'),
    #url(r'^cron_daily_report/', cron.daily_report, name='cron_daily_report'),
    url(r'^daily_report/', report.daily_report, name='daily_report'),
    url(r'^report_order/', report.report_order, name='report_order'),
    url(r'^report_dashboard', report.report_dashboard, name='report_dashboard'),
    url(r'^is_recurring_var_setting/', utils.is_recurring_var_setting, name='is_recurring_var_setting'),
    url(r'^delivery_status_update/', utils.delivery_status_update, name='delivery_status_update'),
    url(r'^attach_order_to_deliverystatus/', utils.attach_order_to_deliverystatus,
        name='attach_order_to_deliverystatus'),
    url(r'^fill_order_ids/', utils.fill_order_ids, name='fill_order_ids'),

)

router = DefaultRouter()
router.register(r'industry', views.IndustryViewSet)
router.register(r'vendor', VendorViewSet)
router.register(r'vendoragent', VendorAgentViewSet)
router.register(r'deliveryguy', DGViewSet)
router.register(r'consumer', ConsumerViewSet)
router.register(r'order', OrderViewSet, base_name='orders')
router.register(r'product', ProductViewSet)

urlpatterns += router.urls
# urlpatterns = format_suffix_patterns(urlpatterns)
