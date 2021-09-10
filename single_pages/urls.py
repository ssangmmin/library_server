from django.urls import path
from . import views

urlpatterns = [
    path('book_list/', views.book_list),
    path('', views.book_detail),
]