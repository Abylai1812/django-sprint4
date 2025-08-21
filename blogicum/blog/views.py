from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone as tz
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

# Локальные импорты
from blog.models import Category, Comment, Post
from .forms import CommentForm, PostForm


User = get_user_model()


def get_filter_posts(posts=Post.objects.all()):
    return posts.filter(
        is_published=True,
        pub_date__lt=tz.now(),
        category__is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return get_filter_posts()


def post_detail(request, post_id):
    form = CommentForm()
    post = get_object_or_404(
        get_filter_posts(),
        pk=post_id
    )

    context = {
        'post': post,
        'form': form,
        'comments': Comment.objects.filter(post=post).select_related('author')
    }

    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(
            is_published=True
        ),
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


class PostMixin():
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    exclude = ('author',)


class PostCreateView(LoginRequiredMixin, CreateView, PostMixin):

    def form_valid(self, form):
        form.instance.author = self.request.user
        super().form_valid(form)
        return redirect('blog:profile', username=self.request.user.username)


class PostUpdateView(OnlyAuthorMixin, UpdateView, PostMixin):
    pk_url_kwarg = 'post_id'


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')
    exclude = ('author',)


def user_profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(
        author=profile
    ).order_by(
        '-pub_date'
    ).annotate(
        comment_count=Count('comments'))

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile,
        'username': profile.username,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


class ProfileUpdateView(OnlyAuthorMixin, UpdateView):
    model = User
    fields = ['username', 'first_name', 'last_name', 'email']
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', post_id=post_id)


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'


class CommentDeleteView(DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return self.object.get_absolute_url()
