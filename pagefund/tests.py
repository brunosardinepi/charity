import django
import os

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core import mail
from django.db import models
from django.test import Client, RequestFactory, TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.timezone import now

from allauth.account.auth_backends import AuthenticationBackend
from allauth.account.forms import BaseSignupForm
from allauth.account import app_settings
from allauth.utils import get_user_model, get_username_max_length

from . import views
from campaign.models import Campaign
from invitations.models import GeneralInvitation
from page.models import Page


class HomeTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.test',
            password='testpassword',
        )
        self.user.userprofile.first_name = 'John'
        self.user.userprofile.last_name = 'Doe'
        self.user.userprofile.zipcode = '88888'
        self.user.userprofile.save()

        self.user2 = User.objects.create_user(
            username='anotherguy',
            email='another@guy.me',
            password='imthatguy',
        )

        self.page = Page.objects.create(name="Buffalo", donation_money=600, is_sponsored=True)
        self.page2 = Page.objects.create(name="Antelope", donation_money=100, is_sponsored=False)

        self.page.subscribers.add(self.user.userprofile)

        self.campaign = Campaign.objects.create(name="Blue", page=self.page, donation_money=50)
        self.campaign2 = Campaign.objects.create(name="Green", page=self.page, donation_money=900)
        self.campaign3 = Campaign.objects.create(name="Yellow", page=self.page, donation_money=500)
        self.campaign4 = Campaign.objects.create(name="Red", page=self.page2, donation_money=20)


    def test_home_logged_out(self):
        response = self.client.get('/')

        page_donations = self.page.donation_money + self.page2.donation_money
        campaign_donations = self.campaign.donation_money + self.campaign2.donation_money + self.campaign3.donation_money + self.campaign4.donation_money
        donations = page_donations + campaign_donations

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, donations, status_code=200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertNotContains(response, self.page2.name, status_code=200)
        self.assertNotContains(response, '/invite/', status_code=200)

    def test_home_logged_in(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/')

        page = self.user.userprofile.subscribers.get(id=self.page.pk)
        campaigns = page.campaigns.all()

        self.assertEqual(response.status_code, 200)
        for c in campaigns:
            if c.is_active == True:
                self.assertContains(response, c.name, status_code=200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertNotContains(response, self.page2.name, status_code=200)
        self.assertContains(response, self.user.userprofile.first_name, status_code=200)
        self.assertContains(response, self.user.userprofile.last_name, status_code=200)
        self.assertContains(response, '/invite/', status_code=200)

    def test_invite_logged_out(self):
        response = self.client.get('/invite/')

        self.assertRedirects(response, '/accounts/login/?next=/invite/', 302, 200)

    def test_invite_logged_in(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/invite/')

        self.assertEqual(response.status_code, 200)
        response = self.client.post('/invite/', {'email': 'my@best.friend'})
        self.assertRedirects(response, '/', 302, 200)
        self.client.logout()
        invitation = GeneralInvitation.objects.get(invite_to='my@best.friend')
        response = self.client.get('/invite/accept/%s/%s/' % (invitation.pk, invitation.key))
        self.assertRedirects(response, '/accounts/signup/?next=/invite/accept/%s/%s/' % (invitation.pk, invitation.key), 302, 200)
        data = {
            'first_name': 'Bob',
            'last_name': 'Walker',
            'email': 'my@best.friend',
            'email2': 'my@best.friend',
            'state': 'IL',
            'password1': 'verybadpass',
            'password2': 'verybadpass'
        }
        response = self.client.post('/accounts/signup/?next=/invite/accept/%s/%s/' % (invitation.pk, invitation.key), data)
        self.assertRedirects(response, '/invite/accept/%s/%s/' % (invitation.pk, invitation.key), 302, 302)

        users = User.objects.all()
        user = User.objects.get(email='my@best.friend')
        self.assertIn(user, users)

        invitation = GeneralInvitation.objects.get(invite_to='my@best.friend')
        self.assertEqual(invitation.expired, True)
        self.assertEqual(invitation.accepted, True)


    def test_invite_user_exists(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/invite/', {'email': 'another@guy.me'})

        self.assertRedirects(response, '/error/invite/user-exists/', 302, 200)


class AccountTests(TestCase):
    def _create_user(self, username='john', password='doe'):
        user = get_user_model().objects.create(
            username=username,
            is_active=True)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def _create_user_and_login(self, usable_password=True):
        password = 'doe' if usable_password else False
        user = self._create_user(password=password)
        c = self.client
        c.force_login(user)
        return user

    def test_password_reset_get(self):
        resp = self.client.get(reverse('account_reset_password'))
        self.assertTemplateUsed(resp, 'password_reset.html')

    def _password_set_or_change_redirect(self, urlname, usable_password):
        self._create_user_and_login(usable_password)
        return self.client.get(reverse(urlname))

    def test_password_set_redirect(self):
        resp = self._password_set_or_change_redirect(
            'account_set_password',
            True)
        self.assertRedirects(
            resp,
            reverse('account_change_password'),
            fetch_redirect_response=False)

    def test_password_change_no_redirect(self):
        resp = self._password_set_or_change_redirect(
            'account_change_password',
            True)
        self.assertEqual(resp.status_code, 200)

    def test_password_set_no_redirect(self):
        resp = self._password_set_or_change_redirect(
            'account_set_password',
            False)
        self.assertEqual(resp.status_code, 200)

    def test_password_change_redirect(self):
        resp = self._password_set_or_change_redirect(
            'account_change_password',
            False)
        self.assertRedirects(
            resp,
            reverse('account_set_password'),
            fetch_redirect_response=False)

    def _request_new_password(self):
        user = get_user_model().objects.create(
            username='john', email='john@doe.org', is_active=True)
        user.set_password('doe')
        user.save()
        self.client.post(
            reverse('account_reset_password'),
            data={'email': 'john@doe.org'})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['john@doe.org'])
        return user

    def _logout_view(self, method):
        c = Client()
        user = get_user_model().objects.create(username='john', is_active=True)
        user.set_password('doe')
        user.save()
        c = Client()
        c.login(username='john', password='doe')
        return c, getattr(c, method)(reverse('account_logout'))

    @override_settings(ACCOUNT_LOGOUT_ON_GET=True)
    def test_logout_view_on_get(self):
        c, resp = self._logout_view('get')
        self.assertTemplateUsed(resp, 'account/messages/logged_out.txt')

    @override_settings(ACCOUNT_LOGOUT_ON_GET=False)
    def test_logout_view_on_post(self):
        c, resp = self._logout_view('get')
        self.assertTemplateUsed(
            resp,
            'account/logout.%s' % app_settings.TEMPLATE_EXTENSION)
        resp = c.post(reverse('account_logout'))
        self.assertTemplateUsed(resp, 'account/messages/logged_out.txt')

    @override_settings(ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS=False)
    def test_account_authenticated_login_redirects_is_false(self):
        self._create_user_and_login()
        resp = self.client.get(reverse('account_login'))
        self.assertEqual(resp.status_code, 200)

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 9,
            }
        }])
    def test_django_password_validation(self):
        if django.VERSION < (1, 9, ):
            return
        resp = self.client.post(
            reverse('account_signup'),
            {'username': 'johndoe',
             'email': 'john@doe.com',
             'password1': 'johndoe',
             'password2': 'johndoe'})
        self.assertFormError(resp, 'form', None, [])
        self.assertFormError(
            resp,
            'form',
            'password1',
            ['This password is too short.'
             ' It must contain at least 9 characters.'])


