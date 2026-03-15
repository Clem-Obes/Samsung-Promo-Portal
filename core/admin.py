from django.contrib import admin
from django.utils.html import format_html
from .models import Device, Testimonial, SiteSettings, Announcement, TestimonyComment, NewsletterSubscriber


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'name', 'formatted_price', 'is_featured', 'created_at']
    list_display_links = ['image_preview', 'name']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_featured']
    list_per_page = 20
    readonly_fields = ['image_full_preview', 'created_at']
    fieldsets = (
        ('📱 Device Details', {
            'fields': ('name', 'description', 'price', 'is_featured'),
            'description': 'Add or edit a Samsung device. Featured devices appear on the homepage.',
        }),
        ('🖼️ Device Photo', {
            'fields': ('image', 'image_full_preview'),
            'description': 'Upload a clear product photo (recommended size: 800×600px).',
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:50px; height:50px; object-fit:cover; border-radius:8px; border:2px solid #444;" />',
                obj.image.url
            )
        return format_html('<span style="color:#bbb;">No img</span>')
    image_preview.short_description = 'Photo'

    def image_full_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px; max-height:200px; object-fit:cover; border-radius:12px;" />',
                obj.image.url
            )
        return 'No image uploaded'
    image_full_preview.short_description = 'Preview'

    def formatted_price(self, obj):
        return format_html(
            '<span style="color:#28a745; font-weight:bold; font-size:1.05em;">${}</span>',
            f'{obj.price:,.2f}'
        )
    formatted_price.short_description = 'Price'
    formatted_price.admin_order_field = 'price'


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['avatar_preview', 'name', 'location', 'device_received', 'star_display', 'status_badge', 'status', 'created_at']
    list_display_links = ['avatar_preview', 'name']
    list_filter = ['status', 'rating', 'created_at']
    search_fields = ['name', 'location', 'quote', 'device_received']
    list_editable = ['status']
    list_per_page = 20
    readonly_fields = ['image_full_preview', 'created_at']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('👤 Customer Info', {
            'fields': ('name', 'location', 'device_received', 'rating'),
            'description': 'Enter the customer\'s name, location, and what device they received.',
        }),
        ('💬 Their Story', {
            'fields': ('quote', 'status'),
            'description': 'Paste their testimonial quote. Set status to "Approved" to show on the website.',
        }),
        ('🖼️ Customer Photo', {
            'fields': ('image', 'image_full_preview'),
            'description': 'Upload a photo of the customer (optional).',
        }),
    )
    actions = ['approve_selected', 'reject_selected']

    def avatar_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:42px; height:42px; object-fit:cover; border-radius:50%; border:2px solid #0d6efd;" />',
                obj.image.url
            )
        letter = obj.name[0].upper() if obj.name else '?'
        return format_html(
            '<div style="width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,#1428A0,#00A9E0);'
            'display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:1rem;">{}</div>',
            letter
        )
    avatar_preview.short_description = ''

    def image_full_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:250px; max-height:180px; object-fit:cover; border-radius:12px;" />',
                obj.image.url
            )
        return 'No image'
    image_full_preview.short_description = 'Preview'

    def star_display(self, obj):
        filled = '<i class="fas fa-star" style="color:#ffc107;"></i>' * obj.rating
        empty = '<i class="far fa-star" style="color:#ddd;"></i>' * (5 - obj.rating)
        return format_html(filled + empty)
    star_display.short_description = 'Rating'
    star_display.admin_order_field = 'rating'

    def status_badge(self, obj):
        colors = {'approved': '#28a745', 'pending': '#ffc107', 'rejected': '#dc3545'}
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:0.8em;font-weight:600;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def approve_selected(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f'{count} testimonial(s) approved.')
    approve_selected.short_description = '✅ Approve selected'

    def reject_selected(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f'{count} testimonial(s) rejected.')
    reject_selected.short_description = '❌ Reject selected'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'promo_status_badge', 'total_participants', 'total_rewards', 'promo_countdown']
    fieldsets = (
        ('🏷️ Website Name & Text', {
            'fields': ('site_name', 'hero_title', 'hero_subtitle'),
            'description': 'Change the website name and the big text visitors see on the homepage.',
        }),
        ('⚡ Promotion On/Off', {
            'fields': ('is_promo_active', 'promo_countdown'),
            'classes': ('wide',),
            'description': 'Turn the promotion on or off. Set a countdown date if needed.',
        }),
        ('📊 Counters', {
            'fields': ('total_participants', 'total_rewards'),
            'description': 'These numbers show on the website as stats.',
        }),
    )

    def promo_status_badge(self, obj):
        if obj.is_promo_active:
            return format_html(
                '<span style="background:#28a745;color:#fff;padding:3px 12px;border-radius:12px;font-weight:600;">LIVE</span>'
            )
        return format_html(
            '<span style="background:#dc3545;color:#fff;padding:3px 12px;border-radius:12px;font-weight:600;">OFF</span>'
        )
    promo_status_badge.short_description = 'Promo'

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'active_badge', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'

    def active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background:#28a745;color:#fff;padding:2px 10px;border-radius:10px;font-size:0.85em;">Active</span>'
            )
        return format_html(
            '<span style="background:#6c757d;color:#fff;padding:2px 10px;border-radius:10px;font-size:0.85em;">Inactive</span>'
        )
    active_badge.short_description = 'Status'


