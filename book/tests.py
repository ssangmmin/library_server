import self as self
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Book, Category

class TestView(TestCase):


    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

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

        self.book_002 = Book.objects.create(
            title='파친코1',
            book_author='이민진',
            publisher='문학사상',
            price='13000',
            release_date='2021-09-23',
            content='dadsjdasd',
            author=self.user_trump,
            category=self.category_music,

        )
        self.book_003 = Book.objects.create(
            title='파친코1',
            book_author='이민진',
            publisher='문학사상',
            price='13000',
            release_date='2021-09-23',
            content='카테고리가 없을수도 있죠',
            author=self.user_obama,

        )
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

        book_002_card = main_area.find('div', id='book-2')
        self.assertIn(self.book_002.title, book_002_card.text)
        self.assertIn(self.book_002.category.name, book_002_card.text)

        book_003_card = main_area.find('div', id='book-3')
        self.assertIn(self.book_003.title, book_003_card.text)
        self.assertIn(self.book_003.category.name, book_003_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

        #도서가 없는 경우
        Book.objects.all().delete()
        self.assertEqual(Book.objects.count(), 0)
        response = self.client.get('/book/')
        soup = BeautifulSoup(response.content, 'html_parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)


    # 포스트 상세페이지 테스트
    def test_post_detail(self):
        #1.1 Book 하나 있다.
        book_001 = Book.objects.create(
            title='파친코1',
            book_author='이민진',
            publisher='문학사상',
            price='13000',
            release_date='2021-09-23',
            content='dadsjdasd',
            author=self.user_trump
        )

        #1.2 그 포스트의 url은'book/1/'이다.
        self.assertEqual(book_001.get_absolute_url(),'/book/1')

        #2. 첫번째 포스트의 상세 페이지 테스트
        #2.1 첫번째 book url로 접근하면 정상적으로 작동한다(status code:200)
        response = self.assertEqual(book_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        #2.2 도서 목록 페이지와 똑같은 내비게이션 바가 있다.
        navbar = soup.nav
        self.assertIn('도서목록', navbar.text)
        self.assertIn('자료검색', navbar.text)

        #2.3 첫 번째 도서의 제목이 웹 브라우저 탭 타이틀에 들어있다.
        self.assertIn(book_001.title, soup.title.text)

        #2.4 첫번째 도서의 제목이 도서 영역(book_area)에 있다.
        main_area = soup.find('div', id='main-area')
        book_area = main_area.find('div', id='book-area')
        self.assertIn(book_001.title, book_area.text)

        #2.5 첫 번째 도서의 작성자(author)가 도서영역에 있다.
        self.assertIn(self.user_trump.username.upper(), book_area.text)

        #2.6 첫 번째 도서의 내용(content)가 도서영역에 있다.
        self.assertIn(book_001.content, book_area.text)