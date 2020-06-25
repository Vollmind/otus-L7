from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.test import TestCase, Client
from django.urls import reverse

from hasker_app.models import UserReq, Question, Tag, Answer, UserRate


class TestAnswer(TestCase):
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
        question = Question.objects.create(
            label='test_question',
            text='test text',
            user=user.user_req
        )
        for x in range(20):
            answer = Answer.objects.create(
                text='',
                user=user.user_req,
                question=question,
                confirmed=(x == 5)
            )
            if x > 15:
                UserRate.objects.create(
                    user=user.user_req,
                    answer=answer,
                    rate=x
                )
        self.question_id = question.id

    def test_get_list(self):
        c = Client()
        c.login(**self.login_data)
        response = c.get(reverse('question_detail', args=[self.question_id]))
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.context['object_list'][0:10],
            list(
                Answer
                .objects
                .annotate(rate=Coalesce(Sum('rates__rate'), 0))
                .filter(question_id=self.question_id)
                .order_by('-confirmed', '-rate', '-created_date')[0:10]
            )
        )

    def test_check_add_form(self):
        c = Client()
        c.login(**self.login_data)
        response = c.get(reverse('question_detail', args=[self.question_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your answer:')

    def test_check_add_form_anon(self):
        c = Client()
        response = c.get(reverse('question_detail', args=[self.question_id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Your answer:')

    def test_check_send_answer_anon(self):
        c = Client()
        response = c.post(reverse('post_answer', args=[self.question_id]))
        self.assertEqual(response.status_code, 403)

    def test_check_send_answer_nonexists_question(self):
        c = Client()
        c.login(**self.login_data)
        response = c.post(reverse('post_answer', args=[0]))
        self.assertEqual(response.status_code, 404)

    def test_check_send_answer(self):
        c = Client()
        c.login(**self.login_data)
        response = c.post(reverse('post_answer', args=[self.question_id]), {'text': 'answer'})
        self.assertEqual(response.status_code, 302)
        answer = Answer.objects.filter(text='answer').get()
        self.assertEqual(answer.question.id, self.question_id)
        self.assertEqual(answer.user.user.username, 'test_1')
