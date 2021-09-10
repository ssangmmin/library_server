from django.shortcuts import render

def book_list(request):
    return render(
        request,
        'single_pages/book_list.html'
    )

def book_detail(request):
    return  render(
        request,
        'single_pages/book_detail.html'
    )
