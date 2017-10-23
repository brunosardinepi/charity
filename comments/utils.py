from django.utils import timezone


def comment_attributes(comment):
    response_data = {}
    response_data['content'] = comment.content
    response_data['user'] = "%s %s" % (comment.user.first_name, comment.user.last_name)
    response_data['date'] = timezone.localtime(comment.date)
    response_data['date'] = response_data['date'].strftime('%m/%d/%y %-I:%M %p')
    response_data['id'] = comment.pk
    return response_data
