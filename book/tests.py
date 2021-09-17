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
        
