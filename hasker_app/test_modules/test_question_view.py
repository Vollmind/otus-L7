from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.test import Client, TestCase
from django.urls import reverse

from hasker_app.models import UserReq, Tag, Question, UserRate


class TestQuestionView(TestCase):
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
        self.question_id = question.id

    def test_question_view(self):
        c = Client()
        c.login(**self.login_data)
        response = c.get(reverse('question_detail', args=[self.question_id]))
        self.assertEqual(response.status_code, 200)

    def test_question_anon_view(self):
        c = Client()
        response = c.get(reverse('question_detail', args=[self.question_id]))
        self.assertEqual(response.status_code, 200)

    def test_question_vote_up(self):
        c = Client()
        c.login(**self.login_data)
        response = c.get(reverse('vote_up', args=['question', self.question_id]))
        self.assertEqual(response.status_code, 302)
        question = (
            Question.objects
            .annotate(rate=Coalesce(Sum('rates__rate'), 0))
            .get(pk=self.question_id)
        )
        self.assertEqual(question.rate, 1)
        self.assertEqual(UserRate.objects.all()[0].user.user.username, 'test_1')
        self.assertEqual(UserRate.objects.all()[0].rate, 1)

    def test_question_vote_up_twice(self):
        c = Client()
        c.login(**self.login_data)
        response = c.get(reverse('vote_up', args=['question', self.question_id]))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('vote_up', args=['question', self.question_id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(UserRate.objects.all()), 1)
        self.assertEqual(UserRate.objects.all()[0].user.user.username, 'test_1')
        self.assertEqual(UserRate.objects.all()[0].rate, 1)

    def test_question_anon_vote_up(self):
        c = Client()
        response = c.get(reverse('vote_up', args=['question', self.question_id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(UserRate.objects.all()), 0)

    def test_question_vote_down(self):
        c = Client()
        c.login(**self.login_data)
        response = c.get(reverse('vote_down', args=['question', self.question_id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(UserRate.objects.all()[0].user.user.username, 'test_1')
        self.assertEqual(UserRate.objects.all()[0].rate, -1)

    def test_question_vote_down_twice(self):
        c = Client()
        c.login(**self.login_data)
        response = c.get(reverse('vote_down', args=['question', self.question_id]))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('vote_down', args=['question', self.question_id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(UserRate.objects.all()), 1)
        self.assertEqual(UserRate.objects.all()[0].user.user.username, 'test_1')
        self.assertEqual(UserRate.objects.all()[0].rate, -1)

    def test_question_anon_vote_down(self):
        c = Client()
        response = c.get(reverse('vote_up', args=['question', self.question_id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(UserRate.objects.all()), 0)

    def test_question_vote_up_down(self):
        c = Client()
        c.login(**self.login_data)
        response = c.get(reverse('vote_up', args=['question', self.question_id]))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('vote_down', args=['question', self.question_id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(UserRate.objects.all()), 1)
        self.assertEqual(UserRate.objects.all()[0].rate, 0)
