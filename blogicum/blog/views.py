from typing import Any, Dict

from django.urls import reverse
from django.db.models.query import QuerySet
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)
from django.utils import timezone
from django.http import HttpRequest, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
)

from blog.models import Post, User, Category, Comment
from blog.forms import PostForm, UserForm, CommentForm
from blog.services import (
    get_posts,
    get_category_posts,
    get_profile_posts,
    get_author,
    get_object,
    validate_user,
)


POSTS_ON_PAGE: int = 10


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostDetailView(DetailView):
    model = Post

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        try:
            obj = get_object(
                Post,
                self.kwargs['pk'],
                ('author',),
            )
            if (
                not obj.is_published or obj.pub_date > timezone.now()
            ) and obj.author.username != self.request.user.username:
                raise Http404('Такого поста не существует')
            return super().get(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise Http404('Такого поста не существует')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm

    @validate_user
    def get(
        self, request: HttpRequest, *args: str, **kwargs: Any
    ) -> HttpResponse:
        return super().get(request, *args, **kwargs)

    @validate_user
    def post(
        self, request: HttpRequest, *args: str, **kwargs: Any
    ) -> HttpResponse:
        return super().post(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_form.html'

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )

    @validate_user
    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        return super().get(request, *args, **kwargs)

    @validate_user
    def post(
        self, request: HttpRequest, *args: str, **kwargs: Any
    ) -> HttpResponse:
        return super().post(request, *args, **kwargs)


@login_required
def comment(request: HttpRequest, pk: int):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})

    @validate_user
    def get(
        self, request: HttpRequest, *args: str, **kwargs: Any
    ) -> HttpResponse:
        return super().get(request, *args, **kwargs)

    @validate_user
    def post(
        self, request: HttpRequest, *args: str, **kwargs: Any
    ) -> HttpResponse:
        return super().post(request, *args, **kwargs)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})

    @validate_user
    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        return super().get(request, *args, **kwargs)

    @validate_user
    def post(
        self, request: HttpRequest, *args: str, **kwargs: Any
    ) -> HttpResponse:
        return super().post(request, *args, **kwargs)


class PostListView(ListView):
    model = Post
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self) -> QuerySet[Any]:
        return get_posts()


class CategoryListView(ListView):
    template_name = 'blog/category.html'
    model = Post
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self) -> QuerySet[Any]:
        return get_category_posts(self.kwargs['category_slug'])

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return context


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self) -> QuerySet[Any]:
        return get_profile_posts(
            self.request.user.username == self.kwargs['username'],
            self.kwargs['username'],
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'


@login_required
def profile_edit(request: HttpRequest) -> HttpResponse:
    instance = get_object_or_404(User, username=request.user)
    form = UserForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
    context = {'form': form}
    return render(request, 'blog/user.html', context)
