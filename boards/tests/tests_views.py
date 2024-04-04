from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve

from boards.form import NewTopicForm
from boards.models import Board, Topic, Post
from boards.views import home, board_topic, new_topic
from django.urls import resolve


# Create your tests here.
class homeTests(TestCase):
    def setUp(self) -> None:
        Board.objects.create(name="Django", description="this is diango description")
        url = reverse("home")
        self.response = self.client.get(url)

    def test_home(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_home_url(self):
        view = resolve("/")
        self.assertEquals(view.func, home)

    def test_url_contain(self):
        url = reverse("board_topics", kwargs={'pk': 1})
        self.assertContains(self.response, 'href="{0}"'.format(url))


class BoardTopicsTests(TestCase):
    def setUp(self) -> None:
        Board.objects.create(name='Django', description='Django board.')

    def test_board_topic_view_success_code(self):
        url = reverse("board_topics", kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_board_topic_view_fail_code(self):
        url = reverse("board_topics", kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_board_topic_view(self):
        view = resolve("/boards/1/")
        self.assertEquals(view.func, board_topic)


class NewTopicTest(TestCase):
    def setUp(self) -> None:
        Board.objects.create(name="Django", description="this is diango description")

    def test_new_topic_success(self):
        url = reverse("new_topic", kwargs={'pk': 1})
        client_get = self.client.get(url)
        self.assertEquals(client_get.status_code, 200)

    def test_new_topic_error(self):
        url = reverse("new_topic", kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_new_topic_view(self):
        view = resolve('/boards/1/new/')
        self.assertEquals(view.func, new_topic)

    def test_new_topic_view_contains_link_back_to_board_topics_view(self):
        url = reverse("new_topic", kwargs={'pk': 1})
        board_url = reverse("board_topics", kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'href="{0}"'.format(board_url))

    def test_board_topics_view_contains_navigation_links(self):
        home_url = reverse("home")
        board_topic_url = reverse("board_topics", kwargs={'pk': 1})
        new_topic_url = reverse("new_topic", kwargs={'pk': 1})

        response = self.client.get(board_topic_url)
        self.assertContains(response, 'href="{0}"'.format(home_url))
        self.assertContains(response, 'href="{0}"'.format(new_topic_url))


class newTopicTests(TestCase):
    def setUp(self) -> None:
        board = Board.objects.create(name='Django', description='Django board.')
        user = User.objects.create_user(username='john', email='john@doe.com', password='123')

    def test_crsf(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_valid_from(self):
        url = reverse("new_topic", kwargs={'pk': 1})
        data = {
            "subject": "test",
            "message": "test"
        }
        response = self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_valid_null(self):
        url = reverse("new_topic", kwargs={'pk': 1})
        data = {
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)

    def test_new_topic_invalid_post_data_empty_fields(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {
            'subject': '',
            'message': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())

    def test_new_topic_invalid_post_data(self):
        url = reverse('new_topic', kwargs={'pk': 2})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_new_topic_invalid_post_data(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)


from boards import views


class BoardTopicsTests(TestCase):

    def test_board_topics_url_resolves_board_topics_view(self):
        view = resolve('/boards/1/')
        self.assertEquals(view.func.view_class, views.TopicListView)
