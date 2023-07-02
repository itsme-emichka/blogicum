from django.db.models.query import QuerySet
from django.utils import timezone
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from typing import Any

from blog.models import Post


def get_posts() -> QuerySet:
    return Post.objects.select_related(
        'location',
        'category',
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )


class PostDispatchMixin:
    model = Post

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.request.user.username == Post.objects.select_related('author').get(id=self.kwargs['pk']).author.username:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])
