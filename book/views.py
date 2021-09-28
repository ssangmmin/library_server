from django.shortcuts import render
from .models import Book, Category, Tag
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
def category_page(request, slug):
    if slug == 'no_category':
        category ='미분류'
        book_list = Book.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        book_list = Book.objects.filter(category=category)

    return render(
      request,
            'book/book_list.html',
        {
                'book_list': book_list,
                'categories': Category.objects.all(),
                'no_category_book_count': Book.objects.filter(category=None).count(),
                'category': category,
        }
    )
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

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    book_list = tag.book_set.all()

    return render(
        request,
        'book/book_list.html',
        {
            'book_list': book_list,
            'tag': tag,
            'categories': Category.objects.all(),
            'no_category_book_count': Book.objects.filter(category=None).count(),
        }
    )

