from rest_framework.routers import DefaultRouter

from seatingplan import views

router = DefaultRouter()

router.register('', views.seatingplanViewSets, basename='seatingplanviewsets')
router.register('', views.sessionRoomViewSets, basename='sessionroomviewsets')

urlpatterns = []

urlpatterns += router.urls
