from django.db.models import Q
from django.shortcuts import render

from book.models import Book
from book.views import book_list


def index(request):
    recent_books = Book.objects.order_by('-pk')[:3]
    return  render(
        request,
        'single_pages/index.html',
        {
            'recent_books' : recent_books,
        }
    )



