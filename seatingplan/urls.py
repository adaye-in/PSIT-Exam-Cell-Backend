from rest_framework.routers import DefaultRouter

from seatingplan import views

router = DefaultRouter()

router.register('', views.seatingplanViewSets, basename='seatingplanviewsets')

urlpatterns = []

urlpatterns += router.urls
