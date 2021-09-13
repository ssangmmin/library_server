from django.shortcuts import render

def index(request):
    return  render(
        request,
        'single_pages/index.html'
    )
