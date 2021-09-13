from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.car_detail), #FBV 방식 // 함수를 불러와서 사용
    path('', views.car_list), #FBV 방식

]