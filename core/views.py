# core/views.py

from django.shortcuts import render


def index(request):
    """صفحه اصلی سایت"""
    context = {
        'page_title': 'خانه',
    }
    return render(request, 'core/index.html', context)
