import self as self
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Book, Category, Tag

class TestView(TestCase):


    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')

        self.user_obama.is_staff = True
        self.user_obama.save()

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.tag_seller = Tag.objects.create(name='베스트셀러', slug='베스트셀러')
        self.tag_new = Tag.objects.create(name='신간', slug='신간')
        self.tag_best = Tag.objects.create(name='월간베스트', slug='월간베스트')
        self.tag_top = Tag.objects.create(name='Top10', slug='Top10')

        self.book_001 = Book.objects.create(
            title='파친코1',
            book_author='이민진',
            publisher='문학사상',
            price='13000',
            release_date='2021-09-23',
            content='dadsjdasd',
            author=self.user_trump,
            category=self.category_programming,


        )
        self.book_001.tags.add(self.tag_seller)
        self.book_001.tags.add(self.tag_top)

        self.book_002 = Book.objects.create(
            title='파친코2',
            book_author='이민진',
            publisher='문학사상',
            price='13000',
            release_date='2021-09-23',
            content='dadsjdasd',
            author=self.user_trump,
            category=self.category_music,

        )

        self.book_003 = Book.objects.create(
            title='Book Form 만들기',
            book_author='이민진',
            publisher='문학사상',
            price='13000',
            release_date='2021-09-23',
            content='카테고리가 없을수도 있죠',
            author=self.user_obama,
        )
        self.book_003.tags.add(self.tag_new)


    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('도서관안내', navbar.text)
        self.assertIn('자료검색', navbar.text)

        #로고 버튼은 홈으로 이동해야 한다.
        logo_btn = navbar.find('a', text='ssong library')
        self.assertEqual(logo_btn.attrs['href'], '/')

        # Home 버튼은 홈으로 이동해야 한다.
        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        # 자료검색 버튼은 포스트 목록 페이지로 이동해야 한다.
        blog_btn = navbar.find('a', text='자료검색')
        self.assertEqual(blog_btn.attrs['href'], '/book/')

        # About Me 버튼은 자기소개 페이지로 이동해야 한다.
        about_me_btn = navbar.find('a', text='도서관안내')
        self.assertEqual(about_me_btn.attrs['href'], '/book/')

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.book_set.count()})',
                      categories_card.text)
        self.assertIn(f'{self.category_music.name} ({self.category_music.book_set.count()})',
                      categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)


    def test_book_list(self):
        #포스트가 있는 경우
        self.assertEqual(Book.objects.count(), 3)

        response = self.client.get('/book/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        book_001_card = main_area.find('div', id='book-1')
        self.assertIn(self.book_001.title, book_001_card.text)
        self.assertIn(self.book_001.category.name, book_001_card.text)
        self.assertIn(self.tag_seller.name, book_001_card.text)
        self.assertIn(self.tag_top.name, book_001_card.text)
        self.assertNotIn(self.tag_new.name, book_001_card.text)
        self.assertNotIn(self.tag_best.name, book_001_card.text)

        book_002_card = main_area.find('div', id='book-2')
        self.assertIn(self.book_002.title, book_002_card.text)
        self.assertIn(self.book_002.category.name, book_002_card.text)
        self.assertNotIn(self.tag_seller.name, book_002_card.text)
        self.assertNotIn(self.tag_top.name, book_002_card.text)
        self.assertNotIn(self.tag_new.name, book_002_card.text)
        self.assertNotIn(self.tag_best.name, book_002_card.text)

        book_003_card = main_area.find('div', id='book-3')
        self.assertIn(self.book_003.title, book_003_card.text)
        self.assertIn(f'미분류', book_003_card.text)
        self.assertIn(self.tag_new.name, book_003_card.text)
        self.assertNotIn(self.tag_top.name, book_003_card.text)
        self.assertNotIn(self.tag_seller.name, book_003_card.text)
        self.assertNotIn(self.tag_best.name, book_003_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

        #도서가 없는 경우
        Book.objects.all().delete()
        self.assertEqual(Book.objects.count(), 0)
        response = self.client.get('/book/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)


    # 포스트 상세페이지 테스트
    def test_book_detail(self):


        #1.2 그 포스트의 url은'book/1/'이다.
        self.assertEqual(self.book_001.get_absolute_url(), '/book/1/')

        #2. 첫번째 포스트의 상세 페이지 테스트
        #2.1 첫번째 book url로 접근하면 정상적으로 작동한다(status code:200)
        response = self.client.get(self.book_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        #2.2 도서 목록 페이지와 똑같은 내비게이션 바가 있다.
        self.navbar_test(soup)

        self.category_card_test(soup)

        #2.3 첫 번째 도서의 제목이 웹 브라우저 탭 타이틀에 들어있다.
        self.assertIn(self.book_001.title, soup.title.text)

        #2.4 첫번째 도서의 제목이 도서 영역(book_area)에 있다.
        main_area = soup.find('div', id='main-area')
        book_area = main_area.find('div', id='book-area')
        self.assertIn(self.book_001.title, book_area.text)
        self.assertIn(self.category_programming.name, book_area.text)

        #2.5 첫 번째 도서의 작성자(author)가 도서영역에 있다.
        self.assertIn(self.user_trump.username.upper(), book_area.text)

        #2.6 첫 번째 도서의 내용(content)가 도서영역에 있다.
        self.assertIn(self.book_001.content, book_area.text)

        self.assertIn(self.tag_seller.name, book_area.text)
        self.assertIn(self.tag_top.name, book_area.text)
        self.assertNotIn(self.tag_new.name, book_area.text)
        self.assertNotIn(self.tag_best.name, book_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_programming.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.book_001.title, main_area.text)
        self.assertNotIn(self.book_002.title, main_area.text)
        self.assertNotIn(self.book_003.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_top.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_top.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_top.name, main_area.text)

        self.assertIn(self.tag_top.name, main_area.text)
        self.assertIn(self.book_001.title, main_area.text)
        self.assertNotIn(self.book_002.title, main_area.text)
        self.assertNotIn(self.book_003.title, main_area.text)

    def test_create_book(self):

        # 로그인하지 않으면 status_code가 200이면 안 된다!
        response = self.client.get('/book/create_book/')
        self.assertNotEqual(response.status_code, 200)
        # staff가 아닌 trump가 로그인을 한다.
        self.client.login(username='trump', password='somepassword')
        response = self.client.get('/book/create_book/')
        self.assertNotEqual(response.status_code, 200)
        # staff인 obama로 로그인한다.
        self.client.login(username='obama', password='somepassword')
        response = self.client.get('/book/create_book/')
        self.assertEqual(response.status_code, 200)
        # 도서 추가 페이지의 제목이 'Create Book - Library' 이어야 한다.
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual('Create Book - Library', soup.title.text)
        # 도서 추가 페이지에 main-area 영역의 제목은 'Create New Book' 이어야 한다.
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Book', main_area.text)
        # Client의 객체를 이용하여 POST method 방식으로 글을 작성한다.
        # 글 제목은 'Book Form 만들기', 내용은 여러분들 마음대로 작성하기
        self.client.post(
            {
                'title': 'Book Form 만들기',
                'content': '4124',
            }
        )

        # 최근에 작성한 글을 last_book 변수를 선언하여 가져온다.
        last_book = Book.objects.last()
        # 제일 최근에 작성한 글의 제목과 작성자명을 비교하여 검증해본다.
        self.assertEqual(last_book.title, 'Book Form 만들기')
        self.assertEqual(last_book.author.username, 'obama')