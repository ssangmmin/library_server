from django.shortcuts import render
from .models import Book

def index(request):
    books = Book.objects.all().order_by('-pk')

    return render(
        request,
        'book/index.html',
        {
            'books': books,
        }
    )

def single_book_page(request, pk):
    book = Book.objects.get(pk=pk)

    return render(
        request,
        'book/single_book_page.html',
        {
            'book': book,
        }
    )
