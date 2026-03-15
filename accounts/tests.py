"""
Comprehensive tests for the accounts app.
Covers: models, registration, login/logout, profile, email/phone verification.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, EmailVerification, PhoneVerification


# ─── MODEL TESTS ────────────────────────────────────────────

class UserProfileModelTest(TestCase):
    """Test UserProfile model creation, referral codes, and verification logic."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='TestPass123!'
        )

    def test_profile_auto_created_via_view(self):
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        self.assertTrue(created)
        self.assertEqual(profile.user, self.user)

    def test_referral_code_generated(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertIsNotNone(profile.referral_code)
        self.assertEqual(len(profile.referral_code), 10)

    def test_referral_code_is_unique(self):
        profile1 = UserProfile.objects.create(user=self.user)
        user2 = User.objects.create_user('user2', 'u2@test.com', 'Pass123!')
        profile2 = UserProfile.objects.create(user=user2)
        self.assertNotEqual(profile1.referral_code, profile2.referral_code)

    def test_verification_progress_zero(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(profile.verification_progress, 0)

    def test_verification_progress_half(self):
        profile = UserProfile.objects.create(user=self.user, email_verified=True)
        self.assertEqual(profile.verification_progress, 50)

    def test_verification_progress_full(self):
        profile = UserProfile.objects.create(
            user=self.user, email_verified=True, phone_verified=True
        )
        self.assertTrue(profile.is_verified)
        self.assertEqual(profile.verification_progress, 100)

    def test_str_representation(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertIn('testuser', str(profile))


class EmailVerificationModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')

    def test_otp_auto_generated(self):
        verification = EmailVerification.objects.create(user=self.user)
        self.assertEqual(len(verification.otp_code), 6)
        self.assertTrue(verification.otp_code.isdigit())

    def test_token_auto_generated(self):
        verification = EmailVerification.objects.create(user=self.user)
        self.assertTrue(len(verification.token) > 0)

    def test_expires_at_auto_set(self):
        verification = EmailVerification.objects.create(user=self.user)
        self.assertIsNotNone(verification.expires_at)

    def test_is_expired_false_when_fresh(self):
        verification = EmailVerification.objects.create(user=self.user)
        self.assertFalse(verification.is_expired)

    def test_is_expired_true_when_old(self):
        verification = EmailVerification.objects.create(user=self.user)
        verification.expires_at = timezone.now() - timedelta(minutes=1)
        verification.save()
        self.assertTrue(verification.is_expired)


class PhoneVerificationModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')

    def test_otp_auto_generated(self):
        verification = PhoneVerification.objects.create(
            user=self.user, phone_number='+2348001234567'
        )
        self.assertEqual(len(verification.otp_code), 6)
        self.assertTrue(verification.otp_code.isdigit())

    def test_expiry_set(self):
        before = timezone.now()
        verification = PhoneVerification.objects.create(
            user=self.user, phone_number='+2348001234567'
        )
        self.assertGreater(verification.expires_at, before)


# ─── VIEW TESTS ─────────────────────────────────────────────

class RegistrationViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('accounts:register')

    def test_register_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_successful_registration(self):
        response = self.client.post(self.url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'phone': '+2348001234567',
            'location': 'Lagos, Nigeria',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())

    def test_password_mismatch(self):
        response = self.client.post(self.url, {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'Pass123!',
            'password2': 'Different!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_duplicate_username(self):
        User.objects.create_user('existinguser', 'e@test.com', 'Pass!')
        response = self.client.post(self.url, {
            'username': 'existinguser',
            'email': 'new@test.com',
            'password': 'Pass123!',
            'password2': 'Pass123!',
        })
        self.assertEqual(response.status_code, 200)

    def test_duplicate_email(self):
        User.objects.create_user('user1', 'taken@test.com', 'Pass!')
        response = self.client.post(self.url, {
            'username': 'user2',
            'email': 'taken@test.com',
            'password': 'Pass123!',
            'password2': 'Pass123!',
        })
        self.assertEqual(response.status_code, 200)

    def test_referral_code_awards_points(self):
        referrer = User.objects.create_user('referrer', 'ref@test.com', 'Pass!')
        referrer_profile = UserProfile.objects.create(user=referrer)
        ref_code = referrer_profile.referral_code

        self.client.post(self.url, {
            'username': 'referred_user',
            'email': 'referred@test.com',
            'password': 'Pass123!',
            'password2': 'Pass123!',
            'referral_code': ref_code,
        })
        referrer_profile.refresh_from_db()
        self.assertEqual(referrer_profile.points, 100)

    def test_authenticated_user_redirected(self):
        User.objects.create_user('u', 'u@t.com', 'P!')
        self.client.login(username='u', password='P!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class LoginLogoutViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')

    def test_login_page_loads(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_valid_login(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser', 'password': 'Pass123!',
        })
        self.assertEqual(response.status_code, 302)

    def test_invalid_login(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser', 'password': 'WrongPass!',
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)


class ProfileViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')
        self.url = reverse('accounts:profile')

    def test_profile_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_profile_loads(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_profile_update(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.post(self.url, {
            'first_name': 'Test', 'last_name': 'User',
            'phone': '+2348001234567', 'location': 'Lagos',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')


class EmailVerificationViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.login(username='testuser', password='Pass123!')

    def test_verify_email_page_loads(self):
        response = self.client.get(reverse('accounts:verify_email_page'))
        self.assertEqual(response.status_code, 200)

    def test_valid_otp_verifies_email(self):
        verification = EmailVerification.objects.create(user=self.user)
        response = self.client.post(reverse('accounts:verify_email_page'), {
            'otp_code': verification.otp_code,
        })
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.email_verified)

    def test_invalid_otp_rejected(self):
        response = self.client.post(reverse('accounts:verify_email_page'), {
            'otp_code': '000000',
        })
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.email_verified)

    def test_expired_otp_rejected(self):
        verification = EmailVerification.objects.create(user=self.user)
        verification.expires_at = timezone.now() - timedelta(hours=1)
        verification.save()
        self.client.post(reverse('accounts:verify_email_page'), {
            'otp_code': verification.otp_code,
        })
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.email_verified)

    def test_already_verified_redirects(self):
        self.profile.email_verified = True
        self.profile.save()
        response = self.client.get(reverse('accounts:verify_email_page'))
        self.assertEqual(response.status_code, 302)

    def test_resend_otp(self):
        response = self.client.get(reverse('accounts:resend_email_otp'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(EmailVerification.objects.filter(user=self.user).exists())

    def test_verify_email_link(self):
        verification = EmailVerification.objects.create(user=self.user)
        response = self.client.get(
            reverse('accounts:verify_email_link', args=[verification.token])
        )
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.email_verified)


class PhoneVerificationViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Pass123!')
        self.profile = UserProfile.objects.create(user=self.user, phone='+2348001234567')
        self.client.login(username='testuser', password='Pass123!')

    def test_verify_phone_page_loads(self):
        response = self.client.get(reverse('accounts:verify_phone_page'))
        self.assertEqual(response.status_code, 200)

    def test_send_otp_step(self):
        response = self.client.post(reverse('accounts:verify_phone_page'), {
            'action': 'send_otp', 'phone_number': '+2348001234567',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(PhoneVerification.objects.filter(user=self.user).exists())

    def test_valid_phone_otp_verifies(self):
        verification = PhoneVerification.objects.create(
            user=self.user, phone_number='+2348001234567'
        )
        response = self.client.post(reverse('accounts:verify_phone_page'), {
            'action': 'verify_otp',
            'phone_number': '+2348001234567',
            'otp_code': verification.otp_code,
        })
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.phone_verified)
