from django.contrib import admin

from book.models import Book, Category

admin.site.register(Book)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)