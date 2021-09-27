from django.shortcuts import render
from .models import Book, Category
from django.views.generic import ListView, DetailView


class book_list(ListView):
    model = Book
    ordering = '-pk'

    def get_context_data(self, **kwargs):
        context = super(book_list, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_book_count'] = Book.objects.filter(category=None).count()
        return context


# def book_list(request):
#     books = Book.objects.all().order_by('-pk')
#
#     return render(
#         request,
#         'book/book_list.html',
#         {
#             'books': books, #왼쪽은 templates에서 사용할 변수명
#         }
#     )

class book_detail(DetailView):
    model = Book

    def get_context_data(self, **kwargs):
        context = super(book_detail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_book_count'] = Book.objects.filter(category=None).count()
        return context

# def book_detail(request, pk):
#     book = Book.objects.get(pk=pk)
#
#     return render(
#         request,
#         'book/book_detail.html',
#         {
#             'b': book,
#         }
#     )


