from django.urls import path
from django.conf.urls import include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('client', views.ClientViewSet)
router.register('user', views.UserViewSet)
router.register('referral', views.ReferralViewSet)
router.register('order', views.OrderViewSet)
router.register('tariff', views.TarifViewSet)
router.register('vpn-server', views.VpnServerViewSet)
router.register('peer', views.PeerViewSet)
router.register('server-traffic', views.ServerTrafficViewSet)
router.register('login', views.LoginViewSet, basename='login')




urlpatterns = [
    path('', include(router.urls)),
]