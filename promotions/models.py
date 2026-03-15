from django.db import models
from django.contrib.auth.models import User


class Campaign(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('upcoming', 'Upcoming'),
        ('ended', 'Ended'),
    ]
    title = models.CharField(max_length=300)
    description = models.TextField()
    image = models.ImageField(upload_to='campaigns/', blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    reward_description = models.TextField(blank=True)
    max_participants = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Promo Campaign'
        verbose_name_plural = 'Promo Campaigns'


class Task(models.Model):
    TASK_TYPES = [
        ('share', 'Share Product Page'),
        ('follow', 'Follow Channel'),
        ('refer', 'Refer Friends'),
        ('review', 'Write Review'),
        ('social', 'Social Media Post'),
    ]
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=300)
    description = models.TextField()
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    points = models.IntegerField(default=10)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']
        verbose_name = 'Campaign Task'
        verbose_name_plural = 'Campaign Tasks'


class UserTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='user_tasks')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    proof = models.TextField(blank=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.task.title}"

    class Meta:
        unique_together = ['user', 'task']
        verbose_name = 'Task Submission'
        verbose_name_plural = 'Task Submissions'


class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referred_by_user')
    created_at = models.DateTimeField(auto_now_add=True)
    is_rewarded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.referrer.username} -> {self.referred.username}"

    class Meta:
        unique_together = ['referrer', 'referred']
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'


class RewardClaim(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('delivered', 'Delivered'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reward_claims')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='claims')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reward_description = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.campaign.title}"

    class Meta:
        verbose_name = 'Reward Claim'
        verbose_name_plural = 'Reward Claims'
