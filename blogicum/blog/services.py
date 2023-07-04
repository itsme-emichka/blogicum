from django.db.models.query import QuerySet
from django.utils import timezone
from django.db import models

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


def get_category_posts(slug: str) -> QuerySet:
    return get_posts().filter(category__slug=slug, category__is_published=True)


def get_profile_posts(for_user: bool, username: str) -> QuerySet:
    if for_user:
        posts = Post.objects.select_related('author').filter(
            author__username=username
        )
    else:
        posts = (
            get_posts()
            .select_related('author')
            .filter(author__username=username)
        )
    return posts


def get_object(
    model: type[models.Model], pk: int, related: tuple[str]
) -> type[models.Model]:
    return model.objects.select_related(*related).get(pk=pk)


def get_author(model: type[models.Model], pk: int) -> str:
    author = model.objects.select_related('author').get(id=pk).author.username
    return author
