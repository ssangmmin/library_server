from django.db import models
from django.contrib.auth.models import User
import os


class Book(models.Model):
    title = models.CharField(max_length=30)
    book_author = models.CharField(max_length=128)
    publisher = models.CharField(max_length=255)
    price = models.IntegerField()
    release_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=1500)
    hook_text = models.CharField(max_length=100, blank=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    head_image = models.ImageField(upload_to='book/images/%Y/%m/%d/', blank=True)
    file_upload = models.FileField(upload_to='book/files/%Y/%m/%d/', blank=True)

    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'

    def get_absolute_url(self):
        return f'/book/{self.pk}'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]

