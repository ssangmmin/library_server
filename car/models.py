from django.db import models


class Car(models.Model):
    name = models.CharField(max_length=128)
    manufacturer = models.CharField(max_length=255)
    price = models.IntegerField()
    release_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField()

    def __str__(self):
        return f'[{self.pk}]{self.name}'

    def get_absolute_url(self):
        return f'/car/{self.pk}/'