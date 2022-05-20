from django.shortcuts import render
from rest_framework import viewsets
from cite import serializers
from django.http import JsonResponse
from api.models import Tariff

from . import models


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ReviewSerializer
    queryset = models.Refiew.objects.all()


class OrderRequestViewSet(viewsets.ViewSet):
    serializer_class = serializers.OrderRequestSerializer
    queryset = models.OrderRequest.objects.all()

    def create(self, request):
        print(request)
        print(request.data)
        return JsonResponse({})


def index(request):
    context = {}
    for i, t in enumerate(Tariff.objects.filter(is_public=True)):
        context[f't{i}'] = t
    context['test'] = Tariff.objects.filter(is_public=False).first()
    context['order_save_url'] = request.build_absolute_uri() + 'cite-api/order/'
    return render(request, 'cite/index.html', context=context)

