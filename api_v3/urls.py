from django.conf.urls import url, patterns
from rest_framework.routers import DefaultRouter

from api_v3 import mail, views, view_user, view_freshdesk, view_address, view_dashboard, report, cron_jobs, \
    view_internals
from api_v3.view_consumer import ConsumerViewSet
from api_v3.view_dg import DGViewSet
from api_v3.view_order import OrderViewSet
from api_v3.view_product import ProductViewSet
from api_v3.view_vendor import VendorViewSet
from api_v3.view_vendoragent import VendorAgentViewSet

urlpatterns = patterns(
    'api_v3.views',
    url(r'^register/', view_user.register, name='Registration'),
    # url(r'^reset_password_link/', view_user.reset_password_link, name='reset_password_link'),
    # url(r'^reset_password/', view_user.reset_password, name='reset_password'),
    url(r'^add_address/', view_address.add_address, name='add_address'),
    url(r'^remove_address', view_address.remove_address, name='remove_address'),
    url(r'^dashboard_stats/', view_dashboard.dashboard_stats, name='dashboard_stats'),
    url(r'^excel_download/', view_dashboard.excel_download, name='excel_download'),
    url(r'^freshdesk/all_tickets', view_freshdesk.all_tickets, name='freshdesk_all_tickets'),
    url(r'^freshdesk/groups', view_freshdesk.groups, name='freshdesk_groups'),
    url(r'^freshdesk/create_ticket', view_freshdesk.create_ticket, name='freshdesk_create_ticket'),
    url(r'^freshdesk/get_ticket', view_freshdesk.get_ticket, name='freshdesk_get_ticket'),
    url(r'^freshdesk/add_note', view_freshdesk.add_note, name='freshdesk_add_note'),
    url(r'^freshdesk/resolve', view_freshdesk.resolve, name='freshdesk_resolve'),
    url(r'^daily_report/', report.daily_report, name='daily_report'),
    url(r'^cod_report/', report.cod_report, name='cod_report'),
    url(r'^website_email/', mail.website_email, name='website_email'),
    url(r'^assign_dg/', cron_jobs.assign_dg, name='assign_dg'),

    # STAFF METHODS -----------------------------------------
    url(r'^new_order_id_for_old_order_id/', view_internals.new_order_id_for_old_order_id,
        name='new_order_id_for_old_order_id'),
    url(r'^old_order_id_for_new_order_id/', view_internals.old_order_id_for_new_order_id,
        name='old_order_id_for_new_order_id'),
    url(r'^fill_full_address/', view_internals.fill_full_address, name='fill_full_address')
    # --------------------------------------------------------
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
