from http import client
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken


from . import serializers
from . import models
from . import permissions as p


class ClientViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.ClientSerializer
    queryset = models.Client.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAdminUser]


class UserViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()
    permission_classes = [p.IsNotAuthenticated | p.IsUsertOwner]


class ReferralViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.ReferralSerializer
    queryset = models.Referral.objects.all()
    permission_classes = [p.IsReferralOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = models.User.objects.get(
            client=request.user,
        )
        serializer.save(user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.OrderSerializer
    queryset = models.Order.objects.all()
    permission_classes = [p.IsOrderOwner]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = models.User.objects.get(
            client=request.user,
        )
        serializer.save(user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TarifViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.TariffSerializer
    queryset = models.Tariff.objects.all()
    permission_classes = [p.ReadOnly | IsAdminUser]


class VpnServerViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.VpnServerSerializer
    queryset = models.VpnServer.objects.all()
    permission_classes = [p.ReadOnly | IsAdminUser]


class PeerViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.PeerSerializer
    queryset = models.Peer.objects.all()
    permission_classes = [p.ReadOnly | IsAdminUser]


class ServerTrafficViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.ServerTrafficSerializer
    queryset = models.ServerTraffic.objects.all()
    permission_classes = [p.ReadOnly | IsAdminUser]


class PeerTrafficViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.PeerTrafficSerializer
    queryset = models.PeerTraffic.objects.all()
    permission_classes = [p.ReadOnly | IsAdminUser]


class LoginViewSet(viewsets.ViewSet):

    serializer_class = AuthTokenSerializer

    def create(self, request):

        return ObtainAuthToken().as_view()(request=request._request)
