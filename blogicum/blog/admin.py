from django.contrib import admin
from .models import Category, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'author',
        'is_published',
        'pub_date',
        'category',
        'location',
        'created_at'
    )
    list_editable = (
        'is_published',
        'author',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


admin.site.register(Category)
admin.site.register(Location)
