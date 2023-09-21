from rest_framework.routers import DefaultRouter

from student import views

router = DefaultRouter()

router.register('', views.StudentViewSets, basename='studentviewset')

urlpatterns = []

urlpatterns += router.urls
