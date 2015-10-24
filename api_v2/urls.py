from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from api_v2.view_consumers import ConsumerViewSet
from api_v2.view_order import OrderViewSet
from api_v2.view_dg import DGViewSet
from api_v2 import utils
from api_v2 import views

urlpatterns = patterns(
	'',
	url(r'^is_recurring_var_setting/', utils.is_recurring_var_setting, name = 'is_recurring_var_setting'),
	url(r'^delivery_status_update/', utils.delivery_status_update, name = 'delivery_status_update'),
	url(r'^fill_full_address/', utils.fill_full_address, name = 'fill_full_address'),
	url(r'^cron/', views.cron_trial, name = 'cron_trial'),
)
router = DefaultRouter()
router.register(r'consumer', ConsumerViewSet)
router.register(r'order', OrderViewSet, base_name='Order')
router.register(r'delivery_guy', DGViewSet, base_name='delivery_guy')
urlpatterns += router.urls