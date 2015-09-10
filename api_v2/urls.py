from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from api_v2.view_consumers import ConsumerViewSet
from api_v2.view_order import OrderViewSet

urlpatterns = patterns(
	'',
)
router = DefaultRouter()
router.register(r'consumer', ConsumerViewSet)
router.register(r'order', OrderViewSet, base_name='Order')
urlpatterns += router.urls