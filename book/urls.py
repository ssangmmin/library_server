from django.urls import path
from . import views

urlpatterns = [
    path('create_book/', views.BookCreate.as_view()),
    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page),
    path('<int:pk>/', views.book_detail.as_view()), #FBV 방식
    path('', views.book_list.as_view()),
    # path('', views.book_list), #FBV 방식
]