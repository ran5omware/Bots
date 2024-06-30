from django.shortcuts import render
from news.models import Articles


def index(request):
    latest_news = [Articles.objects.order_by('date').last()]
    context = {
        'latest_news': latest_news
    }
    return render(request, 'main/index.html', context)


def about(request):
    return render(request, 'main/about.html')


def contacts(request):
    return render(request, 'main/contacts.html')
