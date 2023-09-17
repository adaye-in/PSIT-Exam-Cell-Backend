from rest_framework.routers import DefaultRouter

from collageInfo import views

router = DefaultRouter()

router.register('', views.BranchViewSet, basename='branchviewset')
router.register('', views.SectionViewSet, basename='sectionviewset')
router.register('', views.RoomViewSet, basename='roomsviewset')

urlpatterns = []

urlpatterns += router.urls
