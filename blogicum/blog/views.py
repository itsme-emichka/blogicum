from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)
from django.http import HttpRequest, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
)
from django.utils import timezone

from blog.models import Post, User, Category
from blog.forms import PostForm, UserForm, CommentForm
from blog.utils import (
    get_posts,
    PostDispatchMixin,
    CommentDispatchUrlMixin,
    PostListMixin,
    PostRedirectMixin,
)


class PostCreateView(LoginRequiredMixin, PostRedirectMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        try:
            obj = Post.objects.select_related('author').get(pk=kwargs['pk'])
            print(obj.author.username)
            print(self.request.user.username)
            if (
                not obj.is_published or obj.pub_date > timezone.now()
            ) and obj.author.username != self.request.user.username:
                raise Http404('Поста с таким id не существует')
            else:
                return super().dispatch(request, *args, **kwargs)
        except:
            raise Http404('Поста с таким id не существует')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostUpdateView(LoginRequiredMixin, PostDispatchMixin, UpdateView):
    form_class = PostForm


class PostDeleteView(
    LoginRequiredMixin, PostDispatchMixin, PostRedirectMixin, DeleteView
):
    template_name = 'blog/post_form.html'


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


class CommentUpdateView(
    LoginRequiredMixin, CommentDispatchUrlMixin, UpdateView
):
    form_class = CommentForm


class CommentDeleteView(
    LoginRequiredMixin, CommentDispatchUrlMixin, DeleteView
):
    pass


class PostListView(PostListMixin, ListView):
    def get_queryset(self) -> QuerySet[Any]:
        return get_posts()


class CategoryListView(PostListMixin, ListView):
    template_name = 'blog/category.html'

    def get_queryset(self) -> QuerySet[Any]:
        return get_posts().filter(
            category__slug=self.kwargs['category_slug'],
            category__is_published=True,
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return context


class ProfileListView(PostListMixin, ListView):
    template_name = 'blog/profile.html'

    def get_queryset(self) -> QuerySet[Any]:
        if self.request.user.username == self.kwargs['username']:
            queryset = Post.objects.select_related('author').filter(
                author__username=self.kwargs['username']
            )
        else:
            queryset = (
                get_posts()
                .select_related('author')
                .filter(author__username=self.kwargs['username'])
            )
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return context


@login_required
def profile_edit(request: HttpRequest) -> HttpResponse:
    instance = get_object_or_404(User, username=request.user)
    form = UserForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
    context = {'form': form}
    return render(request, 'blog/user.html', context)