@admin.register(TestimonyComment)
class TestimonyCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'short_text', 'device_received', 'star_display', 'status_badge', 'media_icons', 'like_count', 'status', 'created_at']
    list_filter = ['status', 'rating', 'created_at']
    list_editable = ['status']
    search_fields = ['user__username', 'text', 'device_received']
    readonly_fields = ['like_count', 'photo_preview', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    actions = ['approve_comments', 'reject_comments']
    fieldsets = (
        ('✍️ Testimony Details', {
            'fields': ('user', 'text', 'device_received', 'rating'),
            'description': 'Review what the user wrote and the device they mentioned.',
        }),
        ('📸 Photos & Videos', {
            'fields': ('photo', 'photo_preview', 'video'),
            'description': 'Media uploaded by the user as proof.',
        }),
        ('🛡️ Review & Approve', {
            'fields': ('status', 'like_count', 'created_at', 'updated_at'),
            'description': 'Set to "Approved" to publish on the website, or "Rejected" to hide.',
        }),
    )

    def short_text(self, obj):
        return obj.text[:80] + '...' if len(obj.text) > 80 else obj.text
    short_text.short_description = 'Testimony'

    def star_display(self, obj):
        filled = '<i class="fas fa-star" style="color:#ffc107;"></i>' * obj.rating
        empty = '<i class="far fa-star" style="color:#ddd;"></i>' * (5 - obj.rating)
        return format_html(filled + empty)
    star_display.short_description = 'Rating'

    def status_badge(self, obj):
        colors = {'approved': '#28a745', 'pending': '#ffc107', 'rejected': '#dc3545'}
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:0.8em;font-weight:600;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def media_icons(self, obj):
        icons = []
        if obj.photo:
            icons.append('<i class="fas fa-camera" style="color:#17a2b8;"></i>')
        if obj.video:
            icons.append('<i class="fas fa-video" style="color:#e83e8c;"></i>')
        return format_html(' '.join(icons)) if icons else format_html('<span style="color:#ccc;">—</span>')
    media_icons.short_description = 'Media'

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width:250px; max-height:180px; object-fit:cover; border-radius:12px;" />',
                obj.photo.url
            )
        return 'No photo'
    photo_preview.short_description = 'Photo Preview'

    def approve_comments(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f'{count} comment(s) approved.')
    approve_comments.short_description = '✅ Approve selected comments'

    def reject_comments(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f'{count} comment(s) rejected.')
    reject_comments.short_description = '❌ Reject selected comments'


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    list_editable = ('is_active',)
    readonly_fields = ('subscribed_at',)
    list_per_page = 50
    actions = ['deactivate_subscribers', 'activate_subscribers']

    fieldsets = (
        ('📧 Subscriber Info', {
            'fields': ('email', 'is_active', 'subscribed_at')
        }),
    )

    def deactivate_subscribers(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} subscriber(s) deactivated.')
    deactivate_subscribers.short_description = '🚫 Deactivate selected subscribers'

    def activate_subscribers(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} subscriber(s) activated.')
    activate_subscribers.short_description = '✅ Activate selected subscribers'
