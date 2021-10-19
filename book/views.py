from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.core.mail import EmailMessage
from .forms import ReviewForm, RentalForm, ReservationForm
from .models import Book, Category, Tag, Review, Rental, Reservation
from django.views.generic import ListView, DetailView, CreateView, UpdateView


class book_list(ListView):
    model = Book
    ordering = '-pk'
    paginate_by = 3

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
                'book_list': book_list, # book_list를 book_list 트럭에 담아서 book_list.html으로 옮겨서 사용
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
        context['rental_form'] = RentalForm
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
    fields = ['title', 'book_author', 'publisher', 'price', 'release_date', 'hook_text', 'content', 'head_image', 'file_upload', 'category', ]

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
        # 요청받은 주소에서 pk 번호를 이용해 Post 테이블을 조회
        # 해당 pk를 가지는 포스트가 존재한다면 get 동작 수행
        # 그렇지 않으면 404 예외발생하여 코드 실행을 중단하고
        # 클라이언트에게 404 응답을 보내게 된다.
        book = get_object_or_404(Book, pk=pk)

        # request 요청 내용 중 method 변수를 확인하여
        # POST 요청인지 확인한다.
        if request.method == 'POST':
            # CommentForm에 POST 요청받은 내용을 담아 form 객체를 생성
            review_form = ReviewForm(request.POST)
            # form 객체 내부의 is_valid() 함수를 실행하여 유효성 검사 후
            # 이상이 없다면 if문 실행
            if review_form.is_valid():
                # comment_form에 담긴 내용을 DB에 저장하는 동작은 하지만
                # 트랜젝션(Transaction)은 이뤄지지 않았다. (commit=False)
                # comment 변수에는 Comment 객체가 담겨져 있다.
                review = review_form.save(commit=False)
                # comment 객체에 post 필드를 채워준다. (처음 pk로 불러온 Post)
                review.book = book
                # author 필드는 현재 로그인한 사용자의 객체를 담는다.
                review.author = request.user
                # comment 객체의 모든 내용을 채웠으므로
                # 최종적으로 데이터베이스에 저장한다. 트랜젝션이 이루어진다.
                review.score = request.POST.get('my_score')
                review.save()
                # 댓글이 작성된 곳으로 페이지 이동한다.
                return redirect(review.get_absolute_url())
        else:
            # POST 방식이 아닌 요청이 들어온 경우는
            # 포스트 상세페이지로 다시 이동한다.
            return redirect(book.get_absolute_url())
    else:
        # 로그인하지 않은 사용자가 접근한 경우는 PermissionDenied 예외를 발생시키고
        # 허가거부 페이지를 응답으로 보내게 된다.
        raise PermissionDenied


