from rest_framework.routers import DefaultRouter

from auth_app import views

router = DefaultRouter()

router.register('', views.AdminViewSet, basename='adminviewset')

urlpatterns = []

urlpatterns += router.urls
