import self as self
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Book

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')

    def test_book_list(self):
        #1.1 테스트 목록 페이지를 가져온다.
        response = self.client.get('/book/')

        #1.2 정삭적으로 페이지가 로드된다.
        self.assertEqual(response.status_code, 200)

        #1.3 페이지 타이틀은 '도서목록'이다.
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, '도서목록')

        #1.4 내비게이션 바가 있다
        navbar = soup.nav

        #1.5 "Home", "자료검색", "도서관안내" 라는 문구가 내비게이션 바에 있다.
        self.assertIn('Home', navbar.text)
        self.assertIn('자료검색', navbar.text)
        self.assertIn('도서관안내', navbar.text)

        #2.1 메인 영역에 게시물이 하나도 없다면 (count 함수 활용)
        self.assertEqual(Book.objects.count(), 0)

        #2.2 '아직 게시물이 없습니다'라는 문구가 보인다.
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

        #3.1 게시물 2개를 등록하고 2개가 등록되었는지 체크
        book_001 = Book.objects.create(
            title='파친코1',
            book_author='이민진',
            publisher='문학사상',
            price='13000',
            release_date='2021-09-23',
            content='dadsjdasd',
            author=self.user_trump

        )

        book_002 = Book.objects.create(
            title='파친코2',
            book_author='이민진',
            publisher='문학사상',
            price='13000',
            release_date='2021-09-23',
            content='dadsjdasd',
            author=self.user_obama
        )

        self.assertEqual(Book.objects.count(), 2)

        response = self.client.get('/book/')
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)

        main_area = soup.find('div', id='main-area')
        self.assertIn(book_001.title, main_area.text)
        self.assertIn(book_002.title, main_area.text)

        #3.2 '아직 게시물이 없습니다'라는 문구는 더 이상 보이지 않는다.
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

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
        #아직 작성불가

        #2.6 첫 번째 도서의 내용(content)가 도서영역에 있다.
        self.assertIn(book_001.content, book_area.text)