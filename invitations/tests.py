from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from . import models
from . import views
from page.models import Page


class ManagerInvitationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.test',
            password='testpassword'
        )

        self.user2 = User.objects.create_user(
            username='harrypotter',
            email='harry@potter.com',
            password='imawizard',
            first_name='Harry',
            last_name='Potter'
        )

        self.user3 = User.objects.create_user(
            username='forgetful',
            email='i@forgot.it',
            password='iwillforgetthis'
        )

        self.page = Page.objects.create(
            name='Test Page',
            page_slug='testpage',
            description='This is a description for Test Page.',
            donation_count='20',
            donation_money='30',
            category='Animal'
        )

        self.page.admins.add(self.user.userprofile)

        self.invitation = models.ManagerInvitation.objects.create(
            invite_to=self.user2.email,
            invite_from=self.user,
            page=self.page,
            manager_edit=True,
            manager_delete=True,
            manager_invite=True,
            manager_image_edit=True,
            manager_view_dashboard=True,
        )

        self.invitation2 = models.GeneralInvitation.objects.create(
            invite_to="nerd@tester.yo",
            invite_from=self.user
        )

        self.forgotpasswordrequest = models.ForgotPasswordRequest.objects.create(
            email='i@forget.all',
            expired=True
        )

        self.forgotpasswordrequest2 = models.ForgotPasswordRequest.objects.create(
            email='i@am.forgetful',
            expired=False,
            completed=True
        )

    def test_invitation_exists(self):
        m_invitations = models.ManagerInvitation.objects.all()
        self.assertIn(self.invitation, m_invitations)

        g_invitations = models.GeneralInvitation.objects.all()
        self.assertIn(self.invitation2, g_invitations)

    def test_invitation_page(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.pending_invitations(request)

        self.assertEqual(response.status_code, 200)

    def test_accept_manager_invitation_logged_out(self):
        response = self.client.get('/invite/manager/accept/%s/%s/' % (self.invitation.pk, self.invitation.key))
        self.assertRedirects(response, '/accounts/signup/?next=/invite/manager/accept/%s/%s/' % (self.invitation.pk, self.invitation.key), 302, 200)

    def test_accept_manager_invitation_logged_in_correct_user(self):
        self.client.login(username='harrypotter', password='imawizard')
        response = self.client.get('/invite/manager/accept/%s/%s/' % (self.invitation.pk, self.invitation.key))

        self.assertRedirects(response, self.page.get_absolute_url(), 302, 200)
        self.assertTrue(self.user2.has_perm('manager_edit', self.page))
        self.assertTrue(self.user2.has_perm('manager_delete', self.page))
        self.assertTrue(self.user2.has_perm('manager_invite', self.page))
        self.assertTrue(self.user2.has_perm('manager_image_edit', self.page))
        self.assertIn(self.user2.userprofile, self.page.subscribers.all())

        invitations = models.ManagerInvitation.objects.filter(expired=False)
        self.assertNotIn(self.invitation, invitations)

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/testpage/dashboard/')
        self.assertContains(response, "%s %s" % (self.user2.first_name, self.user2.last_name), status_code=200)
        self.assertContains(response, self.user2.email, status_code=200)

    # need to write tests for these when the view has been built:
        # wrong user accepts invite
        # bad invitation pk
        # bad invitation key

    def test_decline_invitation_logged_out(self):
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.decline_invitation(request, 'manager', self.invitation.pk, self.invitation.key)
        response.client = self.client

        self.assertRedirects(response, reverse('home'), 302, 200)
        self.assertFalse(self.user2.has_perm('manager_edit', self.page))
        self.assertFalse(self.user2.has_perm('manager_delete', self.page))
        self.assertFalse(self.user2.has_perm('manager_invite', self.page))
        self.assertFalse(self.user2.has_perm('manager_image_edit', self.page))

        invitations = models.ManagerInvitation.objects.filter(expired=False)
        self.assertNotIn(self.invitation, invitations)

    def test_decline_invitation_logged_in(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.decline_invitation(request, 'manager', self.invitation.pk, self.invitation.key)
        response.client = self.client

        self.client.login(username='harrypotter', password='imawizard')
        response = self.client.get('/invite/manager/decline/%s/%s/' % (self.invitation.pk, self.invitation.key))
        self.assertRedirects(response, '/invite/pending/', 302, 200)
        self.assertFalse(self.user2.has_perm('manager_edit', self.page))
        self.assertFalse(self.user2.has_perm('manager_delete', self.page))
        self.assertFalse(self.user2.has_perm('manager_invite', self.page))
        self.assertFalse(self.user2.has_perm('manager_image_edit', self.page))

        invitations = models.ManagerInvitation.objects.filter(expired=False)
        self.assertNotIn(self.invitation, invitations)

    def test_remove_invitation(self):
        m_invitations = models.ManagerInvitation.objects.filter(expired=False)
        self.assertIn(self.invitation, m_invitations)
        g_invitations = models.GeneralInvitation.objects.filter(expired=False)
        self.assertIn(self.invitation2, g_invitations)

        views.remove_invitation(self.invitation.pk, 'manager', 'True', 'False')
        views.remove_invitation(self.invitation2.pk, 'general', 'True', 'False')

        m_invitations = models.ManagerInvitation.objects.filter(expired=False)
        self.assertNotIn(self.invitation, m_invitations)
        g_invitations = models.GeneralInvitation.objects.filter(expired=False)
        self.assertNotIn(self.invitation2, g_invitations)

    def test_forgot_password_reset(self):
        # click forgot password link and go to form
        response = self.client.get('/forgot/')
        self.assertEqual(response.status_code, 200)

        # put email in form and submit
        response = self.client.post('/forgot/', {'email': 'i@forgot.it'})
        self.assertRedirects(response, '/', 302, 200)

        # click email link to go to password reset
        invitation = models.ForgotPasswordRequest.objects.get(email='i@forgot.it', expired=False, completed=False)
        response = self.client.get('/password/reset/%s/%s/' % (invitation.pk, invitation.key))
        self.assertEqual(response.status_code, 200)

        # set both passwords and submit
        data = {
            'password1': 'newpassword',
            'password2': 'newpassword'
        }
        response = self.client.post('/password/reset/%s/%s/' % (invitation.pk, invitation.key), data)
        self.assertRedirects(response, '/', 302, 200)

        # login with new passwords
        self.client.login(username='forgetful', password='newpassword')
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)

    def test_forgot_password_reset_expired(self):
        data = {
            'password1': 'newpassword',
            'password2': 'newpassword'
        }
        response = self.client.post('/password/reset/%s/%s/' % (self.forgotpasswordrequest.pk, self.forgotpasswordrequest.key), data)
        self.assertRedirects(response, '/error/password/reset/expired/', 302, 200)

    def test_forgot_password_reset_completed(self):
        data = {
            'password1': 'newpassword',
            'password2': 'newpassword'
        }
        response = self.client.post('/password/reset/%s/%s/' % (self.forgotpasswordrequest2.pk, self.forgotpasswordrequest2.key), data)
        self.assertRedirects(response, '/error/password/reset/completed/', 302, 200)
