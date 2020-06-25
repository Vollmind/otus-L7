from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.test import Client, TestCase
from django.urls import reverse

from hasker_app.models import UserReq, Tag, Question, UserRate


class TestSearch(TestCase):
    login_data = {'username': 'test_1', 'password': 'test_password', 'next': '/'}
    maxDiff = None

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
        tag2 = Tag.objects.create(
            name='test_tag_2'
        )
        for x in range(20):
            question = Question.objects.create(
                label=f'test_question_{x}',
                text=f'test text {x-1}',
                user=user.user_req
            )
            question.tags.add(tag)

            if x >= 15:
                question.tags.add(tag2)
            if x < 5:
                UserRate.objects.create(
                    user=user.user_req,
                    question=question,
                    rate=x
                )

    def test_get_list(self):
        c = Client()
        response = c.get(reverse('question_list'))
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.context['object_list'][0:5],
            list(
                Question
                .objects
                .annotate(rate=Coalesce(Sum('rates__rate'), 0))
                .order_by('-rate', '-created_date')[0:5]
            )
        )

    def test_get_list_page_2(self):
        c = Client()
        response = c.get(reverse('question_list') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.context['object_list'][0:5],
            list(
                Question
                .objects
                .annotate(rate=Coalesce(Sum('rates__rate'), 0))
                .order_by('-rate', '-created_date')[10:15]
            )
        )

    def test_get_list_page_5(self):
        c = Client()
        response = c.get(reverse('question_list') + '?page=5')
        self.assertEqual(response.status_code, 404)

    def test_get_list_date_ordered(self):
        c = Client()
        response = c.get(reverse('question_list_date_ordered'))
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.context['object_list'][0:5],
            list(
                Question
                .objects
                .annotate(rate=Coalesce(Sum('rates__rate'), 0))
                .order_by('-created_date', '-rate')[0:5]
            )
        )

    def test_get_list_search_label(self):
        c = Client()
        response = c.get(reverse('question_search') + '?search_str=question_1')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.context['object_list'][0:5],
            list(
                Question
                .objects
                .annotate(rate=Coalesce(Sum('rates__rate'), 0))
                .filter(label__contains='question_1')
                .order_by('-rate', '-created_date')[0:5]
            )
        )

    def test_get_list_search_text(self):
        c = Client()
        response = c.get(reverse('question_search') + '?search_str=text 1')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.context['object_list'][0:5],
            list(
                Question
                .objects
                .annotate(rate=Coalesce(Sum('rates__rate'), 0))
                .filter(text__contains='text 1')
                .order_by('-rate', '-created_date')[0:5]
            )
        )

    def test_get_list_search_text_and_label(self):
        c = Client()
        response = c.get(reverse('question_search') + '?search_str=15')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.context['object_list'][0:5],
            list(
                Question
                .objects
                .annotate(rate=Coalesce(Sum('rates__rate'), 0))
                .filter(Q(text='test text 15') | Q(label='test_question_15'))
                .order_by('-rate', '-created_date')[0:5]
            )
        )

    def test_get_list_search_tag(self):
        c = Client()
        response = c.get(reverse('question_search') + '?search_tag=test_tag_2')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.context['object_list'][0:5],
            list(
                Question
                .objects
                .annotate(rate=Coalesce(Sum('rates__rate'), 0))
                .filter(tags__name='test_tag_2')
                .order_by('-rate', '-created_date')[0:5]
            )
        )