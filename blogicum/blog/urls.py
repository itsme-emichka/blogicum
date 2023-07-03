from django.urls import path, include
from django.views.generic import CreateView

from blog import views
from blog.apps import BlogConfig

app_name = BlogConfig.name

urlpatterns = [
    path(
        '',
        views.PostListView.as_view(),
        name='index',
    ),
    path(
        'posts/<int:pk>/',
        views.PostDetailView.as_view(),
        name='post_detail',
    ),
    path(
        'posts/<int:pk>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post',
    ),
    path(
        'posts/<int:pk>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post',
    ),
    path(
        'posts/<int:pk>/comment/',
        views.comment,
        name='add_comment',
    ),
    path(
        'posts/<int:pk>/edit_comment/<int:comment_id>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment',
    ),
    path(
        'posts/<int:pk>/delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment',
    ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryListView.as_view(),
        name='category_posts',
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post',
    ),
    path(
        'profile/edit/',
        views.profile_edit,
        name='edit_profile'
    ),
    path(
        'profile/<slug:username>/',
        views.ProfileListView.as_view(),
        name='profile',
    ),
]
