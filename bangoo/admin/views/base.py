from django.shortcuts import render


def home(request, template_name='admin/home.html'):
    return render(request, template_name)