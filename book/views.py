from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify

from .forms import ReviewForm
from .models import Book, Category, Tag
from django.views.generic import ListView, DetailView, CreateView, UpdateView


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
        context['review_form'] = ReviewForm
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

class BookCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Book
    fields = ['title', 'book_author', 'publisher', 'price', 'release_date', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(BookCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)

            return response

        else:
            return redirect('/book/')

class BookUpdate(LoginRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'book_author', 'publisher', 'price', 'release_date', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    template_name = 'book/book_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(BookUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(BookUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(BookUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)

        return response

# 댓글 작성 POST 요청이 들어올 경우 처리
def new_review(request, pk):

    # 로그인한 경우
    if request.user.is_authenticated:

        book = get_object_or_404(Book, pk=pk)
        if request.method == 'POST':
            review_form = ReviewForm(request.POST)

            if review_form.is_valid():

                review = review_form.save(commit=False)
                review.book = book

                review.author = request.user

                review.save()

                return redirect(review.get_absolute_url())
        else:
            # POST 방식이 아닌 요청이 들어온 경우는
            # 포스트 상세페이지로 다시 이동한다.
            return redirect(book.get_absolute_url())
    else:
        # 로그인하지 않은 사용자가 접근한 경우는 PermissionDenied 예외를 발생시키고
        # 허가거부 페이지를 응답으로 보내게 된다.
        raise PermissionDenied