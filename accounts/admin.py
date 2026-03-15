from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, EmailVerification, PhoneVerification


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'avatar_preview', 'user', 'user_email', 'phone', 'location',
        'referral_code', 'verification_display', 'ambassador_badge',
        'formatted_points', 'referral_count', 'is_verified', 'is_ambassador', 'points', 'created_at'
    ]
    list_display_links = ['avatar_preview', 'user']
    list_filter = ['is_verified', 'is_ambassador', 'email_verified', 'phone_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'referral_code', 'phone', 'location']
    list_editable = ['is_verified', 'is_ambassador', 'points']
    readonly_fields = ['referral_code', 'avatar_full_preview', 'verification_progress_bar', 'created_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    actions = ['verify_users', 'make_ambassador', 'add_100_points', 'add_500_points', 'reset_points']
    fieldsets = (
        ('👤 User Info', {
            'fields': ('user', 'phone', 'location', 'avatar', 'avatar_full_preview'),
            'description': 'Basic profile information. Phone and location are optional.',
        }),
        ('✅ Verification Status', {
            'fields': ('email_verified', 'phone_verified', 'is_verified', 'verification_progress_bar'),
            'description': 'Check the boxes to manually verify a user\'s email or phone.',
        }),
        ('⭐ Ambassador & Points', {
            'fields': ('is_ambassador', 'points'),
            'description': 'Ambassadors get special badges. Points are earned by completing tasks.',
        }),
        ('🔗 Referral Info', {
            'fields': ('referral_code', 'referred_by'),
            'description': 'The referral code is auto-generated. "Referred by" shows who invited this user.',
        }),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;object-fit:cover;border-radius:50%;border:2px solid #0d6efd;" />',
                obj.avatar.url
            )
        letter = obj.user.username[0].upper()
        return format_html(
            '<div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#1428A0,#00A9E0);'
            'display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;">{}</div>',
            letter
        )
    avatar_preview.short_description = ''

    def avatar_full_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-width:150px;max-height:150px;object-fit:cover;border-radius:12px;" />',
                obj.avatar.url
            )
        return 'No avatar'
    avatar_full_preview.short_description = 'Avatar Preview'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'

    def verification_display(self, obj):
        email_icon = '<i class="fas fa-envelope" style="color:{};" title="Email {}"></i>'.format(
            '#28a745' if obj.email_verified else '#dc3545',
            'verified' if obj.email_verified else 'not verified'
        )
        phone_icon = '<i class="fas fa-phone" style="color:{};" title="Phone {}"></i>'.format(
            '#28a745' if obj.phone_verified else '#dc3545',
            'verified' if obj.phone_verified else 'not verified'
        )
        check = ''
        if obj.is_verified:
            check = ' <i class="fas fa-check-circle" style="color:#28a745;" title="Fully verified"></i>'
        return format_html('{} {} {}', format_html(email_icon), format_html(phone_icon), format_html(check))
    verification_display.short_description = 'Verified'

    def verification_progress_bar(self, obj):
        pct = obj.verification_progress
        color = '#28a745' if pct == 100 else '#ffc107' if pct > 0 else '#dc3545'
        return format_html(
            '<div style="width:200px;background:#e0e0e0;border-radius:10px;overflow:hidden;">'
            '<div style="width:{}%;background:{};height:20px;border-radius:10px;text-align:center;'
            'color:#fff;font-size:0.75em;line-height:20px;font-weight:600;">{}%</div></div>',
            pct, color, pct
        )
    verification_progress_bar.short_description = 'Verification Progress'

    def ambassador_badge(self, obj):
        if obj.is_ambassador:
            return format_html(
                '<span style="background:linear-gradient(135deg,#ffc107,#ff8c00);color:#000;padding:2px 10px;'
                'border-radius:10px;font-size:0.8em;font-weight:700;">⭐ Ambassador</span>'
            )
        return format_html('<span style="color:#666;">Member</span>')
    ambassador_badge.short_description = 'Role'

    def formatted_points(self, obj):
        color = '#28a745' if obj.points > 500 else '#ffc107' if obj.points > 100 else '#6c757d'
        return format_html(
            '<span style="color:{};font-weight:bold;">{:,} pts</span>',
            color, obj.points
        )
    formatted_points.short_description = 'Points'
    formatted_points.admin_order_field = 'points'

    def verify_users(self, request, queryset):
        queryset.update(is_verified=True, email_verified=True, phone_verified=True)
        self.message_user(request, f'{queryset.count()} user(s) fully verified.')
    verify_users.short_description = '✅ Verify selected users'

    def make_ambassador(self, request, queryset):
        queryset.update(is_ambassador=True, is_verified=True)
        self.message_user(request, f'{queryset.count()} user(s) promoted to Ambassador.')
    make_ambassador.short_description = '⭐ Promote to Ambassador'

    def add_100_points(self, request, queryset):
        for profile in queryset:
            profile.points += 100
            profile.save()
        self.message_user(request, f'+100 points added to {queryset.count()} user(s).')
    add_100_points.short_description = '➕ Add 100 points'

    def add_500_points(self, request, queryset):
        for profile in queryset:
            profile.points += 500
            profile.save()
        self.message_user(request, f'+500 points added to {queryset.count()} user(s).')
    add_500_points.short_description = '➕ Add 500 points'

    def reset_points(self, request, queryset):
        queryset.update(points=0)
        self.message_user(request, f'Points reset for {queryset.count()} user(s).')
    reset_points.short_description = '🔄 Reset points to 0'


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_short', 'otp_code', 'is_used', 'expiry_status', 'created_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['token', 'otp_code', 'created_at']

    def token_short(self, obj):
        return obj.token[:16] + '...' if len(obj.token) > 16 else obj.token
    token_short.short_description = 'Token'

    def expiry_status(self, obj):
        if obj.is_expired:
            return format_html('<span style="color:#dc3545;font-weight:600;">Expired</span>')
        return format_html('<span style="color:#28a745;font-weight:600;">Valid</span>')
    expiry_status.short_description = 'Status'


@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'otp_code', 'is_used', 'expiry_status', 'created_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username', 'phone_number']
    readonly_fields = ['otp_code', 'created_at']

    def expiry_status(self, obj):
        if obj.is_expired:
            return format_html('<span style="color:#dc3545;font-weight:600;">Expired</span>')
        return format_html('<span style="color:#28a745;font-weight:600;">Valid</span>')
    expiry_status.short_description = 'Status'
