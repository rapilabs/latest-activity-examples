from django.db import models

from django_cte import CTEManager


class Activity(models.Model):
    objects = CTEManager()

    who = models.CharField(max_length=255)
    when = models.DateTimeField()
    what = models.CharField(max_length=255)

    def __str__(self):
        return '{} {} {}'.format(self.who, self.when, self.what)
