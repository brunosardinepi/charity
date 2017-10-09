from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from guardian.shortcuts import assign_perm, get_user_perms, remove_perm


def update_manager_permissions(post_data, type):
#    post_data = request.POST.getlist('permissions[]')
    new_permissions = dict()
    for p in post_data:
        m = p.split("_", 1)[0]
        p = p.split("_", 1)[1]
        if m not in new_permissions:
            new_permissions[m] = []
        new_permissions[m].append(p)

    # get list of user's current perms
    old_permissions = dict()
    for k in new_permissions:
        user = get_object_or_404(User, pk=k)
        user_permissions = get_user_perms(user, type)
        if k not in old_permissions:
            old_permissions[k] = []
        for p in user_permissions:
            old_permissions[k].append(p)

    # for every item in the user's current perms, compare to the new list of perms from the form
    for k, v in old_permissions.items():
        user = get_object_or_404(User, pk=k)
        for e in v:
            # if that item is in the list, remove it from the new list and do nothing to the perm
            if e in new_permissions[k]:
                new_permissions[k].remove(e)
            # if that item is not in the list, remove the perm
            else:
                remove_perm(e, user, type)
    # for every item in the new list, give the user the perms for that item
    for k,v in new_permissions.items():
        user = get_object_or_404(User, pk=k)
        for e in v:
            assign_perm(e, user, type)
