import urllib.request as urllib

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect

from guardian.shortcuts import assign_perm, get_user_perms, remove_perm
import sendgrid
from sendgrid.helpers.mail import *

from . import config, settings


def email(user_email, subject, body, template, substitutions):
    if not settings.TESTING:
        sg = sendgrid.SendGridAPIClient(apikey=config.settings["sendgrid_api_key"])
        templates = {
            'page_manager_invitation': 'd6a60dee-9e61-41e5-954e-0e049e95d0ed',
            'campaign_manager_invitation': '19f2f1f5-0559-4f27-a2c1-fd0fee5a3dc0',
            'new_campaign_created': 'd5952e1d-3672-4876-97a1-7b5ee3c2fef7',
            'new_campaign_created_admin': 'cb6099ff-d8a0-4f8c-a73e-05cdd92feb78',
            'new_page_created': '0ba093a3-5628-4da9-b3e5-267f9f0313c4',
            'new_user_signup': '0f0ff154-4a0e-48eb-b073-d59447ac67e8',
            'page_bank_information_updated': 'c988f1b2-ded9-476b-85a1-a7b1ec3a55e7',
            'pagefund_invitation': '09db718c-d1bb-446c-9cf5-67cd0adf0c97',
            'reset_password': '3fcbedb0-d54b-49b3-885e-856bbbaf21c8',
            'note_abuse': '2dc1a02e-cf7c-4e47-9989-ae32aefe662b',
            'donation': '5cbe8e19-d441-4fec-a880-464889239d86',
            'admin_new_user_signup': '0122d455-720c-4ee3-b5eb-70185fae4579',
            'admin_new_page': '41206bb2-1b0b-4b76-9240-08b02ac847a8',
            'admin_new_campaign': 'cabaff4b-9c8e-4965-8b80-2485688d6b5d',
            'admin_new_donation': '4abfaf11-3ab0-45bd-ba85-44330b8ca9c1',
            'note_error': 'e25c4a89-353a-434d-b24e-321cfd626113',
            'admin_webhook_test': '4ff6e428-bd27-4591-a4bc-9f6f6ca0c7d2',
            'email_confirmation': '969cdbf5-a4f1-4fb3-a1bc-91dfee474506',
            'email_confirmation_signup': '969cdbf5-a4f1-4fb3-a1bc-91dfee474506',
            'page_verification': '3e410b88-b917-42c0-9eb6-04820f32e5ac',
        }

        data = {
          "personalizations": [
            {
              "to": [
                {
                  "email": user_email
                }
              ],
              "substitutions": substitutions,
              "subject": subject
            },
          ],
          "from": {
            "email": "no-reply@page.fund"
          },
          "content": [
            {
              "type": "text/html",
              "value": body
            }
          ],
          "template_id": templates[template]
        }
        try:
            response = sg.client.mail.send.post(request_body=data)
        except urllib.HTTPError as e:
            print (e.read())
            exit()

def update_manager_permissions(post_data, obj):
    new_permissions = dict()
    # post_data contains the new permissions list
    # obj is the object that the permission is applied to
    for p in post_data:
        # m is the manager id
        m = p.split("_", 1)[0]
        # p is the permission
        p = p.split("_", 1)[1]
        # make sure this user is unique
        if m not in new_permissions:
            # create a new dictionary for this manager
            new_permissions[m] = []
        # at the end, we'll have a dictionary
        # with the manager id as the key
        # and their permissions as the values
        new_permissions[m].append(p)

    # get list of user's current perms
    old_permissions = dict()
    # k is they key, so it will be each manager id
    for k in new_permissions:
        # get the user with the corresponding id
        user = get_object_or_404(User, pk=k)
        # get the user permissions as a queryset
        user_permissions = get_user_perms(user, obj)
        # make sure this user is unique
        if k not in old_permissions:
            # create a new dictionary for this manager
            old_permissions[k] = []
        # add the user's current permissions
        # to the diciontary for comparison later
        for p in user_permissions:
            old_permissions[k].append(p)

    # for every item in the user's current perms,
    # compare to the new list of perms from the form
    # k is the manager id
    # v is the list of old permissions
    for k, v in old_permissions.items():
        # get the user based on the manager id
        user = get_object_or_404(User, pk=k)
        # for each permission in the list of old permissions
        for e in v:
            # if that item is in the list,
            # remove it from the new list
            # and do nothing to the perm
            if e in new_permissions[k]:
                new_permissions[k].remove(e)
            # if that item is not in the list,
            # remove the perm
            else:
                remove_perm(e, user, obj)
    # for every item in the new list,
    # give the user the perms for that item
    # k is the manager id
    # v is the list of new permissions
    for k, v in new_permissions.items():
        # get the user based on the manager id
        user = get_object_or_404(User, pk=k)
        # for each new permission,
        # assign the permission to the user
        for e in v:
            assign_perm(e, user, obj)

def donation_amount(initial_amount):
    stripe_fee = int(initial_amount * 0.029) + 30
    pagefund_fee = int(initial_amount * config.settings['pagefund_fee'])
    return initial_amount - stripe_fee - pagefund_fee

def has_dashboard_access(user, obj, permission):
    # user needs to be an admin,
    # or if there's a permission, then they need to be a manager with that permission.
    # otherwise, just a manager

    if user.userprofile.is_admin(obj):
        return True
    elif user.userprofile.is_manager(obj):
        if permission:
            if user.has_perm(permission, obj):
                return True
            else:
                return False
        else:
            return True
    else:
        return False

def get_content_type(pk):
    return ContentType.objects.get(pk=pk)

def has_notification(user, notification):
    # get a list of the user's enabled notifications
    # return True if notification is in list
    # return False if notification is not in list

    notification_preferences = user.userprofile.notification_preferences()
    if notification_preferences[notification]['value'] == True:
        return True
    else:
        return False
