from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase
from django.utils import timezone
from guardian.shortcuts import assign_perm

from . import forms
from . import models
from . import views
from invitations.models import ManagerInvitation
from page.models import Page


class CampaignTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.test',
            password='testpassword'
        )

        self.user2 = User.objects.create_user(
            username='pizza',
            email='my@pizza.pie',
            password='mehungry'
        )

        self.user3 = User.objects.create_user(
            username='ineedfood',
            email='give@food.pls',
            password='stomachwantsit'
        )

        self.user4 = User.objects.create_user(
            username='goforit',
            email='go@for.it',
            password='yougottawin'
        )

        self.user5 = User.objects.create_user(
            username='ijustate',
            email='now@im.full',
            password='foodcoma'
        )

        self.page = Page.objects.create(name='Test Page',)
        self.page.admins.add(self.user.userprofile)

        self.campaign = models.Campaign.objects.create(
            name='Test Campaign',
            campaign_slug='campaignslug',
            page=self.page,
            type='Event',
            city='Dallas',
            state='Texas',
            description='This is a description for Test Campaign.',
            goal='666',
            donation_count='5',
            donation_money='100'
        )

        self.campaign.campaign_admins.add(self.user.userprofile)
        self.campaign.campaign_managers.add(self.user2.userprofile)
        assign_perm('manager_edit', self.user2, self.campaign)
        assign_perm('manager_delete', self.user2, self.campaign)
        assign_perm('manager_invite', self.user2, self.campaign)
        self.campaign.campaign_managers.add(self.user4.userprofile)

        self.invitation = ManagerInvitation.objects.create(
            invite_to=self.user3.email,
            invite_from=self.user,
            campaign=self.campaign
        )

    def test_campaign_exists(self):
        campaigns = models.Campaign.objects.all()
        self.assertIn(self.campaign, campaigns)

    def test_page_creation_time(self):
        campaign = models.Campaign.objects.create(name='time tester', page=self.page)
        now = timezone.now()
        self.assertLess(campaign.created_on, now)

    def test_duplicate_campaign_slug(self):
        self.client.login(username='testuser', password='testpassword')

        data = {
            'name': "MyCampaign",
            'campaign_slug': "campaignslug"
        }

        response = self.client.post('/%s/campaign/create/' % self.page.page_slug, data)
        self.assertEqual(models.Campaign.objects.all().count(), 1)

    def test_campaign_status_logged_out(self):
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.campaign(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign.type, status_code=200)
        self.assertContains(response, self.campaign.city, status_code=200)
        self.assertContains(response, self.campaign.state, status_code=200)
        self.assertContains(response, self.campaign.description, status_code=200)
        self.assertContains(response, self.campaign.goal, status_code=200)
        self.assertContains(response, self.campaign.donation_count, status_code=200)
        self.assertContains(response, self.campaign.donation_money, status_code=200)

    def test_campaign_status_logged_in(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.campaign(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign.type, status_code=200)
        self.assertContains(response, self.campaign.city, status_code=200)
        self.assertContains(response, self.campaign.state, status_code=200)
        self.assertContains(response, self.campaign.description, status_code=200)
        self.assertContains(response, self.campaign.goal, status_code=200)
        self.assertContains(response, self.campaign.donation_count, status_code=200)
        self.assertContains(response, self.campaign.donation_money, status_code=200)

    def test_campaign_admin_logged_out(self):
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.campaign(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Admin", status_code=200)
        self.assertNotContains(response, "Edit Campaign", status_code=200)
        self.assertNotContains(response, "Delete Campaign", status_code=200)
        self.assertNotContains(response, "Manager", status_code=200)
        self.assertNotContains(response, "Invite others to manage Campaign", status_code=200)

    def test_campaign_admin_logged_in(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.campaign(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin", status_code=200)
        self.assertContains(response, "Edit Campaign", status_code=200)
        self.assertContains(response, "Delete Campaign", status_code=200)
        self.assertContains(response, "/%s/%s/%s/managers/%s/remove/" % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug,
            self.user2.pk
            ), status_code=200)

    def test_campaign_manager_logged_in(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.campaign(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manager", status_code=200)
        self.assertContains(response, "Edit Campaign", status_code=200)
        self.assertContains(response, "Delete Campaign", status_code=200)
        self.assertContains(response, "Invite others to manage Campaign", status_code=200)

    def test_campaign_edit_not_admin(self):
        self.client.login(username='ineedfood', password='stomachwantsit')
        response = self.client.get('/%s/%s/%s/edit/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 404)

    def test_campaign_edit_admin(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.campaign_edit(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 200)

    def test_campaign_edit_manager_perms(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.campaign_edit(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 200)

    def test_campaign_edit_manager_no_perms(self):
        self.client.login(username='goforit', password='yougottawin')
        response = self.client.get('/%s/%s/%s/edit/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 404)

    def test_deletecampaignform(self):
        form = forms.DeleteCampaignForm({
            'name': self.campaign
        })
        self.assertTrue(form.is_valid())

    def test_delete_campaign_admin(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.campaign_delete(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug)

        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)

    def test_delete_campaign_logged_out(self):
        response = self.client.get('/%s/%s/%s/delete/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertRedirects(response, '/accounts/login/?next=/%s/%s/%s/delete/' % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug
            ), 302, 200
        )

    def test_delete_campaign_not_admin(self):
        self.client.login(username='ineedfood', password='stomachwantsit')
        response = self.client.get('/%s/%s/%s/delete/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 404)

    def test_delete_campaign_manager_perms(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.campaign_delete(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug)

        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)

    def test_delete_campaign_manager_no_perms(self):
        self.client.login(username='goforit', password='yougottawin')
        response = self.client.get('/%s/%s/%s/delete/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 404)

    def test_campaign_create_logged_out(self):
        response = self.client.get('/%s/campaign/create/' % self.page.page_slug)
        self.assertRedirects(response, '/accounts/login/?next=/%s/campaign/create/' % self.page.page_slug, 302, 200)

    def test_campaign_create_logged_in(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.campaign_create(request, self.page.page_slug)

        self.assertEqual(response.status_code, 200)

    def test_campaignform(self):
        form = forms.CampaignForm({
            'name': 'Headphones',
            'city': 'Austin',
            'state': 'TX',
            'campaign_slug': 'headphones',
            'goal': '234',
            'type': 'event',
            'description': 'I wear headphones.'
        })
        self.assertTrue(form.is_valid())
        campaign = form.save(commit=False)
        campaign.user = self.user
        campaign.page = self.page
        campaign.save()
        self.assertEqual(campaign.name, "Headphones")
        self.assertEqual(campaign.user, self.user)
        self.assertEqual(campaign.page, self.page)
        self.assertEqual(campaign.city, "Austin")
        self.assertEqual(campaign.state, "TX")
        self.assertEqual(campaign.campaign_slug, "headphones")
        self.assertEqual(campaign.goal, 234)
        self.assertEqual(campaign.type, "event")
        self.assertEqual(campaign.description, "I wear headphones.")

    def test_campaignform_blank(self):
        form = forms.CampaignForm({})
        self.assertFalse(form.is_valid())

    def test_campaign_edit_status_logged_out(self):
        response = self.client.get('/%s/%s/%s/edit/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertRedirects(response, '/accounts/login/?next=/%s/%s/%s/edit/' % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug
            ), 302, 200
        )

    def test_campaign_edit_status_not_admin(self):
        self.client.login(username='ineedfood', password='stomachwantsit')
        response = self.client.get('/%s/%s/%s/edit/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 404)

    def test_campaign_edit_status_admin(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.campaign_edit(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)

    def test_campaign_invite_not_admin_not_manager(self):
        self.client.login(username='ineedfood', password='stomachwantsit')
        response = self.client.get('/%s/%s/%s/managers/invite/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 404)

    def test_campaign_invite_admin_not_manager(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.campaign_invite(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, "Invite", status_code=200)

    def test_campaign_invite_not_admin_manager_no_perms(self):
        self.client.login(username='goforit', password='yougottawin')
        response = self.client.get('/%s/%s/%s/managers/invite/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 404)

    def test_campaign_invite_not_admin_manager_perms(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.campaign_invite(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, "Invite", status_code=200)

    def test_campaign_invite(self):
        data = {
            'email': self.user2.email,
            'manager_edit': "True",
            'manager_delete': "True",
            'manager_invite': "True"
        }

        self.client.login(username='testuser', password='testpassword')

        # user is already a manager
        response = self.client.post('/%s/%s/%s/managers/invite/' % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug
            ), data
        )
        self.assertRedirects(response, self.campaign.get_absolute_url(), 302, 200)

        # user already has an invite
        data['email'] = self.user3.email
        response = self.client.post('/%s/%s/%s/managers/invite/' % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug
            ), data
        )
        self.assertRedirects(response, self.campaign.get_absolute_url(), 302, 200)

        # user isn't a manager and doesn't have an invite
        data['email'] = self.user5.email
        response = self.client.post('/%s/%s/%s/managers/invite/' % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug
            ), data
        )
        self.assertTrue(ManagerInvitation.objects.all().count(), 2)
        self.assertRedirects(response, self.campaign.get_absolute_url(), 302, 200)

    def test_ManagerInviteForm(self):
        data = {
            'email': self.user5.email,
            'manager_edit': "True",
            'manager_delete': "True",
            'manager_invite': "True"
        }
        form = forms.ManagerInviteForm(data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form['email'], self.user5.email)
        self.assertTrue(form['manager_edit'], "True")
        self.assertTrue(form['manager_delete'], "True")
        self.assertTrue(form['manager_invite'], "True")

    def test_ManagerInviteForm_blank(self):
        form = forms.ManagerInviteForm({})
        self.assertFalse(form.is_valid())

    def test_remove_manager_logged_out(self):
        response = self.client.get('/%s/%s/%s/managers/%s/remove/' % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug,
            self.user3.pk
            )
        )
        self.assertRedirects(response, '/accounts/login/?next=/%s/%s/%s/managers/%s/remove/' % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug,
            self.user3.pk
            ), 302, 200
        )

    def test_remove_manager_logged_in_not_admin(self):
        self.client.login(username='ineedfood', password='stomachwantsit')
        response = self.client.get('/%s/%s/%s/managers/%s/remove/' % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug,
            self.user2.pk
        ))
        self.assertEqual(response.status_code, 404)

    def test_remove_manager_logged_in_admin(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.remove_manager(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug, self.user2.pk)
        response.client = self.client

        self.assertRedirects(response, self.campaign.get_absolute_url(), 302, 200)

    def test_remove_manager(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.remove_manager(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug, self.user2.pk)
        response.client = self.client

        managers = self.campaign.campaign_managers.all()
        self.assertNotIn(self.user2, managers)
        self.assertFalse(self.user2.has_perm('manager_edit', self.campaign))
        self.assertFalse(self.user2.has_perm('manager_delete', self.campaign))
        self.assertFalse(self.user2.has_perm('manager_invite', self.campaign))
        self.assertRedirects(response, self.campaign.get_absolute_url(), 302, 200)

    def test_campaign_permissions_add(self):
        permissions = []
        permissions.append(str(self.user4.pk) + "_manager_edit")
        permissions.append(str(self.user4.pk) + "_manager_delete")
        permissions.append(str(self.user4.pk) + "_manager_invite")
        data = {'permissions[]': permissions}

        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/%s/%s/%s/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug), data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user4.has_perm('manager_edit', self.campaign))
        self.assertTrue(self.user4.has_perm('manager_delete', self.campaign))
        self.assertTrue(self.user4.has_perm('manager_invite', self.campaign))

    def test_campaign_permissions_remove(self):
        permissions = []
        permissions.append(str(self.user2.pk) + "_manager_invite")
        data = {'permissions[]': permissions}

        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/%s/%s/%s/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user2.has_perm('manager_edit', self.campaign))
        self.assertFalse(self.user2.has_perm('manager_delete', self.campaign))
        self.assertTrue(self.user2.has_perm('manager_invite', self.campaign))

    def test_campaign_permissions_multiple(self):
        permissions = []
        permissions.append(str(self.user2.pk) + "_manager_invite")
        permissions.append(str(self.user4.pk) + "_manager_edit")
        permissions.append(str(self.user4.pk) + "_manager_delete")
        permissions.append(str(self.user4.pk) + "_manager_invite")
        data = {'permissions[]': permissions}

        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/%s/%s/%s/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user2.has_perm('manager_edit', self.campaign))
        self.assertFalse(self.user2.has_perm('manager_delete', self.campaign))
        self.assertTrue(self.user2.has_perm('manager_invite', self.campaign))
        self.assertTrue(self.user4.has_perm('manager_edit', self.campaign))
        self.assertTrue(self.user4.has_perm('manager_delete', self.campaign))
        self.assertTrue(self.user4.has_perm('manager_invite', self.campaign))
