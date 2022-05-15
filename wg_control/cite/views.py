from django.shortcuts import render
from api.models import Tariff
# Create your views here.


def index(request):
    context = {}
    for i, t in enumerate(Tariff.objects.filter(is_public=True)):
        context[f't{i}'] = t
    context['test'] = Tariff.objects.filter(is_public=False).first()
    return render(request, 'cite/index.html', context=context)