from django.urls import path
from . import views

urlpatterns = [


    path('<int:pk>/', views.book_detail.as_view()), #FBV 방식
    path('',views.book_list.as_view()),
    # path('', views.book_list), #FBV 방식
]