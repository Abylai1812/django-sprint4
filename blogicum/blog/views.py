from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404,redirect, render
from django.utils import timezone as tz

from blog.models import Post, Category,PostCreate
from .forms import PostForm


def get_filter_posts(posts=Post.objects.all()):
    return posts.filter(
        is_published=True,
        pub_date__lt=tz.now(),
        category__is_published=True)


def index(request):
    template_name = 'blog/index.html'
    posts = get_filter_posts()
    paginator = Paginator(posts,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}

    return render(request, template_name, context)


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


def create_post(request,pk=None):
    if pk is not None:
        instance = get_object_or_404(PostCreate,pk=pk)
    else:
        instance=None

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=instance)
    
    context = {'form': form}
    if form.is_valid():
        form.save()
    return render(request,'blog/create.html',context)


def delete_post(request,pk):
    instance = get_object_or_404(PostCreate,pk=pk)
    form = PostForm(instance=instance)
    context = {'form':form}

    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(request,'blog/create.html',context)
