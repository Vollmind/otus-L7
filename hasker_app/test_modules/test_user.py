import base64

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client

# Create your tests here.
from django.urls import reverse
from django.utils.http import urlencode

from hasker_app.models import UserReq


class TestUser(TestCase):
    login_data = {'username': 'test_1', 'password': 'test_password', 'next': '/'}
    wrong_login_data = {'username': 'test_1', 'password': 'test_password1', 'next': '/'}
    image_content = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAUA" +
        "AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO" +
        "9TXL0Y4OHwAAAABJRU5ErkJggg=="
    )

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

    def test_user_login(self):
        c = Client()

        response = c.post(
            reverse('login'),
            self.login_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('question_list'))

    def test_user_login_wrong(self):
        c = Client()
        response = c.post(
            reverse('login'),
            self.wrong_login_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password.')

    def test_user_get_edit_info(self):
        c = Client()
        c.post(reverse('login'), self.login_data)
        response = c.get(reverse('edit_account'))
        self.assertEqual(response.status_code, 200)
        form = response.context['form'].initial
        self.assertEqual(form['email'], 'test_email@email.email')
        self.assertEqual(form['avatar'].url, '/static/hasker_app/default_avatar.jpg')

    def test_user_get_edit_info_no_user(self):
        c = Client()
        response = c.get(reverse('edit_account'))
        self.assertEqual(response.status_code, 403)

    def test_user_edit_email(self):
        c = Client()
        c.post(reverse('login'), self.login_data)
        response = c.post(reverse('edit_account'), {'email': 'new_test_mail@mail.mail'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, 'edit_account')
        user = User.objects.first()
        self.assertEqual(user.email, 'new_test_mail@mail.mail')

    def test_user_edit_avatar(self):
        c = Client()
        c.post(reverse('login'), self.login_data)
        image = SimpleUploadedFile("file.png", self.image_content, content_type="image/pnd")
        response = c.post(reverse('edit_account'), {'avatar': image})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, 'edit_account')
        user = UserReq.objects.first()
        self.assertNotEqual(user.avatar.url, '/static/hasker_app/default_avatar.jpg')

    def test_user_logout(self):
        c = Client()
        c.post(reverse('login'), self.login_data)
        # After login - edit_account will return 403 (previous ests)
        response = c.get(reverse('edit_account'))
        self.assertEqual(response.status_code, 200)

        response = c.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        # After logout - edit_account will return 403 (previous tests)
        response = c.get(reverse('edit_account'))
        self.assertEqual(response.status_code, 403)

    def test_user_get_register_page(self):
        c = Client()
        response = c.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, 'register')

    def test_user_register(self):
        c = Client()
        image = SimpleUploadedFile("file.png", self.image_content, content_type="image/pnd")
        register_data = {
            'username': 'test_register',
            'first_name': 'test_register_name',
            'email': 'mail@mail.mail',
            'avatar': image,
            'password1': 'zaXScdVF123',
            'password2': 'zaXScdVF123'
        }
        response = c.post(reverse('register'), register_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        user = User.objects.get(username='test_register')
        self.assertEqual(user.first_name, 'test_register_name')
        self.assertEqual(user.email, 'mail@mail.mail')
        self.assert_(user.user_req.avatar.url.startswith('/media/file'))
        c.post(reverse('login'), {'username': 'test_register', 'password': 'zaXScdVF123'})
        self.assertEqual(response.status_code, 302)

    def test_user_register_no_avatar(self):
        c = Client()
        register_data = {
            'username': 'test_register',
            'first_name': 'test_register_name',
            'email': 'mail@mail.mail',
            'password1': 'zaXScdVF123',
            'password2': 'zaXScdVF123'
        }
        response = c.post(reverse('register'), register_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        user = User.objects.get(username='test_register')
        self.assert_(user.user_req.avatar.url.startswith('/static/hasker_app/default_avatar.jpg'))
        c.post(reverse('login'), {'username': 'test_register', 'password': 'zaXScdVF123'})
        self.assertEqual(response.status_code, 302)

    def test_user_register_easy_password(self):
        c = Client()
        register_data = {
            'username': 'test_register',
            'first_name': 'test_register_name',
            'email': 'mail@mail.mail',
            'password1': '123',
            'password2': '123'
        }
        response = c.post(reverse('register'), register_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'too similar to your other personal information')
        self.assertContains(response, 'This password is too short')
        self.assertContains(response, 'This password is entirely numeric')
        user = User.objects.filter(username='test_register').all()
        self.assertEqual(len(user), 0)

    def test_user_register_already_exists(self):
        c = Client()
        register_data = {
            'username': 'test_1',
            'first_name': 'test_register_name',
            'email': 'mail@mail.mail',
            'password1': 'zaXScdvf123',
            'password2': 'zaXScdvf123'
        }
        response = c.post(reverse('register'), register_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists.')
        user = User.objects.filter(username='test_register').all()
        self.assertEqual(len(user), 0)
