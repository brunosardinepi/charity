import ast
import datetime
import pytz

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Sum
from django.forms import formset_factory
from django.test import Client, RequestFactory, TestCase
from django.utils import timezone
from guardian.shortcuts import assign_perm

from . import forms
from . import models
from . import views
from donation.models import Donation
from invitations.models import ManagerInvitation
from page.models import Page


class CampaignTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.test',
            password='testpassword',
            first_name='Tester',
            last_name='McTestee',
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

        self.page = Page.objects.create(
            name='Test Page',
            page_slug='testpage',
        )
        self.page.admins.add(self.user.userprofile)

        self.page2 = Page.objects.create(
            name='uihasdlkjahsd',
            page_slug='uhaslduhaskjd',
        )

        self.campaign = models.Campaign.objects.create(
            name='Test Campaign',
            campaign_slug='testcampaign',
            page=self.page,
            type='vote',
            description='This is a description for Test Campaign.',
            goal='666',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )

        self.campaign.campaign_admins.add(self.user.userprofile)
        self.campaign.campaign_managers.add(self.user2.userprofile)
        assign_perm('manager_edit', self.user2, self.campaign)
        assign_perm('manager_delete', self.user2, self.campaign)
        assign_perm('manager_invite', self.user2, self.campaign)
        assign_perm('manager_image_edit', self.user2, self.campaign)
        self.campaign.campaign_managers.add(self.user4.userprofile)

        self.campaign2 = models.Campaign.objects.create(
            name='Captain',
            campaign_slug='captain',
            page=self.page,
            type='event',
            description='Im the captain',
            goal='334',
            deleted=True,
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )

        self.campaign3 = models.Campaign.objects.create(
            name='haisdufhasdlkfnasdlkjfnsd',
            campaign_slug='uhilwuaenflaknjndsaf',
            page=self.page2,
            type='general',
            description='aoiefj;asfn eafjsafj dsa;lfkjaeio;fj asdklf',
            goal='1999',
            end_date=datetime.datetime(2001, 8, 15, 8, 15, 12, 0, pytz.UTC),
            is_active=False,
        )

        self.invitation = ManagerInvitation.objects.create(
            invite_to=self.user3.email,
            invite_from=self.user,
            campaign=self.campaign
        )

        self.vote_participant = models.VoteParticipant.objects.create(
            name="Harry",
            campaign=self.campaign,
        )

        self.vote_participant2 = models.VoteParticipant.objects.create(
            name="Sally",
            campaign=self.campaign,
        )

        self.donation = Donation.objects.create(
            amount=2000,
            comment='I donated!',
            page=self.campaign.page,
            campaign=self.campaign,
            user=self.user,
        )

        self.donation2 = Donation.objects.create(
            amount=800,
            comment='I like campaigns.',
            page=self.campaign.page,
            campaign=self.campaign,
            user=self.user,
        )

        self.donation3 = models.Donation.objects.create(
            amount=163,
            anonymous_amount=True,
            anonymous_donor=True,
            comment='Total ghost',
            page=self.campaign.page,
            campaign=self.campaign,
            campaign_participant=self.vote_participant,
            user=self.user,
        )

        self.donation4 = models.Donation.objects.create(
            amount=1375,
            anonymous_donor=True,
            comment='No name',
            page=self.campaign.page,
            campaign=self.campaign,
            campaign_participant=self.vote_participant,
            donor_first_name="Frank",
            donor_last_name="Jackson",
        )

        self.donation5 = models.Donation.objects.create(
            amount=566511,
            anonymous_amount=True,
            comment='Goodbye amount',
            page=self.campaign.page,
            campaign=self.campaign,
            campaign_participant=self.vote_participant2,
            user=self.user
        )

        self.donation6 = models.Donation.objects.create(
            amount=8365,
            anonymous_amount=True,
            anonymous_donor=True,
            comment='What is happening',
            page=self.campaign.page,
            campaign=self.campaign,
            campaign_participant=self.vote_participant2,
            user=self.user
        )

    def test_campaign_exists(self):
        campaigns = models.Campaign.objects.all()
        self.assertIn(self.campaign, campaigns)

    def test_campaign_no_exist(self):
        response = self.client.get('/page/3/campaign/')
        self.assertRedirects(response, '/notes/error/campaign/does-not-exist/', 302, 200)

    def test_campaign_creation_time(self):
        campaign = models.Campaign.objects.create(
            name='time tester',
            page=self.page,
            goal='666',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )
        now = timezone.now()
        self.assertLess(campaign.created_on, now)

    def test_page_delete_cascade(self):
        campaigns = models.Campaign.objects.filter(deleted=False)
        self.assertEqual(campaigns.count(), 2)

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/%s/delete/' % self.page.page_slug)
        campaigns = models.Campaign.objects.filter(deleted=False)
        self.assertEqual(campaigns.count(), 1)

    def test_duplicate_campaign_slug(self):
        self.client.login(username='testuser', password='testpassword')
        data = {
            'name': "MyCampaign",
            'campaign_slug': self.campaign.campaign_slug,
            'page': self.page.pk,
            'type': "vote",
            'category': "other",
            'goal': 1000,
            'end_date': "2099-01-01 00:00:00",
        }
        response = self.client.post('/create/campaign/', data)
        self.assertEqual(models.Campaign.objects.filter(deleted=False).count(), 3)

        campaign = models.Campaign.objects.get(name="MyCampaign")
        self.assertIn(self.user.userprofile, campaign.campaign_subscribers.all())

    def test_campaign_status_logged_out(self):
        response = self.client.get('/%s/%s/%s/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign.get_type_display(), status_code=200)
        self.assertContains(response, self.campaign.description, status_code=200)
        self.assertContains(response, self.campaign.goal, status_code=200)
        self.assertContains(response, self.campaign.donation_count(), status_code=200)
        self.assertContains(response, int(self.campaign.donation_money() / 100), status_code=200)
        self.assertContains(response, self.vote_participant.name)
        self.assertContains(response, self.vote_participant2.name)
        self.assertContains(response, int(self.vote_participant.vote_amount() / 100))
        self.assertContains(response, int(self.vote_participant2.vote_amount() / 100))

    def test_campaign_status_logged_in(self):
        response = self.client.get('/%s/%s/%s/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign.get_type_display(), status_code=200)
        self.assertContains(response, self.campaign.description, status_code=200)
        self.assertContains(response, self.campaign.goal, status_code=200)
        self.assertContains(response, self.campaign.donation_count(), status_code=200)
        self.assertContains(response, int(self.campaign.donation_money() / 100), status_code=200)

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

    def test_campaign_manager_logged_in(self):
        self.client.login(username='pizza', password='mehungry')
        response = self.client.get('/{}/{}/{}/'.format(self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manage", status_code=200)

        response = self.client.get('/{}/{}/{}/manage/admin/'.format(self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Campaign")
        self.assertContains(response, "Delete Campaign")
        self.assertContains(response, "Invite others to manage Campaign")
        self.assertContains(response, "Remove self as manager")
        self.assertNotContains(response, "/%s/%s/%s/managers/%s/remove/".format(self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug, self.user4.pk))

    def test_campaign_edit_not_admin(self):
        self.client.login(username='ineedfood', password='stomachwantsit')
        response = self.client.get('/%s/%s/%s/edit/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertRedirects(response, '/notes/error/permissions/', 302, 200)

    def test_campaign_edit_admin(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/{}/{}/manage/admin/'.format(
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug
        ))

        self.assertEqual(response.status_code, 200)

    def test_campaign_edit_manager_perms(self):
        self.client.login(username='pizza', password='mehungry')
        response = self.client.get('/%s/%s/%s/edit/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))

        self.assertEqual(response.status_code, 200)

    def test_campaign_edit_manager_no_perms(self):
        self.client.login(username='goforit', password='yougottawin')
        response = self.client.get('/%s/%s/%s/edit/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertRedirects(response, '/notes/error/permissions/', 302, 200)

    def test_deletecampaignform(self):
        form = forms.DeleteCampaignForm({
            'name': self.campaign
        })
        self.assertTrue(form.is_valid())

    def test_delete_campaign_admin(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/%s/%s/%s/delete/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))

        self.assertRedirects(response, '/%s/' % self.page.page_slug, 302, 200)

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
        self.assertRedirects(response, '/notes/error/permissions/', 302, 200)

    def test_delete_campaign_manager_perms(self):
        self.client.login(username='pizza', password='mehungry')
        response = self.client.get('/%s/%s/%s/delete/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))

        self.assertRedirects(response, '/%s/' % self.page.page_slug, 302, 200)

    def test_delete_campaign_manager_no_perms(self):
        self.client.login(username='goforit', password='yougottawin')
        response = self.client.get('/%s/%s/%s/delete/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertRedirects(response, '/notes/error/permissions/', 302, 200)

    def test_campaign_create_logged_out(self):
        response = self.client.get('/%s/campaign/create/' % self.page.page_slug)
        self.assertRedirects(response, '/accounts/login/?next=/%s/campaign/create/' % self.page.page_slug, 302, 200)

    def test_campaign_create_event_logged_in(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/campaign/create/'.format(self.page.page_slug))
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/create/campaign/')
        self.assertEqual(response.status_code, 200)

        data = {
            'name': "MyCampaign",
            'campaign_slug': "mycampaign",
            'page': self.page.pk,
            'type': "general",
            'category': "other",
            'goal': 1000,
            'end_date': "2099-01-01 00:00:00",
        }
        response = self.client.post('/create/campaign/', data)
        self.assertEqual(models.Campaign.objects.filter(deleted=False).count(), 3)
        campaign = models.Campaign.objects.get(campaign_slug="mycampaign")
        self.assertRedirects(response, '/{}/{}/{}/'.format(campaign.page.page_slug, campaign.pk, campaign.campaign_slug), 302, 200)

    def test_campaign_create_vote_logged_in(self):
        self.client.login(username='testuser', password='testpassword')
        data = {
            'name': "MyCampaign",
            'campaign_slug': "mycampaign",
            'page': self.page.pk,
            'type': "vote",
            'category': "other",
            'goal': 1000,
            'end_date': "2099-01-01 00:00:00",
        }
        response = self.client.post('/create/campaign/', data)
        self.assertEqual(models.Campaign.objects.filter(deleted=False).count(), 3)
        campaign = models.Campaign.objects.get(campaign_slug="mycampaign")
        self.assertRedirects(response, '/{}/{}/{}/vote/edit/'.format(campaign.page.page_slug, campaign.pk, campaign.campaign_slug), 302, 200)

    def test_campaignform(self):
        form = forms.CampaignForm({
            'name': 'Headphones',
            'campaign_slug': 'headphones',
            'goal': '234',
            'type': 'vote',
            'category': 'other',
            'description': 'I wear headphones.',
            'end_date': '2099-01-01 00:00:00',
        })
        self.assertTrue(form.is_valid())
        campaign = form.save(commit=False)
        campaign.user = self.user
        campaign.page = self.page
        campaign.save()
        self.assertEqual(campaign.name, "Headphones")
        self.assertEqual(campaign.user, self.user)
        self.assertEqual(campaign.page, self.page)
        self.assertEqual(campaign.campaign_slug, "headphones")
        self.assertEqual(campaign.goal, 234)
        self.assertEqual(campaign.type, "vote")
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
        self.assertRedirects(response, '/notes/error/permissions/', 302, 200)

    def test_campaign_edit_status_admin(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.campaign_edit(request, self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.name, status_code=200)

    def test_campaign_invite_not_admin_not_manager(self):
        self.client.login(username='ineedfood', password='stomachwantsit')
        response = self.client.get('/%s/%s/%s/managers/invite/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertRedirects(response, '/notes/error/permissions/', 302, 200)

    def test_campaign_invite_admin_not_manager(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/{}/{}/managers/invite/'.format(
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug
        ))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.name)
        self.assertContains(response, "Invite")

    def test_campaign_invite_not_admin_manager_no_perms(self):
        self.client.login(username='goforit', password='yougottawin')
        response = self.client.get('/%s/%s/%s/managers/invite/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertRedirects(response, '/notes/error/permissions/', 302, 200)

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
            'manager_invite': "True",
            'manager_image_edit': "True",
            'manager_view_dashboard': "True",
        }

        self.client.login(username='testuser', password='testpassword')

        response = self.client.get('/{}/{}/{}/managers/invite/'.format(
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug,
        ))

        # user is already a manager
        response = self.client.post('/%s/%s/%s/managers/invite/' % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug
            ), data)

        self.assertRedirects(response, '/notes/error/invite/manager-exists/', 302, 200)

        # user already has an invite
        data['email'] = self.user3.email
        response = self.client.post('/%s/%s/%s/managers/invite/' % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug
            ), data
        )
        self.assertRedirects(response, '/{}/{}/{}/manage/admin/'.format(
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug), 302, 200)

        # user isn't a manager and doesn't have an invite
        data['email'] = self.user5.email
        response = self.client.post('/%s/%s/%s/managers/invite/' % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug
            ), data
        )
        self.assertTrue(ManagerInvitation.objects.all().count(), 2)
        self.assertRedirects(response, '/{}/{}/{}/manage/admin/'.format(
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug), 302, 200)
        # accept the invite and make sure the page has the right perms
        self.client.login(username='ijustate', password='foodcoma')
        invitation = ManagerInvitation.objects.get(invite_to=self.user5.email)
        response = self.client.get('/invite/manager/accept/%s/%s/' % (invitation.pk, invitation.key))
        self.assertRedirects(response, invitation.campaign.get_absolute_url(), 302, 200)
        response = self.client.get('/%s/%s/%s/manage/admin/' % (
            invitation.campaign.page.page_slug,
            invitation.campaign.pk,
            invitation.campaign.campaign_slug
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user5.userprofile, self.campaign.campaign_subscribers.all())
        self.assertContains(response, "Edit Campaign", status_code=200)
        self.assertContains(response, "Delete Campaign", status_code=200)
        self.assertContains(response, "Invite others to manage Campaign", status_code=200)

    def test_page_dashboard_invite(self):
        data = {
            'email': self.user5.email,
            'manager_edit': "True",
            'manager_delete': "True",
            'manager_invite': "True",
            'manager_image_edit': "True",
            'manager_view_dashboard': "False",
        }

        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/{}/{}/{}/managers/invite/'.format(self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug), data)
        self.assertTrue(ManagerInvitation.objects.all().count(), 2)
        self.assertRedirects(response, '/{}/{}/{}/manage/admin/'.format(
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug), 302, 200)

        self.client.login(username='ijustate', password='foodcoma')
        invitation = ManagerInvitation.objects.get(invite_to=self.user5.email)
        response = self.client.get('/invite/manager/accept/{}/{}/'.format(invitation.pk, invitation.key))
        self.assertRedirects(response, invitation.campaign.get_absolute_url(), 302, 200)
        response = self.client.get('/{}/{}/{}/manage/admin/'.format(invitation.campaign.page.page_slug, invitation.campaign.pk, invitation.campaign.campaign_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Campaign")
        self.assertContains(response, "Delete Campaign")
        self.assertContains(response, "Invite others to manage Campaign")

        self.client.login(username='testuser', password='testpassword')
        permissions = []
        permissions.append(str(self.user5.pk) + "_manager_edit")
        permissions.append(str(self.user5.pk) + "_manager_delete")
        permissions.append(str(self.user5.pk) + "_manager_invite")
        permissions.append(str(self.user5.pk) + "_manager_image_edit")
        permissions.append(str(self.user5.pk) + "_manager_view_dashboard")
        data = {'permissions[]': permissions}
        response = self.client.post('/{}/{}/{}/manage/'.format(self.campaign.page.page_slug, self.campaign.pk, self.campaign.campaign_slug), data)

        self.client.login(username='ijustate', password='foodcoma')
        response = self.client.get('/{}/{}/{}/manage/admin/'.format(self.campaign.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Campaign")
        self.assertContains(response, "Delete Campaign")
        self.assertContains(response, "Invite others to manage Campaign")

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
        self.assertRedirects(response, '/notes/error/permissions/', 302, 200)

    def test_remove_manager_logged_in_admin(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/%s/%s/%s/managers/%s/remove/' % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug,
            self.user2.pk
        ))
        self.assertRedirects(response, '/{}/{}/{}/manage/admin/'.format(self.campaign.page.page_slug, self.campaign.pk, self.campaign.campaign_slug), 302, 200)

    def test_remove_manager(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/%s/%s/%s/managers/%s/remove/' % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug,
            self.user2.pk
        ))

        managers = self.campaign.campaign_managers.all()
        self.assertNotIn(self.user2, managers)
        self.assertFalse(self.user2.has_perm('manager_edit', self.campaign))
        self.assertFalse(self.user2.has_perm('manager_delete', self.campaign))
        self.assertFalse(self.user2.has_perm('manager_invite', self.campaign))
        self.assertFalse(self.user2.has_perm('manager_image_edit', self.campaign))
        self.assertRedirects(response, '/{}/{}/{}/manage/admin/'.format(self.campaign.page.page_slug, self.campaign.pk, self.campaign.campaign_slug), 302, 200)

    def test_campaign_permissions_add(self):
        permissions = []
        permissions.append(str(self.user4.pk) + "_manager_edit")
        permissions.append(str(self.user4.pk) + "_manager_delete")
        permissions.append(str(self.user4.pk) + "_manager_invite")
        permissions.append(str(self.user4.pk) + "_manager_image_edit")
        permissions.append(str(self.user4.pk) + "_manager_view_dashboard")
        data = {'permissions[]': permissions}

        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/%s/%s/%s/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug), data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user4.has_perm('manager_edit', self.campaign))
        self.assertTrue(self.user4.has_perm('manager_delete', self.campaign))
        self.assertTrue(self.user4.has_perm('manager_invite', self.campaign))
        self.assertTrue(self.user4.has_perm('manager_image_edit', self.campaign))
        self.assertTrue(self.user4.has_perm('manager_view_dashboard', self.campaign))

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
        self.assertFalse(self.user2.has_perm('manager_image_edit', self.campaign))

    def test_campaign_permissions_multiple(self):
        permissions = []
        permissions.append(str(self.user2.pk) + "_manager_invite")
        permissions.append(str(self.user2.pk) + "_manager_image_edit")
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
        self.assertTrue(self.user2.has_perm('manager_image_edit', self.campaign))
        self.assertTrue(self.user4.has_perm('manager_edit', self.campaign))
        self.assertTrue(self.user4.has_perm('manager_delete', self.campaign))
        self.assertTrue(self.user4.has_perm('manager_invite', self.campaign))
        self.assertFalse(self.user4.has_perm('manager_image_edit', self.campaign))

    def test_delete_campaign_view(self):
        response = self.client.get('/%s/%s/%s/' % (self.page.page_slug, self.campaign2.pk, self.campaign2.campaign_slug))
        self.assertRedirects(response, '/notes/error/campaign/does-not-exist/', 302, 200)

    def test_upload_admin(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/%s/%s/%s/manage/images/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 200)

    def test_upload_manager_perms(self):
        self.client.login(username='pizza', password='mehungry')
        response = self.client.get('/%s/%s/%s/manage/images/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 200)

    def test_upload_manager_no_perms(self):
        self.client.login(username='goforit', password='yougottawin')
        response = self.client.get('/%s/%s/%s/manage/images/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertRedirects(response, '/notes/error/permissions/', 302, 200)

    def test_upload_logged_in_no_perms(self):
        self.client.login(username='ijustate', password='foodcoma')
        response = self.client.get('/%s/%s/%s/manage/images/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertRedirects(response, '/notes/error/permissions/', 302, 200)

    def test_upload_logged_out(self):
        response = self.client.get('/%s/%s/%s/manage/images/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertRedirects(response, '/accounts/login/?next=/%s/%s/%s/manage/images/' % (
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug
            ), 302, 200
        )

    def test_campaign_subscribe_redirect(self):
        response = self.client.get('/campaign/subscribe/{}/subscribe/'.format(self.campaign.pk))
        self.assertRedirects(response, '/accounts/login/?next=/campaign/subscribe/{}/subscribe/'.format(self.campaign.pk), 302, 200)

    def test_dashboard_total_donations(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/{}/{}/manage/analytics/'.format(self.campaign.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))

        self.assertEqual(response.status_code, 200)
        total_donations = Donation.objects.filter(campaign=self.campaign).aggregate(Sum('amount')).get('amount__sum')
        total_donations_count = Donation.objects.filter(campaign=self.campaign).count()
        total_donations_avg = int((total_donations / total_donations_count) / 100)
        self.assertContains(response, "${}".format(int(total_donations / 100)))
        self.assertContains(response, "${}".format(total_donations_avg))

    def test_dashboard_donation_history(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/{}/{}/manage/donations/'.format(self.campaign.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))

        self.assertContains(response, self.donation.user.first_name, status_code=200)
        self.assertContains(response, self.donation.user.last_name, status_code=200)
        self.assertContains(response, self.donation2.user.first_name, status_code=200)
        self.assertContains(response, self.donation2.user.last_name, status_code=200)

    def test_dashboard_top_donors(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/{}/{}/manage/donations/'.format(self.campaign.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))

        self.assertEqual(response.status_code, 200)
        total_donation_amount = int((self.donation.amount + self.donation2.amount) / 100)
        self.assertContains(response, "{} {}".format(self.user.first_name, self.user.last_name))
        self.assertContains(response, "${}".format(total_donation_amount))

    def test_image_upload(self):
        self.client.login(username='testuser', password='testpassword')
        content = b"a" * 1024
        image = SimpleUploadedFile("image.png", content, content_type="image/png")
        response = self.client.post('/{}/{}/{}/manage/images/'.format(self.campaign.page.page_slug, self.campaign.pk, self.campaign.campaign_slug), {'image': image})
        self.assertEqual(response.status_code, 200)

        images = models.CampaignImage.objects.filter(campaign=self.campaign)
        self.assertEqual(len(images), 1)

        image = images[0]
        response = self.client.get('/{}/{}/{}/'.format(self.campaign.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertContains(response, image.image.url, status_code=200)

        image.delete()
        images = models.CampaignImage.objects.filter(campaign=self.campaign)
        self.assertEqual(len(images), 0)

    def test_image_upload_error_size(self):
        self.client.login(username='testuser', password='testpassword')
        content = b"a" * 1024 * 1024 * 5
        image = SimpleUploadedFile("image.png", content, content_type="image/png")
        response = self.client.post('/{}/{}/{}/manage/images/'.format(self.campaign.page.page_slug, self.campaign.pk, self.campaign.campaign_slug), {'image': image})
        content = response.content.decode('ascii')
        content = ast.literal_eval(content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["is_valid"], "f")
        self.assertEqual(content["redirect"], "error_size")

        images = models.CampaignImage.objects.filter(campaign=self.campaign)
        self.assertEqual(len(images), 0)

    def test_image_upload_error_type(self):
        self.client.login(username='testuser', password='testpassword')
        content = b"a"
        image = SimpleUploadedFile("notimage.txt", content, content_type="text/html")
        response = self.client.post('/{}/{}/{}/manage/images/'.format(self.campaign.page.page_slug, self.campaign.pk, self.campaign.campaign_slug), {'image': image})
        content = response.content.decode('ascii')
        content = ast.literal_eval(content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["is_valid"], "f")
        self.assertEqual(content["redirect"], "error_type")

        images = models.CampaignImage.objects.filter(campaign=self.campaign)
        self.assertEqual(len(images), 0)

    def test_campaign_active(self):
        response = self.client.get('/{}/{}/{}/'.format(self.campaign.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vote")
        self.assertNotContains(response, "Donate")

        self.campaign.is_active = False
        self.campaign.save()
        response = self.client.get('/{}/{}/{}/'.format(self.campaign.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This campaign has ended.")

    def test_vote_participant_formset(self):
        vp_formset = formset_factory(forms.VoteParticipantForm, formset=forms.VoteParticipantFormSet)
        data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-name': 'person1',
            'form-0-description': 'description1',
            'form-1-name': 'person2',
            'form-1-description': 'description2',
        }
        formset = vp_formset(data)
        self.assertTrue(formset.is_valid())

    def test_vote_participants(self):
        self.client.login(username='testuser', password='testpassword')
#        content = b"a" * 1024
#        image1 = SimpleUploadedFile("image1.png", content, content_type="image/png")
#        image2 = SimpleUploadedFile("image2.png", content, content_type="image/png")
        data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '2',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-name': 'person1',
            'form-0-description': 'description1',
#            'form-0-image': image1,
#            'form-0-id': '1',
            'form-1-name': 'person2',
#            'form-1-image': image2,
#            'form-1-id': '2',
        }
        response = self.client.post('/{}/{}/{}/vote/edit/'.format(
            self.campaign.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug), data)
        self.assertRedirects(response, '/{}/{}/{}/'.format(
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug), 302, 200)

        vote_participants = models.VoteParticipant.objects.filter(campaign=self.campaign)
        self.assertEqual(len(vote_participants), 4)

        for vote_participant in vote_participants:
#            image = vote_participant.image
            response = self.client.get('/{}/{}/{}/'.format(self.campaign.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
#            self.assertContains(response, image.image.url, status_code=200)
            self.assertContains(response, vote_participant.name, status_code=200)

    def test_vote_general(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/{}/{}/vote/edit/'.format(
            self.campaign2.page.page_slug,
            self.campaign2.pk,
            self.campaign2.campaign_slug,
        ))
        self.assertEqual(response.status_code, 404)

    def test_campaign_ended(self):
        response = self.client.get('/{}/{}/{}/'.format(
            self.campaign3.page.page_slug,
            self.campaign3.pk,
            self.campaign3.campaign_slug,
        ))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Donate")

    def test_dashboard_donations(self):
        self.client.login(username='testuser', password='testpassword')
        response  = self.client.get('/{}/{}/{}/manage/donations/'.format(
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug,
        ))
        self.assertEqual(response.status_code, 200)

    def test_campaign_donations_all(self):
        response = self.client.get('/{}/{}/{}/donations/'.format(self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertContains(response, int(self.donation.amount / 100))
        self.assertContains(response, int(self.donation2.amount / 100))
        self.assertContains(response, int(self.donation3.amount / 100))
        self.assertContains(response, int(self.donation4.amount / 100))
        self.assertNotContains(response, int(self.donation5.amount / 100))
        self.assertNotContains(response, int(self.donation6.amount / 100))
