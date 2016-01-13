from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from api_v2.view_consumers import ConsumerViewSet
from api_v2.view_order import OrderViewSet
from api_v2.view_vendor import VendorViewSet
from api_v2.view_product import ProductViewSet

from api_v2 import view_dashboard
from api_v2 import utils
from api_v2 import views
from api_v2 import mail
from api_v2 import view_dg
from api_v2 import view_notifications

urlpatterns = patterns(
	'',
	url(r'^cron/', views.cron_trial, name = 'cron_trial'),
	url(r'^daily_report/', views.daily_report, name = 'daily_report'),
	url(r'^dashboard_report/', view_dashboard.report, name = 'dashboard_report'),
	url(r'^excel_download/', view_dashboard.excel_download, name = 'excel_download'),
	url(r'^website_email/', mail.website_email, name = 'website_email'),
	
	url(r'^new_order_id_for_old_order_id/', utils.new_order_id_for_old_order_id, name = 'new_order_id_for_old_order_id'),
	url(r'^old_order_id_for_new_order_id/', utils.old_order_id_for_new_order_id, name = 'old_order_id_for_new_order_id'),	
	url(r'^fill_full_address/', utils.fill_full_address, name = 'fill_full_address'),
	url(r'^dg_app_version/', view_dg.dg_app_version, name='dg_app_version'),
	url(r'^delivery_guy/profile/', view_dg.profile, name='dg_profile'),
	url(r'^notifications/', view_notifications.my_notifications, name = 'my_notifications'),
)
router = DefaultRouter()
router.register(r'consumer', ConsumerViewSet)
router.register(r'order', OrderViewSet, base_name='Order')
router.register(r'delivery_guy', view_dg.DGViewSet, base_name='delivery_guy')
router.register(r'vendor', VendorViewSet, base_name='vendor')
router.register(r'product', ProductViewSet, base_name='product')

urlpatterns += router.urls