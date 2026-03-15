from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import random
import string


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    is_ambassador = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = uuid.uuid4().hex[:10].upper()
        # Auto-update is_verified when both email and phone are verified
        if self.email_verified and self.phone_verified:
            self.is_verified = True
        super().save(*args, **kwargs)

    @property
    def referral_count(self):
        return self.referrals.count()

    @property
    def verification_progress(self):
        """Returns percentage of verification steps completed."""
        steps = 0
        if self.email_verified:
            steps += 1
        if self.phone_verified:
            steps += 1
        return int((steps / 2) * 100)


class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    token = models.CharField(max_length=100, unique=True)
    otp_code = models.CharField(max_length=6, blank=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Email verification for {self.user.username}"

    class Meta:
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex
        if not self.otp_code:
            self.otp_code = ''.join(random.choices(string.digits, k=6))
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=30)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        if self.expires_at is None:
            return True
        return timezone.now() > self.expires_at


class PhoneVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phone_verifications')
    phone_number = models.CharField(max_length=20)
    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Phone verification for {self.user.username} ({self.phone_number})"

    class Meta:
        verbose_name = 'Phone Verification'
        verbose_name_plural = 'Phone Verifications'

    def save(self, *args, **kwargs):
        if not self.otp_code:
            self.otp_code = ''.join(random.choices(string.digits, k=6))
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        if self.expires_at is None:
            return True
        return timezone.now() > self.expires_at
