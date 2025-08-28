from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone as tz

from blog.models import Post
from blog.constans import PAGINATE_BY


def get_filter_posts(
    posts=Post.objects.all(),
    filter_published=True,
    count_comments=True
):
    """Вспомогательная функция для фильтрации постов."""
    queryset = posts

    if filter_published:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lt=tz.now(),
            category__is_published=True,
        )

    if count_comments:
        queryset = queryset.annotate(comment_count=Count('comments'))

    return queryset.select_related(
        'author',
        'category',
        'location'
    ).order_by('-pub_date')


def get_paginator(request, queryset, per_page=PAGINATE_BY):
    """Вспомогательная функция для пагинации."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
