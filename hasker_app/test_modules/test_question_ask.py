from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from hasker_app.models import UserReq, Question, Tag


class TestQuestionAsk(TestCase):
    login_data = {'username': 'test_1', 'password': 'test_password', 'next': '/'}

    def setUp(self) -> None:
        user = User.objects.create_user(
            username='test_1',
            first_name='test_first_name_1',
            email='test_email@email.email',
            password='test_password'
        )
        UserReq.objects.create(
            user=user,
            avatar='../static/hasker_app/default_avatar.jpg'
        )
        tag = Tag.objects.create(
            name='test_tag'
        )
        question = Question.objects.create(
            label='test_question',
            text='test text',
            user=user.user_req
        )
        question.tags.add(tag)

    def test_question_has_button(self):
        c = Client()
        c.login(**self.login_data)
        response = c.get(reverse('question_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ask question</button>')

    def test_question_anon_havenot_button(self):
        c = Client()
        response = c.get(reverse('question_list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Ask question</button>')

    def test_question_anon_cannot_ask(self):
        c = Client()
        response = c.get(reverse('ask_question'))
        self.assertEqual(response.status_code, 403)

    def test_question_can_ask(self):
        c = Client()
        c.login(**self.login_data)
        response = c.get(reverse('ask_question'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['tags_list'], ['test_tag'])

    def test_question_ask(self):
        c = Client()
        c.login(**self.login_data)
        question_data = {
            'label': 'test question creation',
            'text': 'test text',
            'tags': 'test_tag'
        }
        response = c.post(reverse('ask_question'), question_data)
        self.assertEqual(response.status_code, 302)
        question = Question.objects.get(label='test question creation')
        self.assertEqual(response.url + '/', reverse('question_detail', args=[question.id]))
        self.assertEqual(question.text, 'test text')
        self.assertEqual(len(question.tags.all()), 1)
        self.assertEqual(len(Tag.objects.all()), 1)
        self.assertEqual(question.tags.all()[0].name, 'test_tag')

    def test_question_ask_no_label(self):
        c = Client()
        c.login(**self.login_data)
        question_data = {
            'label': '',
            'text': 'test text',
            'tags': 'test_tag'
        }
        response = c.post(reverse('ask_question'), question_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertEqual(len(Question.objects.filter(label='')), 0)

    def test_question_ask_no_text(self):
        c = Client()
        c.login(**self.login_data)
        question_data = {
            'label': 'test question creation',
            'text': '',
            'tags': 'test_tag'
        }
        response = c.post(reverse('ask_question'), question_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertEqual(len(Question.objects.filter(label='test question creation')), 0)

    def test_question_ask_no_tag(self):
        c = Client()
        c.login(**self.login_data)
        question_data = {
            'label': 'test question creation',
            'text': 'text',
            'tags': ''
        }
        response = c.post(reverse('ask_question'), question_data)
        self.assertEqual(response.status_code, 302)
        question = Question.objects.get(label='test question creation')
        self.assertEqual(len(question.tags.all()), 0)

    def test_question_ask_new_tag(self):
        c = Client()
        c.login(**self.login_data)
        question_data = {
            'label': 'test question creation',
            'text': 'text',
            'tags': 'new_tag'
        }
        response = c.post(reverse('ask_question'), question_data)
        self.assertEqual(response.status_code, 302)
        question = Question.objects.get(label='test question creation')
        self.assertEqual(len(question.tags.all()), 1)
        self.assertEqual(Tag.objects.get(name='new_tag'), question.tags.all()[0])

    def test_question_ask_two_tag(self):
        c = Client()
        c.login(**self.login_data)
        question_data = {
            'label': 'test question creation',
            'text': 'text',
            'tags': 'new_tag, test_tag'
        }
        response = c.post(reverse('ask_question'), question_data)
        self.assertEqual(response.status_code, 302)
        question = Question.objects.get(label='test question creation')
        self.assertEqual(len(question.tags.all()), 2)

    def test_question_anon_ask(self):
        c = Client()
        question_data = {
            'label': 'test question creation',
            'text': 'test text',
            'tags': 'test_tag'
        }
        response = c.post(reverse('ask_question'), question_data)
        self.assertEqual(response.status_code, 403)
