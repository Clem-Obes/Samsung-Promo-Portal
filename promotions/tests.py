"""
Comprehensive tests for the promotions app.
Covers: Campaign, Task, UserTask, Referral, RewardClaim models and views.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Campaign, Task, UserTask, Referral, RewardClaim


# ─── MODEL TESTS ────────────────────────────────────────────

class CampaignModelTest(TestCase):

    def test_create_campaign(self):
        c = Campaign.objects.create(
            title='Galaxy Promo', description='Win big!',
            start_date=timezone.now(), end_date=timezone.now() + timedelta(days=30),
        )
        self.assertEqual(str(c), 'Galaxy Promo')
        self.assertEqual(c.status, 'upcoming')


class TaskModelTest(TestCase):

    def test_create_task(self):
        campaign = Campaign.objects.create(
            title='Camp', description='Desc',
            start_date=timezone.now(), end_date=timezone.now() + timedelta(days=30),
        )
        task = Task.objects.create(
            campaign=campaign, title='Share Product', task_type='share', points=20
        )
        self.assertEqual(str(task), 'Share Product')
        self.assertEqual(task.points, 20)


class UserTaskModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')
        self.campaign = Campaign.objects.create(
            title='Camp', description='D',
            start_date=timezone.now(), end_date=timezone.now() + timedelta(days=30),
        )
        self.task = Task.objects.create(
            campaign=self.campaign, title='Task', task_type='share', points=10
        )

    def test_create_user_task(self):
        ut = UserTask.objects.create(user=self.user, task=self.task)
        self.assertEqual(ut.status, 'pending')
        self.assertIn('testuser', str(ut))

    def test_unique_user_task(self):
        UserTask.objects.create(user=self.user, task=self.task)
        with self.assertRaises(Exception):
            UserTask.objects.create(user=self.user, task=self.task)


class ReferralModelTest(TestCase):

    def test_create_referral(self):
        u1 = User.objects.create_user('u1', 'u1@t.com', 'P!')
        u2 = User.objects.create_user('u2', 'u2@t.com', 'P!')
        ref = Referral.objects.create(referrer=u1, referred=u2)
        self.assertIn('u1', str(ref))
        self.assertIn('u2', str(ref))


class RewardClaimModelTest(TestCase):

    def test_create_claim(self):
        user = User.objects.create_user('u', 'u@t.com', 'P!')
        campaign = Campaign.objects.create(
            title='C', description='D',
            start_date=timezone.now(), end_date=timezone.now() + timedelta(days=30),
        )
        claim = RewardClaim.objects.create(user=user, campaign=campaign)
        self.assertEqual(claim.status, 'pending')


# ─── VIEW TESTS ─────────────────────────────────────────────

class CampaignViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.campaign = Campaign.objects.create(
            title='Test Campaign', description='Description',
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            status='active',
        )
        self.task = Task.objects.create(
            campaign=self.campaign, title='Share Post', task_type='share', points=10
        )

    def test_campaigns_list(self):
        response = self.client.get(reverse('promotions:campaigns'))
        self.assertEqual(response.status_code, 200)

    def test_campaign_detail(self):
        response = self.client.get(reverse('promotions:campaign_detail', args=[self.campaign.pk]))
        self.assertEqual(response.status_code, 200)

    def test_campaign_detail_404(self):
        response = self.client.get(reverse('promotions:campaign_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)


class TaskInteractionTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')
        self.campaign = Campaign.objects.create(
            title='Active Camp', description='D',
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            status='active',
        )
        self.task = Task.objects.create(
            campaign=self.campaign, title='Task', task_type='share', points=10
        )

    def test_join_task_requires_login(self):
        response = self.client.get(reverse('promotions:join_task', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)

    def test_join_task(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(reverse('promotions:join_task', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserTask.objects.filter(user=self.user, task=self.task).exists())

    def test_complete_task(self):
        self.client.login(username='testuser', password='Pass123!')
        UserTask.objects.create(user=self.user, task=self.task, status='pending')
        response = self.client.post(
            reverse('promotions:complete_task', args=[self.task.pk]),
            {'proof': 'https://twitter.com/screenshot'}
        )
        self.assertEqual(response.status_code, 302)
        ut = UserTask.objects.get(user=self.user, task=self.task)
        self.assertEqual(ut.status, 'completed')

    def test_complete_without_proof_fails(self):
        self.client.login(username='testuser', password='Pass123!')
        UserTask.objects.create(user=self.user, task=self.task, status='pending')
        response = self.client.post(
            reverse('promotions:complete_task', args=[self.task.pk]),
            {'proof': ''}
        )
        ut = UserTask.objects.get(user=self.user, task=self.task)
        self.assertEqual(ut.status, 'pending')

    def test_claim_reward_requires_all_verified(self):
        self.client.login(username='testuser', password='Pass123!')
        UserTask.objects.create(user=self.user, task=self.task, status='pending')
        response = self.client.get(
            reverse('promotions:claim_reward', args=[self.campaign.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RewardClaim.objects.filter(user=self.user).exists())

    def test_claim_reward_success(self):
        self.client.login(username='testuser', password='Pass123!')
        UserTask.objects.create(user=self.user, task=self.task, status='verified')
        response = self.client.get(
            reverse('promotions:claim_reward', args=[self.campaign.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(RewardClaim.objects.filter(user=self.user, campaign=self.campaign).exists())

    def test_duplicate_claim_prevented(self):
        self.client.login(username='testuser', password='Pass123!')
        UserTask.objects.create(user=self.user, task=self.task, status='verified')
        RewardClaim.objects.create(user=self.user, campaign=self.campaign)
        response = self.client.get(
            reverse('promotions:claim_reward', args=[self.campaign.pk])
        )
        self.assertEqual(RewardClaim.objects.filter(user=self.user, campaign=self.campaign).count(), 1)
