# -*- coding: utf8 -*-
from datetime import datetime

from nose.tools import eq_
from pyquery import PyQuery as pq
import test_utils

import amo
from amo.urlresolvers import reverse
from addons.models import Addon
from devhub.models import ActivityLog
from reviews.models import Review
from users.models import UserProfile


class EditorTest(test_utils.TestCase):
    fixtures = ('base/users', 'editors/pending-queue')

    def login_as_editor(self):
        assert self.client.login(username='editor@mozilla.com',
                                 password='password')

    def make_review(self, username='a'):
        u = UserProfile.objects.create(username=username)
        a = Addon.objects.create(name='yermom', type=amo.ADDON_EXTENSION)
        return Review.objects.create(user=u, addon=a)


class TestEventLog(EditorTest):
    def setUp(self):
        self.login_as_editor()
        amo.set_user(UserProfile.objects.get(username='editor'))
        review = self.make_review()
        for i in xrange(30):
            amo.log(amo.LOG.APPROVE_REVIEW, review, review.addon)
            amo.log(amo.LOG.DELETE_REVIEW, review.id, review.addon)

    def test_log(self):
        r = self.client.get(reverse('editors.eventlog'))
        eq_(r.status_code, 200)

    def test_start_filter(self):
        r = self.client.get(reverse('editors.eventlog') + '?start=3011-01-01')
        eq_(r.status_code, 200)
        doc = pq(r.content)
        assert doc('tbody')
        eq_(len(doc('tbody tr')), 0)

    def test_enddate_filter(self):
        """
        Make sure that if our end date is 1/1/2011, that we include items from
        1/1/2011.  To not do as such would be dishonorable.
        """
        review = self.make_review(username='b')
        amo.log(amo.LOG.APPROVE_REVIEW, review, review.addon,
                created=datetime(2011, 1, 1))

        r = self.client.get(reverse('editors.eventlog') + '?end=2011-01-01')
        eq_(r.status_code, 200)
        doc = pq(r.content)
        eq_(doc('tbody td').eq(0).text(), 'Jan 1, 2011 12:00:00 AM')

    def test_action_filter(self):
        """
        Based on setup we should only see 30 items if we filter for deleted
        reviews.
        """
        r = self.client.get(reverse('editors.eventlog') + '?filter=deleted')
        doc = pq(r.content)
        eq_(len(doc('tbody tr')), 30)


class TestEventLogDetail(TestEventLog):
    def test_me(self):
        id = ActivityLog.objects.editor_events()[0].id
        r = self.client.get(reverse('editors.eventlog.detail', args=[id]))
        eq_(r.status_code, 200)


class TestHome(EditorTest):
    """Test the page at /editors."""
    def setUp(self):
        self.login_as_editor()
        amo.set_user(UserProfile.objects.get(username='editor'))

    def test_approved_review(self):
        review = self.make_review()
        amo.log(amo.LOG.APPROVE_REVIEW, review, review.addon)
        r = self.client.get(reverse('editors.home'))
        doc = pq(r.content)
        eq_(doc('.row').eq(0).text().strip().split('.')[0],
            'editor approved Review for yermom ')

    def test_deleted_review(self):
        review = self.make_review()
        amo.log(amo.LOG.DELETE_REVIEW, review.id, review.addon)
        r = self.client.get(reverse('editors.home'))
        doc = pq(r.content)
        eq_(doc('.row').eq(0).text().strip().split('.')[0],
            'editor deleted review %d' % review.id)


class TestPendingQueue(EditorTest):
    def setUp(self):
        super(TestPendingQueue, self).setUp()
        self.login_as_editor()

    def test_only_viewable_by_editor(self):
        self.client.logout()
        assert self.client.login(username='regular@mozilla.com',
                                 password='password')
        r = self.client.get(reverse('editors.queue_pending'))
        eq_(r.status_code, 403)

    def test_invalid_page(self):
        r = self.client.get(reverse('editors.queue_pending'),
                            data={'page': 999})
        eq_(r.status_code, 200)
        eq_(r.context['page'].number, 1)

    def test_grid(self):
        r = self.client.get(reverse('editors.queue_pending'))
        eq_(r.status_code, 200)
        doc = pq(r.content)
        eq_(doc('div.section table tr th:eq(0)').text(), u'Addon')
        eq_(doc('div.section table tr th:eq(1)').text(), u'Type')
        eq_(doc('div.section table tr th:eq(2)').text(), u'Waiting Time')
        eq_(doc('div.section table tr th:eq(3)').text(), u'Applications')
        eq_(doc('div.section table tr th:eq(4)').text(), u'Flags')
        eq_(doc('div.section table tr th:eq(5)').text(),
            u'Additional Information')
        # Smoke test the grid. More tests in test_helpers.py
        row = doc('div.section table tr:eq(1)')
        eq_(doc('td:eq(0)', row).text(), u'Converter 1.0.0')
        eq_(doc('td a:eq(0)', row).attr('href'),
            reverse('editors.review', args=['118409']) + '?num=1')
        row = doc('div.section table tr:eq(2)')
        eq_(doc('td:eq(0)', row).text(), u'Better Facebook! 4.105')
        eq_(doc('a:eq(0)', row).attr('href'),
            reverse('editors.review', args=['118467']) + '?num=2')

    def test_redirect_to_review(self):
        r = self.client.get(reverse('editors.queue_pending'), data={'num': 2})
        self.assertRedirects(r, reverse('editors.review',
                                        args=['118467']) + '?num=2')

    def test_invalid_review_ignored(self):
        r = self.client.get(reverse('editors.queue_pending'), data={'num': 9})
        eq_(r.status_code, 200)

    def test_garbage_review_num_ignored(self):
        r = self.client.get(reverse('editors.queue_pending'),
                            data={'num': 'not-a-number'})
        eq_(r.status_code, 200)

    def test_queue_count(self):
        r = self.client.get(reverse('editors.queue_pending'))
        eq_(r.status_code, 200)
        doc = pq(r.content)
        eq_(doc('.tabnav li a:eq(1)').text(), u'Pending Updates (2)')
        eq_(doc('.tabnav li a:eq(1)').attr('href'),
            reverse('editors.queue_pending'))
