from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse, Http404
from django.shortcuts import *
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView

from boards.form import NewTopicForm, PostForm
from boards.models import Board, Topic, Post


# Create your views here.
class BoardListHome(ListView):
    model = Board
    template_name = "home.html"
    context_object_name = "boards"


def home(request):
    boards = Board.objects.all()
    # response_html = "<br>".join(board.name for board in boards)
    return render(request, "home.html", {'boards': boards})


def board_topic(request, pk):
    # try:
    board = get_object_or_404(Board, id=pk)
    topics = board.topics.order_by("-last_update").annotate(replies=Count('posts') - 1)
    # except Board.DoesNotExist:
    #     raise Http404
    return render(request, "topics.html", {'board': board, 'topics': topics})


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('topic_posts', pk=pk, topic_id=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board_id=pk, pk=topic_pk)
    views = topic.views
    views += 1
    topic.save()
    return render(request, "topic_posts.html", {'topic': topic})


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board_id=pk, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_update = timezone.now()
            topic.save()
        topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
        topic_post_url = '{url}?page={page}#{id}'.format(
            url=topic_url,
            id=post.pk,
            page=topic.get_page_count()
        )
        return redirect(topic_post_url)
    else:
        form = PostForm(request.POST)
    return render(request, "reply_topic.html", {'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ["message", ]
    template_name = "edit_post.html"
    pk_url_kwarg = "post_pk"
    context_object_name = "post"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect("topic_posts", pk=post.topic.board.id, topic_pk=post.topic.id)


class TopicListView(ListView):
    model = Topic
    context_object_name = "topic"
    template_name = "topics.html"
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        query_set = self.board.topics.order_by("-last_update").annotate(replies=Count("posts") - 1)
        return query_set


class PostListView(ListView):
    model = Post
    context_object_name = "posts"
    template_name = "topic_posts.html"
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True

        kwargs['topic'] = self.topic
        return super().get_context_data(kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board_id=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        query_set = self.topic.posts.order_by('created_at')
        return query_set
