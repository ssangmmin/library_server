from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from book.models import Book, Category, Tag, Review, Rental, Reservation

admin.site.register(Book, MarkdownxModelAdmin)
admin.site.register(Review)


admin.site.register(Rental)
admin.site.register(Reservation)


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)