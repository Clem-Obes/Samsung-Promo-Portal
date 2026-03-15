from django.db import models
from django.conf import settings


class Device(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='devices/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Samsung Device'
        verbose_name_plural = 'Samsung Devices'


class Testimonial(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    quote = models.TextField()
    device_received = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.location}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer Story'
        verbose_name_plural = 'Customer Stories'


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default='Samsung Promo Portal')
    hero_title = models.CharField(max_length=300, default='Samsung Promotion Portal')
    hero_subtitle = models.TextField(default='Join our exclusive Samsung promotion program')
    promo_countdown = models.DateTimeField(blank=True, null=True)
    total_participants = models.IntegerField(default=0)
    total_rewards = models.IntegerField(default=0)
    is_promo_active = models.BooleanField(default=True)

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'


class Announcement(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'


class TestimonyComment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='testimony_comments')
    text = models.TextField(help_text='Share your testimony or experience')
    photo = models.ImageField(upload_to='testimony_comments/photos/', blank=True, null=True)
    video = models.FileField(upload_to='testimony_comments/videos/', blank=True, null=True)
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    device_received = models.CharField(max_length=200, blank=True, help_text='Which Samsung device did you receive?')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_testimonies', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.text[:50]}"

    @property
    def like_count(self):
        return self.likes.count()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Testimony'
        verbose_name_plural = 'User Testimonies'


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
