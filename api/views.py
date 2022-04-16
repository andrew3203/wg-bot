from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication

from . import serializers
from . import models
from . import permissions


class BaseUserViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.BaseUserSerializer
    queryset = models.BaseUser.objects.all()
    authentication_classes = (TokenAuthentication,)
    #permission_classes = (permissions.UpdateOwnProfile,)


class UserViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()
    authentication_classes = (TokenAuthentication,)
    #permission_classes = (permissions.UpdateOwnProfile,)


class ReferralViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.ReferralSerializer
    queryset = models.Referral.objects.all()
    #permission_classes = (permissions.UpdateOwnProfile,)


class OrderViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.OrderSerializer
    queryset = models.Order.objects.all()
    #permission_classes = (permissions.UpdateOwnProfile,)


class TarifViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.TariffSerializer
    queryset = models.Tariff.objects.all()
    #permission_classes = (permissions.UpdateOwnProfile,)


class VpnServerViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.VpnServerSerializer
    queryset = models.VpnServer.objects.all()
    #permission_classes = (permissions.UpdateOwnProfile,)


class PeerViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.PeerSerializer
    queryset = models.Peer.objects.all()
    #permission_classes = (permissions.UpdateOwnProfile,)


class ServerTrafficViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.ServerTrafficSerializer
    queryset = models.ServerTraffic.objects.all()
    #permission_classes = (permissions.UpdateOwnProfile,)


class PeerTrafficViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.PeerTrafficSerializer
    queryset = models.PeerTraffic.objects.all()
    #permission_classes = (permissions.UpdateOwnProfile,)
