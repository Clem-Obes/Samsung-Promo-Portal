from django.db import models
from django.contrib.auth.models import User


class MembershipPlan(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    benefits = models.TextField(help_text='One benefit per line')
    is_popular = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"

    @property
    def benefits_list(self):
        return [b.strip() for b in self.benefits.split('\n') if b.strip()]

    class Meta:
        ordering = ['order']
        verbose_name = 'Membership Plan'
        verbose_name_plural = 'Membership Plans'


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=200, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    paystack_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Record'
        verbose_name_plural = 'Payment Records'


class UserMembership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'None'}"

    class Meta:
        verbose_name = 'Active Membership'
        verbose_name_plural = 'Active Memberships'
