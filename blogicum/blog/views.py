from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone as tz
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from blog.models import Category, Comment, Post
from .forms import CommentForm, PostForm, UserForm


User = get_user_model()


def get_filter_posts(posts=Post.objects.all()):
    return (
        posts.filter(
            is_published=True,
            pub_date__lt=tz.now(),
            category__is_published=True
        )
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return get_filter_posts()


def post_detail(request, post_id):
    form = CommentForm()
    post = get_object_or_404(Post, pk=post_id)

    if not (
        post.is_published
        and post.pub_date < tz.now()
        and post.category.is_published
    ):
        if not (
            request.user.is_authenticated
            and post.author == request.user
        ):
            return render(request, 'pages/404.html', status=404)

    context = {
        'post': post,
        'form': form,
        'comments': Comment.objects.filter(
            post=post
        ).select_related('author')
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )
    posts = get_filter_posts(Post.objects.filter(category=category))
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'category': category, 'page_obj': page_obj}
    return render(request, template_name, context)


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class AuthorRequiredMixin(UserPassesTestMixin):
    """
    Ограничивает доступ к объекту только автору.
    Если пользователь не автор → редирект.
    """

    raise_exception = False
    login_url = None

    def test_func(self):
        if not self.request.user.is_authenticated:
            return True
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect(self.get_redirect_url())

    def get_redirect_url(self):
        """
        Возвращает URL для редиректа.
        В наследниках нужно переопределить.
        """
        raise NotImplementedError


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    exclude = ('author',)


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
            kwargs={'post_id': self.get_object().pk}
        )


class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')

    def get_redirect_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.get_object().pk}
        )


def user_profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = (
        Post.objects.filter(author=profile)
        .order_by('-pub_date')
        .annotate(comment_count=Count('comments'))
    )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile,
        'username': profile.username,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def test_func(self):
        obj = self.get_object()
        return obj.username == self.request.user.username

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)

    def form_valid(self, form):
        return super().form_valid(form)

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
            get_filter_posts(),
            pk=self.kwargs['post_id']
        )
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = post
        comment.save()
        return super().form_valid(form)

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
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.get_object().post_id}
        )


class CommentDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_redirect_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.get_object().post_id}
        )

    def get_success_url(self):
        comment = self.get_object()
        return reverse('blog:post_detail', kwargs={'post_id': comment.post_id})
