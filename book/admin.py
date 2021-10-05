from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from book.models import Book, Category, Tag

admin.site.register(Book, MarkdownxModelAdmin)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)