from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView

from blog.models import Post, User, Comment, Category
from blog.forms import PostForm, UserForm, CommentForm
from blog.utils import get_posts


POSTS_ON_PAGE: int = 10


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm
        context['comments'] = self.object.comments.select_related('author')
        print(context)
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.request.user.username == Post.objects.select_related('author').get(id=self.kwargs['pk']).author.username:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_form.html'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.request.user.username == Post.objects.select_related('author').get(id=self.kwargs['pk']).author.username:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])

    def get_success_url(self) -> str:
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


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


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.request.user.username == Comment.objects.select_related('author').get(id=self.kwargs['comment_id']).author.username:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class PostListView(ListView):
    model = Post
    ordering = '-pub_date'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self) -> QuerySet[Any]:
        return get_posts()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        print(super().get_context_data(**kwargs))
        return super().get_context_data(**kwargs)


class CategoryListView(ListView):
    model = Post
    ordering = '-pub_date'
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/category.html'

    def get_queryset(self) -> QuerySet[Any]:
        query = get_list_or_404(get_posts(), category__slug=self.kwargs['category_slug'],)
        return query

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, slug=self.kwargs['category_slug'],)
        print(self.get_queryset())
        return context


class ProfileListView(ListView):
    model = Post
    ordering = '-pub_date'
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/profile.html'

    def get_queryset(self) -> QuerySet[Any]:
        if self.request.user.username == self.kwargs['username']:
            queryset = (
                Post.objects.select_related('author')
                .filter(author__username=self.kwargs['username'])
            )
        else:
            queryset = (
                get_posts().select_related('author')
                .filter(author__username=self.kwargs['username'])
            )
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(User, username=self.kwargs['username'])
        return context


@login_required
def profile_edit(request: HttpRequest) -> HttpResponse:
    instance = get_object_or_404(User, username=request.user)
    form = UserForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
    context = {'form': form}
    return render(request, 'blog/user.html', context)
