"""
Comprehensive tests for the dashboard app.
Covers: Certificate model, dashboard views, access control.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Certificate
from accounts.models import UserProfile
from promotions.models import Campaign, Task, UserTask, Referral, RewardClaim


# ─── MODEL TESTS ────────────────────────────────────────────

class CertificateModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')

    def test_create_certificate(self):
        cert = Certificate.objects.create(
            user=self.user,
            recipient_name='Test User',
            award_amount=1000,
        )
        self.assertIn('SPP-', cert.certificate_id)
        self.assertIsNotNone(cert.verification_hash)
        self.assertEqual(len(cert.verification_hash), 64)

    def test_certificate_id_unique(self):
        c1 = Certificate.objects.create(user=self.user, recipient_name='A', award_amount=500)
        c2 = Certificate.objects.create(user=self.user, recipient_name='B', award_amount=1000)
        self.assertNotEqual(c1.certificate_id, c2.certificate_id)

    def test_formatted_amount(self):
        cert = Certificate.objects.create(user=self.user, recipient_name='T', award_amount=1500.50)
        self.assertEqual(cert.formatted_amount, '$1,500.50')

    def test_short_hash(self):
        cert = Certificate.objects.create(user=self.user, recipient_name='T', award_amount=100)
        self.assertEqual(len(cert.short_hash), 16)

    def test_default_description_generated(self):
        cert = Certificate.objects.create(
            user=self.user, recipient_name='Test', award_amount=1000,
            award_description='',  # Should be auto-filled
        )
        self.assertIn('SAMSUNG', cert.award_description)

    def test_amount_in_words(self):
        cert = Certificate.objects.create(user=self.user, recipient_name='T', award_amount=1500)
        words = cert._amount_in_words()
        self.assertIn('Thousand', words)

    def test_str_representation(self):
        cert = Certificate.objects.create(user=self.user, recipient_name='John Doe', award_amount=100)
        self.assertIn('John Doe', str(cert))


# ─── VIEW TESTS ─────────────────────────────────────────────

class DashboardAccessTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')
        UserProfile.objects.create(user=self.user)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_loads(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

    def test_tasks_page(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(reverse('dashboard:tasks'))
        self.assertEqual(response.status_code, 200)

    def test_referrals_page(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(reverse('dashboard:referrals'))
        self.assertEqual(response.status_code, 200)

    def test_rewards_page(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(reverse('dashboard:rewards'))
        self.assertEqual(response.status_code, 200)

    def test_certificates_list(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(reverse('dashboard:certificates'))
        self.assertEqual(response.status_code, 200)


class CertificateViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')
        self.cert = Certificate.objects.create(
            user=self.user, recipient_name='Test User',
            award_amount=1000, status='issued'
        )

    def test_certificate_view_loads(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(reverse('dashboard:certificate_view', args=[self.cert.pk]))
        self.assertEqual(response.status_code, 200)

    def test_certificate_print_loads(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(reverse('dashboard:certificate_print', args=[self.cert.pk]))
        self.assertEqual(response.status_code, 200)

    def test_certificate_other_user_404(self):
        other = User.objects.create_user('other', 'other@t.com', 'P!')
        self.client.login(username='other', password='P!')
        response = self.client.get(reverse('dashboard:certificate_view', args=[self.cert.pk]))
        self.assertEqual(response.status_code, 404)

    def test_certificate_verify_valid(self):
        hash_prefix = self.cert.verification_hash[:16]
        response = self.client.get(reverse('dashboard:certificate_verify', args=[hash_prefix]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')

    def test_certificate_verify_invalid(self):
        response = self.client.get(reverse('dashboard:certificate_verify', args=['invalidhash12345']))
        self.assertEqual(response.status_code, 200)
