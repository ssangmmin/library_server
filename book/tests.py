from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Book

class TestView(TestCase):
    def setUp(self):
        self.client = Client()

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

        )

        book_002 = Book.objects.create(
            title='파친코2',
            book_author='이민진',
            publisher='문학사상',
            price='13000',
            release_date='2021-09-23',
            content='dadsjdasd',
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
