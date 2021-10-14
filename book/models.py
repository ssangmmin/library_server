from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from markdown import markdown
from markdownx.models import MarkdownxField
import os


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/book/tag/{self.slug}/'


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # 카테고리 페이지의 URL을 구성한다.
        # 카테고리 페이지 URL은 '/blog/category/[카테고리의 slug 필드 값]/' 이다.
        # 예) [문화 & 예술] 카테고리는 '/blog/category/문화-예술'로 만들어진다.
        # 키워드 f는 format의 약자로 변수와 문자열로 구성하여 하나의 문자열을 완성시킨다.
        return f'/book/category/{self.slug}/'

    class Meta:
        verbose_name_plural = 'Categories'






class Book(models.Model):
    title = models.CharField(max_length=30)
    book_author = models.CharField(max_length=128)
    publisher = models.CharField(max_length=255)
    price = models.IntegerField()
    release_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = MarkdownxField()
    hook_text = models.CharField(max_length=100, blank=True)

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True)

    head_image = models.ImageField(upload_to='book/images/%Y/%m/%d/', blank=True)
    file_upload = models.FileField(upload_to='book/files/%Y/%m/%d/', blank=True)




    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'

    def get_absolute_url(self):
        return f'/book/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]

    def get_content_markdown(self):
        return markdown(self.content)

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://doitdjango.com/avatar/id/334/485d7d1a24069abc/svg/{self.author.email}'


class Review(models.Model):
    # CASCADE이기 때문에 POST글이 삭제되면 댓글도 같이 삭제됩니다.
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    content = models.TextField()
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author} :: {self.content} :: {self.score}'

    def get_absolute_url(self):
        return f'{self.book.get_absolute_url()}#review-{self.pk}'

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://doitdjango.com/avatar/id/334/485d7d1a24069abc/svg/{self.author.email}'

class Rental(models.Model):
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, blank=False, null=True)
    librarian = models.ForeignKey(User, on_delete=models.SET_NULL, blank=False, null=True, related_name='librarian')
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=False, null=True, related_name='customer')
    created_at = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField()

    def __str__(self):
        return f'{self.customer} :: {self.return_date}'








