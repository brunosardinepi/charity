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
            description='This is a description for Test Page.',
            donation_count='20',
            donation_money='30',
            category='Animal'
        )

        self.invitation = models.ManagerInvitation.objects.create(
            invite_to=self.user2.email,
            invite_from=self.user,
            page=self.page,
            manager_edit_page=True,
            manager_delete_page=True,
            manager_invite_page=True
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
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.accept_invitation(request, self.invitation.pk, self.invitation.key)

        self.assertEqual(response.status_code, 302)

    def test_accept_invitation_logged_in_correct_user(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.accept_invitation(request, self.invitation.pk, self.invitation.key)
        response.client = self.client

        self.assertRedirects(response, self.page.get_absolute_url(), 302, 200)
        self.assertTrue(self.user2.has_perm('manager_edit_page', self.page))
        self.assertTrue(self.user2.has_perm('manager_delete_page', self.page))
        self.assertTrue(self.user2.has_perm('manager_invite_page', self.page))

        invitations = models.ManagerInvitation.objects.filter(expired=False)
        self.assertNotIn(self.invitation, invitations)

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
        self.assertFalse(self.user2.has_perm('manager_edit_page', self.page))
        self.assertFalse(self.user2.has_perm('manager_delete_page', self.page))
        self.assertFalse(self.user2.has_perm('manager_invite_page', self.page))

        invitations = models.ManagerInvitation.objects.filter(expired=False)
        self.assertNotIn(self.invitation, invitations)

    def test_decline_invitation_logged_in(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.decline_invitation(request, self.invitation.pk, self.invitation.key)
        response.client = self.client

#        self.assertRedirects(response, 'invite/pending', 302, 200)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.user2.has_perm('manager_edit_page', self.page))
        self.assertFalse(self.user2.has_perm('manager_delete_page', self.page))
        self.assertFalse(self.user2.has_perm('manager_invite_page', self.page))

        invitations = models.ManagerInvitation.objects.filter(expired=False)
        self.assertNotIn(self.invitation, invitations)





#def decline_invitation(request, invitation_pk, key):
#    invitation = get_object_or_404(models.ManagerInvitation, pk=invitation_pk)
#    if (int(invitation_pk) == int(invitation.pk)) and (key == invitation.key):
#        remove_invitation(invitation_pk, "False", "True")
#    else:
#        print("bad")

#    # if the user is logged in and declined the invitation, redirect them to their other pending invitations
#    if request.user.is_authenticated():
#        return HttpResponseRedirect(reverse('invitations:pending_invitations'))
#    # if the user isn't logged in and declined the invitation, redirect them to the homepage
#    else:
#        return HttpResponseRedirect(reverse('home'))
