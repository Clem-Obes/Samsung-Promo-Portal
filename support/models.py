from django.db import models
from django.contrib.auth.models import User


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('replied', 'Replied'),
    ]
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    admin_reply = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Support Message'
        verbose_name_plural = 'Support Messages'


class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    sender = models.CharField(max_length=5, choices=SENDER_CHOICES, default='user')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Live Chat Message'
        verbose_name_plural = 'Live Chat Messages'


class Comment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    page = models.CharField(max_length=100, default='general')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_reply = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.content[:50]}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Comment'
        verbose_name_plural = 'User Comments'
