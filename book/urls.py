from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/delete_rental/', views.delete_rental),
    path('<int:pk>/borrowing/', views.borrowing),
    path('search/<str:q>/', views.BookSearch.as_view()),
    path('delete_review/<int:pk>/', views.delete_review),
    path('update_review/<int:pk>/', views.ReviewUpdate.as_view()),
    path('<int:pk>/new_review/', views.new_review),
    path('update_book/<int:pk>/', views.BookUpdate.as_view()),
    path('create_book/', views.BookCreate.as_view()),
    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page),
    path('<int:pk>/', views.book_detail.as_view()), #FBV 방식
    path('', views.book_list.as_view()),
    # path('', views.book_list), #FBV 방식
]