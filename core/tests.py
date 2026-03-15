"""
Comprehensive tests for the core app.
Covers: models, public pages, contact form, testimonials, newsletter.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import (
    Device, Testimonial, SiteSettings, Announcement,
    TestimonyComment, NewsletterSubscriber,
)


# ─── MODEL TESTS ────────────────────────────────────────────

class DeviceModelTest(TestCase):

    def test_create_device(self):
        device = Device.objects.create(name='Galaxy S24 Ultra', price=1299.99)
        self.assertEqual(str(device), 'Galaxy S24 Ultra')
        self.assertEqual(device.price, 1299.99)

    def test_featured_filter(self):
        Device.objects.create(name='Featured', is_featured=True)
        Device.objects.create(name='Not Featured', is_featured=False)
        self.assertEqual(Device.objects.filter(is_featured=True).count(), 1)


class TestimonialModelTest(TestCase):

    def test_create_testimonial(self):
        t = Testimonial.objects.create(
            name='John', location='Lagos', quote='Amazing!', rating=5
        )
        self.assertIn('John', str(t))
        self.assertEqual(t.status, 'pending')

    def test_approved_filter(self):
        Testimonial.objects.create(name='A', location='X', quote='Y', status='approved')
        Testimonial.objects.create(name='B', location='X', quote='Y', status='pending')
        self.assertEqual(Testimonial.objects.filter(status='approved').count(), 1)


class SiteSettingsModelTest(TestCase):

    def test_create_settings(self):
        s = SiteSettings.objects.create()
        self.assertEqual(str(s), 'Samsung Promo Portal')


class AnnouncementModelTest(TestCase):

    def test_create_announcement(self):
        a = Announcement.objects.create(title='Big News', content='Content here')
        self.assertEqual(str(a), 'Big News')
        self.assertTrue(a.is_active)


class TestimonyCommentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')

    def test_create_comment(self):
        c = TestimonyComment.objects.create(user=self.user, text='Great experience!')
        self.assertIn('testuser', str(c))

    def test_like_count(self):
        c = TestimonyComment.objects.create(user=self.user, text='Test')
        self.assertEqual(c.like_count, 0)
        user2 = User.objects.create_user('user2', 'u2@t.com', 'P!')
        c.likes.add(user2)
        self.assertEqual(c.like_count, 1)


class NewsletterSubscriberModelTest(TestCase):

    def test_create_subscriber(self):
        s = NewsletterSubscriber.objects.create(email='test@example.com')
        self.assertEqual(str(s), 'test@example.com')

    def test_unique_email(self):
        NewsletterSubscriber.objects.create(email='dup@test.com')
        with self.assertRaises(Exception):
            NewsletterSubscriber.objects.create(email='dup@test.com')


# ─── PUBLIC PAGE TESTS ──────────────────────────────────────

class PublicPageTests(TestCase):
    """Test all public-facing pages return 200."""

    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_testimonials_page(self):
        response = self.client.get(reverse('core:testimonials'))
        self.assertEqual(response.status_code, 200)

    def test_how_it_works_page(self):
        response = self.client.get(reverse('core:how_it_works'))
        self.assertEqual(response.status_code, 200)

    def test_pricing_page(self):
        response = self.client.get(reverse('core:pricing'))
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)

    def test_contact_page(self):
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)

    def test_privacy_policy(self):
        response = self.client.get(reverse('core:privacy_policy'))
        self.assertEqual(response.status_code, 200)

    def test_terms_of_service(self):
        response = self.client.get(reverse('core:terms_of_service'))
        self.assertEqual(response.status_code, 200)

    def test_cookie_policy(self):
        response = self.client.get(reverse('core:cookie_policy'))
        self.assertEqual(response.status_code, 200)


class ContactFormTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('core:contact')

    def test_contact_form_submission(self):
        response = self.client.post(self.url, {
            'name': 'Test User',
            'email': 'test@test.com',
            'subject': 'Test Subject',
            'message': 'This is a test message',
        })
        self.assertEqual(response.status_code, 302)
        from support.models import ContactMessage
        self.assertTrue(ContactMessage.objects.filter(subject='Test Subject').exists())

    def test_authenticated_user_contact(self):
        user = User.objects.create_user('u', 'u@t.com', 'P!')
        self.client.login(username='u', password='P!')
        self.client.post(self.url, {
            'name': 'User', 'email': 'u@t.com',
            'subject': 'Authed', 'message': 'Test',
        })
        from support.models import ContactMessage
        msg = ContactMessage.objects.get(subject='Authed')
        self.assertEqual(msg.user, user)


class NewsletterTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('core:newsletter_subscribe')

    def test_subscribe_new_email(self):
        response = self.client.post(self.url, {'email': 'new@test.com'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(NewsletterSubscriber.objects.filter(email='new@test.com').exists())

    def test_duplicate_email_no_error(self):
        NewsletterSubscriber.objects.create(email='dup@test.com')
        response = self.client.post(self.url, {'email': 'dup@test.com'})
        self.assertEqual(response.status_code, 302)

    def test_reactivate_inactive(self):
        sub = NewsletterSubscriber.objects.create(email='re@test.com', is_active=False)
        self.client.post(self.url, {'email': 're@test.com'})
        sub.refresh_from_db()
        self.assertTrue(sub.is_active)


class TestimonialCommentTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')

    def test_like_requires_login(self):
        comment = TestimonyComment.objects.create(user=self.user, text='Test', status='approved')
        response = self.client.get(reverse('core:like_testimony', args=[comment.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_like_toggle(self):
        self.client.login(username='testuser', password='Pass123!')
        comment = TestimonyComment.objects.create(user=self.user, text='Test', status='approved')
        # Like
        response = self.client.get(reverse('core:like_testimony', args=[comment.pk]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['liked'])
        self.assertEqual(data['count'], 1)
        # Unlike
        response = self.client.get(reverse('core:like_testimony', args=[comment.pk]))
        data = response.json()
        self.assertFalse(data['liked'])
        self.assertEqual(data['count'], 0)
