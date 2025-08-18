from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404,redirect, render
from django.utils import timezone as tz
from django.views.generic import CreateView,ListView,UpdateView,DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin

from blog.models import Post, Category
from .forms import PostForm,CommentForm


User = get_user_model()


def get_filter_posts(posts=Post.objects.all()):
    return posts.filter(
        is_published=True,
        pub_date__lt=tz.now(),
        category__is_published=True)


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return get_filter_posts()


def post_detail(request, post_id):
    template_name = 'blog/detail.html'

    post = get_object_or_404(
        get_filter_posts(),
        pk=post_id
    )

    context = {'post': post}
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(
            is_published=True
        ),
        slug=category_slug
    )
    posts = get_filter_posts(Post.objects.filter(category=category))
    paginator = Paginator(posts,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, template_name, context)

class PostMixin:
    model = Post
    exclude = ('author',)

class PostFormMixin:
    form_class = PostForm
    template_name = 'blog/create.html'

class OnlyAuthorMixin():
    
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostCreateView(PostMixin,PostFormMixin,LoginRequiredMixin,CreateView,OnlyAuthorMixin):
    
    def form_valid(self,form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(PostMixin,PostFormMixin,LoginRequiredMixin,UpdateView,OnlyAuthorMixin):
    pass

class PostDeleteView(PostMixin,LoginRequiredMixin,DeleteView,OnlyAuthorMixin):
    pass

def add_comment(request,pk):
    post = get_object_or_404(Post,pk=pk)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post:detail',pk=pk)

def user_profile(request,username):
    profile = get_object_or_404(User,username=username)
    context = {'profile':profile}
    return render(request,'blog/profile.html',context)