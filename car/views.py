from django.shortcuts import render
from .models import Car

def car_list(request):
    cars = Car.objects.all().order_by('-pk')
    return render(
        request,
        'car/car_list.html',
        {
            'cars': cars,
        }

    )

def car_detail(request, pk):
    car = Car.objects.get(pk=pk)

    return render(
        request,
        'car/car_detail.html',
        {
            'car': car,
        }
    )

