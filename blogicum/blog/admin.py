from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'created_at'
    )
    list_editable = ('description',)
    search_fields = ('description',)
    list_filter = ('title',)
    list_display_links = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = ()
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


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
    search_fields = ('title','text')
    list_filter = ('is_published',)
    list_display_links = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author','post','created_at',)
    list_filter = ('post','created_at',)
    search_fields = ('text',)