class ReviewUpdate(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author: # 현재 댓글을 작성한 작성자
            return super(ReviewUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(ReviewUpdate, self).form_valid(form)
        my_score = self.request.POST.get('my_score')

        if my_score and (0 < int(my_score) <= 5):
            self.object.score = my_score
            self.object.save()

        else:
            raise ValueError('별점은 1~5점을 입력하셔야 합니다.')

        return response


def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    book = review.book
    if request.user.is_authenticated and request.user == review.author:
        review.delete()
        return redirect(book.get_absolute_url())
    else:
        raise PermissionDenied


class BookSearch(book_list):
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs['q']
        book_list = Book.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q)
        ).distinct() # distinct는 검색한 검색어의중복을 하나로
        return book_list

    def get_context_data(self, **kwargs):
        context = super(BookSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search: {q} ({self.get_queryset().count()})'

        return context



def borrowing(request, pk):
    # 로그인한 경우
    if request.user.is_authenticated and (request.user.is_staff and request.user.is_superuser):
        # 요청받은 주소에서 pk 번호를 이용해 Post 테이블을 조회
        # 해당 pk를 가지는 포스트가 존재한다면 get 동작 수행
        # 그렇지 않으면 404 예외발생하여 코드 실행을 중단하고
        # 클라이언트에게 404 응답을 보내게 된다.
        book = get_object_or_404(Book, pk=pk)

        if request.method == 'POST':

            customer = get_object_or_404(User, username=request.POST.get('customer-name'))
            return_date = request.POST.get('return-date')
            librarian = request.user


            # request 요청 내용 중 method 변수를 확인하여
            # POST 요청인지 확인한다.

            # CommentForm에 POST 요청받은 내용을 담아 form 객체를 생성
            rental_form = RentalForm(request.POST)
            # form 객체 내부의 is_valid() 함수를 실행하여 유효성 검사 후
            # 이상이 없다면 if문 실행
            if rental_form.is_valid():
                # comment_form에 담긴 내용을 DB에 저장하는 동작은 하지만
                # 트랜젝션(Transaction)은 이뤄지지 않았다. (commit=False)
                # comment 변수에는 Comment 객체가 담겨져 있다.
                rental = rental_form.save(commit=False)
                # comment 객체에 post 필드를 채워준다. (처음 pk로 불러온 Post)
                rental.book = book
                # author 필드는 현재 로그인한 사용자의 객체를 담는다.
                rental.librarian = request.user
                # comment 객체의 모든 내용을 채웠으므로
                # 최종적으로 데이터베이스에 저장한다. 트랜젝션이 이루어진다.
                고객이름 = request.POST.get('customer-name')
                rental.customer = get_object_or_404(User, username=고객이름)
                rental.save()
                # 댓글이 작성된 곳으로 페이지 이동한다.
                return redirect(book.get_absolute_url())
        else:
            # POST 방식이 아닌 요청이 들어온 경우는
            # 포스트 상세페이지로 다시 이동한다.
            return redirect(book.get_absolute_url())
    else:
        # 로그인하지 않은 사용자가 접근한 경우는 PermissionDenied 예외를 발생시키고
        # 허가거부 페이지를 응답으로 보내게 된다.
        raise PermissionDenied


def delete_rental(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        book.rental_set.first().delete()
        return redirect(book.get_absolute_url())
    else:
        raise PermissionDenied


 # 'book/' + 'pk' + '/' = 'book/pk/'
 # 'book/' + pk + '/' = 'book/1/'

# search 검색어창 페이지 연결
def search(request):
    return render(
        request,
        'book/search.html',
    )
# info 페이지 연결
def info(request):
    return render(
        request,
        'book/info.html',
    )

def reservation_now(request):
    reservations = Reservation.objects.all()

    return render(
        request,
        'book/reservation_now.html',
        {
            'reservations': reservations,
        }
    )


def reservation(request, pk):
    book = get_object_or_404(Book, pk=pk) # pk = primary key (Book 안의 필드값)

    rental = book.rental_set.all().first()

    reservation = book.reservation_set.all()

    waiting_number = reservation.count()

    available_date = rental.return_date + timedelta(1) # timedelta(1)은 return_date + 1일 추가하기

    if request.user.is_authenticated:
        if not request.user.is_staff and not request.user.is_superuser:
            if request.method == 'POST':

                # CommentForm에 POST 요청받은 내용을 담아 form 객체를 생성
                reservation_form = ReservationForm(request.POST)
                # form 객체 내부의 is_valid() 함수를 실행하여 유효성 검사 후
                # 이상이 없다면 if문 실행
                if reservation_form.is_valid():
                    # comment_form에 담긴 내용을 DB에 저장하는 동작은 하지만
                    # 트랜젝션(Transaction)은 이뤄지지 않았다. (commit=False)
                    # comment 변수에는 Comment 객체가 담겨져 있다.
                    reservation = reservation_form.save(commit=False)

                    reservation.book = book

                    reservation.customer = request.user

                    reservation.save()

                    # email = EmailMessage('안녕', 'django 테스트입니다', to=[request.user.email])
                    # email.send()

                    return render(
                        request,
                        'book/reservation.html',
                        {
                            'available_date': available_date,
                            'waiting_number': waiting_number,
                        }
                    )

            return render(
                request,
                'book/reservation.html',
                {
                    'available_date': available_date,
                    'waiting_number': waiting_number,
                }
            )




