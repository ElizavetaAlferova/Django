import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from blog.models import Category, Comment, Post

from .forms import CommentForm, PostCreateForm, ProfileEditForm

User = get_user_model()


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


def index(request):
    template = 'blog/index.html'
    post_list = Post.objects.annotate(
        comment_count=Count('comments')).order_by(
        '-pub_date').select_related(
        'category').filter(
        is_published=True,
        pub_date__lte=datetime.datetime.now(),
        category__is_published=True)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}
    return render(request, template, context)


def post_detail(request, pk):
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.annotate(comment_count=Count('comments'))
        .order_by('-pub_date').
        filter(is_published=True,
               category__is_published=True,),
        pk=pk)
    form = CommentForm()
    comments = post.comments.select_related('author')
    context = {'post': post, 'form': form, 'comments': comments}
    return render(request, template, context)


class CommentCreateView(LoginRequiredMixin, CreateView):
    posts = None
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        self.posts = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.posts
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.posts.pk})


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'GET' and request.user != comment.author:
        return redirect('blog:post_detail', pk=post_id)
    form = CommentForm(instance=comment)
    if request.method == "POST" and request.user == comment.author:
        form = CommentForm(request.POST, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=post_id)
    context = {'form': form, 'comment': comment}
    return render(request, 'blog/comment.html', context)


def edit_post(request, post_id):
    instance = get_object_or_404(Post, id=post_id)
    if request.user != instance.author:
        return redirect('blog:post_detail', pk=post_id)
    form = PostCreateForm(request.POST or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(request, 'blog/comment.html')


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(
            is_published=True),
        slug=category_slug)
    post_list = Post.objects.annotate(
        comment_count=Count('comments')).select_related(
        'category', 'location', 'author').filter(
        category__slug=category_slug,
        is_published=True,
        pub_date__lte=datetime.datetime.now()).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj, 'category': category}
    return render(request, template, context)


def profile(request, username):
    template = 'blog/profile.html'
    profile = get_object_or_404(User, username=username)
    author = profile.id
    page_obj = Post.objects.filter(author=author).order_by('-pub_date')
    paginator = Paginator(page_obj, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post = Post.objects.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date').filter(
        is_published=True,
        category__is_published=True, )
    context = {'profile': profile, 'page_obj': page_obj, 'post': post}
    return render(request, template, context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'blog/user.html', {'form': form})


@login_required
def delete_post(request, post_id):
    instance = get_object_or_404(Post, id=post_id, author=request.user)
    form = PostCreateForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(request, 'blog/create.html', context)
