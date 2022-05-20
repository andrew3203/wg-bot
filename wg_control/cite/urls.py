from django.urls import path
from rest_framework.routers import DefaultRouter
from django.conf.urls import include

from . import views

router = DefaultRouter()
router.register('order', views.OrderRequestViewSet, basename='order-request')
router.register('review', views.ReviewViewSet)


urlpatterns = [
        path('', views.index, name='index'),
        path('cite-api/', include(router.urls)),
]
