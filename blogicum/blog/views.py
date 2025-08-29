from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone as tz
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.http import Http404

from blog.constans import PAGINATE_BY
from blog.forms import CommentForm, PostForm, UserForm
from blog.mixins import AuthorRequiredMixin
from blog.models import Category, Comment, Post
from blog.service import get_filter_posts, get_paginator

User = get_user_model()


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return get_filter_posts()


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'category', 'location'),
        pk=post_id
    )

    if not (
        (post.is_published
            and post.pub_date < tz.now()
            and post.category.is_published)
        or (request.user.is_authenticated
            and post.author == request.user)
    ):

        raise Http404(f"Пост с id={post_id} не найден или недоступен.")

    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': post.comments.select_related('author')
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )

    posts = get_filter_posts(category.posts.all())
    page_obj = get_paginator(request, posts, PAGINATE_BY)

    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template_name, context)


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(
    LoginRequiredMixin,
    AuthorRequiredMixin,
    PostMixin,
    UpdateView,
):
    pk_url_kwarg = 'post_id'

    def get_redirect_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.get_object().pk},
        )


class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_redirect_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.get_object().pk}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context


def user_profile(request, username):
    profile = get_object_or_404(User, username=username)

    posts = profile.posts.all()

    if request.user != profile:
        posts = get_filter_posts(posts)

    posts = posts.select_related('category', 'location').annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    page_obj = get_paginator(request, posts)

    context = {
        'profile': profile,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        post = get_object_or_404(
            get_filter_posts(Post.objects.all()),
            pk=self.kwargs['post_id']
        )

        if post.author == self.request.user or post.is_published:
            comment = form.save(commit=False)
            comment.author = self.request.user
            comment.post = post
            comment.save()
            return super().form_valid(form)

        raise Http404(f"Пост с id={post.pk} недоступен для комментирования.")

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_redirect_url(self):
        comment = self.get_object()
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': comment.post.pk}
        )


class CommentDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_redirect_url(self):
        comment = self.get_object()
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': comment.post.pk}
        )

    def get_success_url(self):
        comment = self.get_object()
        return reverse('blog:post_detail', kwargs={'post_id': comment.post.pk})
