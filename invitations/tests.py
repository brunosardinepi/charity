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
            password='imawizard'
        )

        self.page = models.Page.objects.create(
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
            manager_upload=True
        )

    def test_invitation_exists(self):
        invitations = models.ManagerInvitation.objects.all()
        self.assertIn(self.invitation, invitations)

    def test_invitation_page(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.pending_invitations(request)

        self.assertEqual(response.status_code, 200)

    def test_accept_invitation_logged_out(self):
        response = self.client.get('/invite/accept/%s/%s/' % (self.invitation.pk, self.invitation.key))
        self.assertRedirects(response, '/accounts/signup/?next=/invite/accept/%s/%s/' % (self.invitation.pk, self.invitation.key), 302, 200)

    def test_accept_invitation_logged_in_correct_user(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.accept_invitation(request, self.invitation.pk, self.invitation.key)
        response.client = self.client

        self.assertRedirects(response, self.page.get_absolute_url(), 302, 200)
        self.assertTrue(self.user2.has_perm('manager_edit', self.page))
        self.assertTrue(self.user2.has_perm('manager_delete', self.page))
        self.assertTrue(self.user2.has_perm('manager_invite', self.page))
        self.assertTrue(self.user2.has_perm('manager_upload', self.page))

        invitations = models.ManagerInvitation.objects.filter(expired=False)
        self.assertNotIn(self.invitation, invitations)

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/testpage/')
        self.assertContains(response, "%s %s" % (self.user2.userprofile.first_name, self.user2.userprofile.last_name), status_code=200)
        self.assertContains(response, self.user2.email, status_code=200)

    # need to write tests for these when the view has been built:
        # wrong user accepts invite
        # bad invitation pk
        # bad invitation key

    def test_decline_invitation_logged_out(self):
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.decline_invitation(request, self.invitation.pk, self.invitation.key)
        response.client = self.client

        self.assertRedirects(response, reverse('home'), 302, 200)
        self.assertFalse(self.user2.has_perm('manager_edit', self.page))
        self.assertFalse(self.user2.has_perm('manager_delete', self.page))
        self.assertFalse(self.user2.has_perm('manager_invite', self.page))
        self.assertFalse(self.user2.has_perm('manager_upload', self.page))

        invitations = models.ManagerInvitation.objects.filter(expired=False)
        self.assertNotIn(self.invitation, invitations)

    def test_decline_invitation_logged_in(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.decline_invitation(request, self.invitation.pk, self.invitation.key)
        response.client = self.client

        self.client.login(username='harrypotter', password='imawizard')
        response = self.client.get('/invite/decline/%s/%s/' % (self.invitation.pk, self.invitation.key))
        self.assertRedirects(response, '/invite/pending/', 302, 200)
        self.assertFalse(self.user2.has_perm('manager_edit', self.page))
        self.assertFalse(self.user2.has_perm('manager_delete', self.page))
        self.assertFalse(self.user2.has_perm('manager_invite', self.page))
        self.assertFalse(self.user2.has_perm('manager_upload', self.page))

        invitations = models.ManagerInvitation.objects.filter(expired=False)
        self.assertNotIn(self.invitation, invitations)

    def test_remove_invitation(self):
        invitations = models.ManagerInvitation.objects.filter(expired=False)
        self.assertIn(self.invitation, invitations)

        views.remove_invitation(self.invitation.pk, "True", "False")
        invitations = models.ManagerInvitation.objects.filter(expired=False)
        self.assertNotIn(self.invitation, invitations)
