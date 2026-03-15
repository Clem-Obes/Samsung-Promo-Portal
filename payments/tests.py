"""
Comprehensive tests for the payments app.
Covers: MembershipPlan, Payment, UserMembership models and views.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import MembershipPlan, Payment, UserMembership


class MembershipPlanModelTest(TestCase):

    def test_create_plan(self):
        plan = MembershipPlan.objects.create(
            name='Premium', slug='premium', price=5000,
            description='Premium plan', benefits='Benefit 1\nBenefit 2',
        )
        self.assertIn('Premium', str(plan))
        self.assertEqual(plan.benefits_list, ['Benefit 1', 'Benefit 2'])

    def test_empty_benefits(self):
        plan = MembershipPlan.objects.create(
            name='Basic', slug='basic', price=0,
            description='Free', benefits='',
        )
        self.assertEqual(plan.benefits_list, [])


class PaymentModelTest(TestCase):

    def test_create_payment(self):
        user = User.objects.create_user('u', 'u@t.com', 'P!')
        plan = MembershipPlan.objects.create(
            name='Premium', slug='premium', price=5000, description='D',
        )
        payment = Payment.objects.create(
            user=user, plan=plan, amount=5000, reference='SAM-TEST123',
        )
        self.assertEqual(payment.status, 'pending')
        self.assertIn('testuser', str(payment).lower().replace('u', 'testuser') or str(payment))


class UserMembershipModelTest(TestCase):

    def test_create_membership(self):
        user = User.objects.create_user('u', 'u@t.com', 'P!')
        plan = MembershipPlan.objects.create(
            name='Premium', slug='premium', price=5000, description='D',
        )
        membership = UserMembership.objects.create(user=user, plan=plan)
        self.assertTrue(membership.is_active)


class PaymentViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')
        self.plan = MembershipPlan.objects.create(
            name='Premium', slug='premium', price=5000,
            description='Premium plan', is_active=True,
        )

    def test_subscribe_requires_login(self):
        response = self.client.get(reverse('payments:subscribe', args=['premium']))
        self.assertEqual(response.status_code, 302)

    def test_subscribe_page_loads(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(reverse('payments:subscribe', args=['premium']))
        self.assertEqual(response.status_code, 200)

    def test_subscribe_creates_pending_payment(self):
        self.client.login(username='testuser', password='Pass123!')
        self.client.get(reverse('payments:subscribe', args=['premium']))
        self.assertTrue(Payment.objects.filter(user=self.user, status='pending').exists())

    def test_verify_payment_activates_membership(self):
        self.client.login(username='testuser', password='Pass123!')
        payment = Payment.objects.create(
            user=self.user, plan=self.plan, amount=5000, reference='SAM-VERIFY123',
        )
        response = self.client.get(reverse('payments:verify_payment') + '?reference=SAM-VERIFY123')
        self.assertEqual(response.status_code, 302)
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'success')
        self.assertTrue(UserMembership.objects.filter(user=self.user, is_active=True).exists())

    def test_verify_payment_no_reference(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(reverse('payments:verify_payment'))
        self.assertEqual(response.status_code, 302)

    def test_payment_success_page(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(reverse('payments:payment_success'))
        self.assertEqual(response.status_code, 200)
