from django.db.models.query import QuerySet
from django.utils import timezone
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import redirect
from typing import Any
from django.urls import reverse

from blog.models import Post, Comment


POSTS_ON_PAGE: int = 10


def get_posts() -> QuerySet:
    return Post.objects.select_related(
        'location',
        'category',
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )


def get_posts_planned(username: str) -> QuerySet:
    return Post.objects.select_related(
        'author',
        'category',
    ).filter(
        is_published=True,
        author__username=username,
        pub_date__gte=timezone.now(),
    )


class PostDispatchMixin:
    model = Post

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        try:
            if (
                self.request.user.username
                == Post.objects.select_related('author')
                .get(id=self.kwargs['pk'])
                .author.username
            ):
                return super().dispatch(request, *args, **kwargs)
            else:
                return redirect('blog:post_detail', pk=self.kwargs['pk'])
        except Exception:
            raise Http404


class CommentDispatchUrlMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        try:
            if (
                self.request.user.username
                == Comment.objects.select_related('author')
                .get(id=self.kwargs['comment_id'])
                .author.username
            ):
                return super().dispatch(request, *args, **kwargs)
            else:
                return redirect('blog:post_detail', pk=self.kwargs['pk'])
        except Exception:
            raise Http404('Такого комментария не существует')

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class PostListMixin:
    model = Post
    paginate_by = POSTS_ON_PAGE


class PostRedirectMixin:
    def get_success_url(self) -> str:
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )
