from rest_framework.routers import DefaultRouter

from adminsession import views

router = DefaultRouter()

router.register('', views.SessionViewSet, basename='Sessionviewset')
router.register('', views.ReportViewSet, basename='Reportviewset')

urlpatterns = []

urlpatterns += router.urls
