import django

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.http import Http404
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from guardian.shortcuts import assign_perm

import unittest

from . import forms
from . import models
from . import views
from campaign import models as CampaignModels


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
            username='harrypotter',
            email='harry@potter.com',
            password='imawizard'
        )

        self.user3 = User.objects.create_user(
            username='bobdole',
            email='bob@dole.com',
            password='dogsarecool'
        )

        self.user4 = User.objects.create_user(
            username='batman',
            email='batman@bat.cave',
            password='imbatman'
        )

        self.page = models.Page.objects.create(
            name='Test Page',
            description='This is a description for Test Page.',
            donation_count='20',
            donation_money='30',
            category='Animal'
        )
        self.page.admins.add(self.user.userprofile)
        self.page.subscribers.add(self.user.userprofile)
        self.page.managers.add(self.user3.userprofile)
        self.page.managers.add(self.user4.userprofile)
        assign_perm('manager_edit_page', self.user3, self.page)
        assign_perm('manager_delete_page', self.user3, self.page)
        assign_perm('manager_invite_page', self.user3, self.page)

        self.campaign = CampaignModels.Campaign.objects.create(
            name='Test Campaign',
            user=self.user,
            page=self.page,
            description='This is a description for Test Campaign.',
            goal='11',
            donation_count='21',
            donation_money='31'
        )

        self.campaign2 = CampaignModels.Campaign.objects.create(
            name='Another One',
            user=self.user2,
            page=self.page,
            description='My cat died yesterday',
            goal='12',
            donation_count='22',
            donation_money='33'
        )

    def test_page_exists(self):
        pages = models.Page.objects.all()
        self.assertIn(self.page, pages)

    def test_page_status_logged_out(self):
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.page(request, self.page.page_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.user.first_name, status_code=200)
        self.assertContains(response, self.user.last_name, status_code=200)
        self.assertContains(response, self.page.description, status_code=200)
        self.assertContains(response, self.page.donation_count, status_code=200)
        self.assertContains(response, self.page.donation_money, status_code=200)
        self.assertContains(response, self.page.category, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign.goal, status_code=200)
        self.assertContains(response, self.campaign.donation_money, status_code=200)
        self.assertContains(response, self.campaign2.name, status_code=200)
        self.assertContains(response, self.campaign2.goal, status_code=200)
        self.assertContains(response, self.campaign2.donation_money, status_code=200)

    def test_page_status_logged_in(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.page(request, self.page.page_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.user.first_name, status_code=200)
        self.assertContains(response, self.user.last_name, status_code=200)
        self.assertContains(response, self.page.description, status_code=200)
        self.assertContains(response, self.page.donation_count, status_code=200)
        self.assertContains(response, self.page.donation_money, status_code=200)
        self.assertContains(response, self.page.category, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign.goal, status_code=200)
        self.assertContains(response, self.campaign.donation_money, status_code=200)
        self.assertContains(response, self.campaign2.name, status_code=200)
        self.assertContains(response, self.campaign2.goal, status_code=200)
        self.assertContains(response, self.campaign2.donation_money, status_code=200)

    def test_page_admin_logged_out(self):
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.page(request, self.page.page_slug)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Admin", status_code=200)
        self.assertNotContains(response, "Edit Page", status_code=200)
        self.assertNotContains(response, "Delete Page", status_code=200)
        self.assertNotContains(response, "Manager", status_code=200)
        self.assertNotContains(response, "Invite others to manage Page", status_code=200)

    def test_page_admin_logged_in(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.page(request, self.page.page_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin", status_code=200)
        self.assertContains(response, "Edit Page", status_code=200)
        self.assertContains(response, "Delete Page", status_code=200)

    def test_page_edit_logged_out(self):
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.page_edit(request, self.page.page_slug)

        self.assertEqual(response.status_code, 302)

    @unittest.expectedFailure
    def test_page_edit_not_admin(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.page_edit(request, self.page.page_slug)

    def test_page_edit_admin(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.page_edit(request, self.page.page_slug)

        self.assertEqual(response.status_code, 200)

    def test_page_edit_manager_perms(self):
        request = self.factory.get('home')
        request.user = self.user3
        response = views.page_edit(request, self.page.page_slug)

        self.assertEqual(response.status_code, 200)

    @unittest.expectedFailure
    def test_page_edit_manager_no_perms(self):
        request = self.factory.get('home')
        request.user = self.user4
        response = views.page_edit(request, self.page.page_slug)

    def test_page_not_subscribed(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.page(request, self.page.page_slug)

        self.assertContains(response, 'name="subscribe"', status_code=200)

    def test_page_subscribed(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.page(request, self.page.page_slug)

        self.assertContains(response, 'name="unsubscribe"', status_code=200)

    def test_page_subscribe_redirect(self):
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.subscribe(request, self.page.pk, action="subscribe")

        self.assertEqual(response.status_code, 302)

    def test_page_create_logged_out(self):
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.page_create(request)

        self.assertEqual(response.status_code, 302)

    def test_page_create_logged_in(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.page_create(request)

        self.assertEqual(response.status_code, 200)

    def test_pageform(self):
        form = forms.PageForm({
            'name': 'Ribeye Steak',
            'page_slug': 'ribeyesteak',
            'category': 'animal',
            'description': 'I like flank steak.'
        })
        self.assertTrue(form.is_valid())
        page = form.save()
        self.assertEqual(page.name, "Ribeye Steak")
        self.assertEqual(page.page_slug, "ribeyesteak")
        self.assertEqual(page.category, "animal")
        self.assertEqual(page.description, "I like flank steak.")

    def test_pageform_blank(self):
        form = forms.PageForm({})
        self.assertFalse(form.is_valid())

    def test_deletepageform(self):
        form = forms.DeletePageForm({
            'name': self.page
        })
        self.assertTrue(form.is_valid())

    def test_delete_page_logged_out(self):
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.page_delete(request, self.page.page_slug)

        self.assertEqual(response.status_code, 302)

    def test_delete_page_admin(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.page_delete(request, self.page.page_slug)

        self.assertContains(response, self.page.name, status_code=200)

    @unittest.expectedFailure
    def test_delete_page_not_admin(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.page_delete(request, self.page.page_slug)

    def test_delete_page_manager_perms(self):
        request = self.factory.get('home')
        request.user = self.user3
        response = views.page_delete(request, self.page.page_slug)

        self.assertContains(response, self.page.name, status_code=200)

    @unittest.expectedFailure
    def test_delete_page_manager_no_perms(self):
        request = self.factory.get('home')
        request.user = self.user4
        response = views.page_delete(request, self.page.page_slug)
