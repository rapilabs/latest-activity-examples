from datetime import datetime

from django.db.models import Subquery, OuterRef, Max, Window, F
from django.db.models.functions.window import FirstValue
from django.test import TestCase
from django_cte import With

from .models import Activity


class ActivityTestCase(TestCase):
    def setUp(self):
        Activity.objects.bulk_create((
            Activity(who='g1eb', when=datetime(2018, 1, 1, 9), what='Go to work'),
            Activity(who='g1eb', when=datetime(2018, 1, 1, 17), what='Knock-off time!'),
            Activity(who='shangxiao', when=datetime(2018, 1, 1, 9), what='Go to work'),
            Activity(who='shangxiao', when=datetime(2018, 1, 1, 17), what='Knock-off time!'),
            Activity(who='shangxiao', when=datetime(2018, 1, 1, 18), what='Attend MelbDjango'),
        ))

    def test_last_activity__app_level(self):
        final_activities = []
        prev = None
        for activity in Activity.objects.all():
            if prev and activity.who != prev.who:
                final_activities.append(prev)
            prev = activity
        final_activities.append(prev)

        print(len(final_activities))
        print(final_activities)

    def test_last_activity__subquery(self):
        max_when = Activity.objects \
            .values('who') \
            .filter(who=OuterRef('who')) \
            .annotate(max_when=Max('when'))
        final_activities = Activity.objects \
            .filter(when=Subquery(max_when.values('max_when')))
        print(final_activities.query)
        print(final_activities)

    def test_last_activity__cte(self):
        max_when = Activity.objects \
            .values('who') \
            .annotate(max_when=Max('when')) \
            .values('who', 'max_when')
        cte = With(max_when)
        final_activities = cte.join(Activity, who=cte.col.who, when=cte.col.max_when).with_cte(cte)
        print(final_activities.query)
        print(final_activities)

    def test_last_activity__window_function(self):
        final_activities = Activity.objects.annotate(max_when=Window(
            expression=FirstValue('when'),
            partition_by=[F('who')],
            order_by=F('when').desc(),
        ))

        # final1 = final_activities.filter(when=F('max_when'))
        # print(final1.query)
        # will produce an sql error as django attempts to put the window function in the where clause
        # print(final1)

        cte = With(final_activities)
        final2 = cte.join(Activity, who=cte.col.who, when=cte.col.max_when).with_cte(cte)
        print(final2.query)
        print(final2)
