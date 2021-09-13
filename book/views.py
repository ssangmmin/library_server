from django.shortcuts import render
from .models import Book

def book_list(request):
    books = Book.objects.all().order_by('-pk')

    return render(
        request,
        'book/book_list.html',
        {
            'books': books, #왼쪽은 templates에서 사용할 변수명
        }
    )

def book_detail(request, pk):
    book = Book.objects.get(pk=pk)

    return render(
        request,
        'book/book_detail.html',
        {
            'b': book,
        }
    )


