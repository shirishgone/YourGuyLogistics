from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from api_v2.view_consumers import ConsumerViewSet

urlpatterns = patterns(
	'',
)
router = DefaultRouter()
router.register(r'consumer', ConsumerViewSet)
urlpatterns += router.urls