class BaseSignupFormTests(TestCase):
    @override_settings(ACCOUNT_USERNAME_REQUIRED=True)
    def test_username_maxlength(self):
        data = {
            'username': 'username',
            'email': 'user@example.com',
        }
        form = BaseSignupForm(data, email_required=True)
        max_length = get_username_max_length()
        field = form.fields['username']
        self.assertEqual(field.max_length, max_length)
        widget = field.widget
        self.assertEqual(widget.attrs.get('maxlength'), str(max_length))


class AuthenticationBackendTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create(
            is_active=True,
            email='john@doe.com',
            username='john')
        user.set_password(user.username)
        user.save()
        self.user = user

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME)  # noqa
    def test_auth_by_username(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                username=user.username,
                password=user.username).pk,
            user.pk)
        self.assertEqual(
            backend.authenticate(
                username=user.email,
                password=user.username),
            None)

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.EMAIL)  # noqa
    def test_auth_by_email(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                username=user.email,
                password=user.username).pk,
            user.pk)
        self.assertEqual(
            backend.authenticate(
                username=user.username,
                password=user.username),
            None)

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME_EMAIL)  # noqa
    def test_auth_by_username_or_email(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                username=user.email,
                password=user.username).pk,
            user.pk)
        self.assertEqual(
            backend.authenticate(
                username=user.username,
                password=user.username).pk,
            user.pk)


class MailServerTest(TestCase):
    def test_mail_server_ping(self):
        host = "10.132.5.139"
        response = os.system("ping -c 1 " + host)

        self.assertEqual(response, 0)
