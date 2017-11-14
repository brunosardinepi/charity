from django.db import models
from django.utils import timezone

from votes.models import Vote


class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return self.question[:10]

    def upvotes(self):
        return Vote.objects.filter(faq=self, score=1).count()

    def downvotes(self):
        return Vote.objects.filter(faq=self, score=-1).count()

    def score(self):
        return Vote.objects.filter(faq=self).aggregate(models.Sum('score')).get('score__sum')
