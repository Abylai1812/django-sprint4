from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
        name='category_posts'),
    path('posts/create/',views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/delete/',views.PostDeleteView.as_view(),name='delete_post'),
    path('posts/<int:post_id>/comment/',views.add_comment,name='comment'),
    path('profile/<str:username>/',views.user_profile,name='profile'),
]
