from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = [
        'certificate_id_display', 'flag_preview_small', 'recipient_name',
        'certificate_type', 'award_amount_display', 'signature_display',
        'status', 'issued_date', 'view_certificate_link',
    ]
    list_filter = ['status', 'certificate_type', 'recipient_country_code', 'issued_date']
    search_fields = ['certificate_id', 'recipient_name', 'user__username', 'user__email']
    list_editable = ['certificate_type', 'status']
    readonly_fields = [
        'certificate_id', 'verification_hash', 'created_at', 'updated_at',
        'preview_certificate', 'flag_preview_large', 'user_info_display',
    ]
    list_per_page = 20
    date_hierarchy = 'issued_date'
    autocomplete_fields = ['campaign']
    raw_id_fields = ['user']

    fieldsets = (
        ('📜 Certificate Info', {
            'fields': ('certificate_id', 'verification_hash', 'status'),
            'description': 'Auto-generated certificate ID & hash. Status can be changed.',
        }),
        ('👤 Recipient — Who gets the certificate', {
            'fields': ('user', 'user_info_display', 'recipient_name', 'recipient_location',
                       'recipient_country_code', 'flag_preview_large'),
            'description': (
                '<b>Pick the user</b>, then type the <b>name</b> you want printed on the certificate. '
                'Choose the <b>country flag</b> from the dropdown — it will appear on the certificate '
                'next to "Certificate of Ownership". Leave name blank to auto-fill from the user account.'
            ),
        }),
        ('💰 Award — What they won', {
            'fields': ('certificate_type', 'award_amount', 'award_description', 'campaign'),
            'description': (
                'Set the <b>award amount</b> (e.g. 900000 for $900,000). '
                'Leave description blank to auto-generate from the amount and signatory. '
                'You can also write a fully custom description.'
            ),
        }),
        ('✍️ Signature — Who signs it', {
            'fields': ('issuer_name', 'issuer_title', 'authorized_signatory'),
            'description': (
                'The <b>authorized signatory</b> name appears as a cursive signature on the certificate. '
                'The <b>issuer title</b> is shown in the certificate body text (e.g. "Senior Online Manager").'
            ),
        }),
        ('📅 Dates', {
            'fields': ('issued_date', 'created_at', 'updated_at'),
        }),
        ('👁️ Live Preview', {
            'fields': ('preview_certificate',),
            'description': 'Save first, then click to see the real printable certificate.',
        }),
    )

    # ---- List display columns ----

    def certificate_id_display(self, obj):
        return format_html(
            '<strong style="font-family: monospace; color: #1428A0;">{}</strong>',
            obj.certificate_id
        )
    certificate_id_display.short_description = 'Cert #'
    certificate_id_display.admin_order_field = 'certificate_id'

    def flag_preview_small(self, obj):
        code = (obj.recipient_country_code or 'us').lower()
        return format_html(
            '<img src="https://flagcdn.com/24x18/{}.png" alt="{}" '
            'style="vertical-align:middle; border:1px solid #ddd; border-radius:2px;">',
            code, obj.recipient_country_code
        )
    flag_preview_small.short_description = 'Flag'

    def award_amount_display(self, obj):
        amount = f'{obj.award_amount:,.2f}'
        return format_html(
            '<strong style="color: #16a34a;">${}</strong>',
            amount
        )
    award_amount_display.short_description = 'Amount'
    award_amount_display.admin_order_field = 'award_amount'

    def signature_display(self, obj):
        return format_html(
            '<span style="font-family: cursive; color: #555;">{}</span>',
            obj.authorized_signatory
        )
    signature_display.short_description = 'Signed By'

    def status_badge(self, obj):
        colors = {
            'issued': ('#16a34a', '#f0fdf4'),
            'draft': ('#ca8a04', '#fefce8'),
            'revoked': ('#dc2626', '#fef2f2'),
        }
        fg, bg = colors.get(obj.status, ('#666', '#f5f5f5'))
        return format_html(
            '<span style="background:{}; color:{}; padding:4px 12px; border-radius:20px; '
            'font-size:0.75rem; font-weight:700;">{}</span>',
            bg, fg, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def view_certificate_link(self, obj):
        url = reverse('dashboard:certificate_print', args=[obj.pk])
        return format_html(
            '<a href="{}" target="_blank" style="color:#1428A0; font-weight:600;">'
            '🔗 View</a>',
            url
        )
    view_certificate_link.short_description = 'View'

    # ---- Detail-page readonly helpers ----

    def user_info_display(self, obj):
        """Shows the selected user's details for reference."""
        if not obj.user_id:
            return format_html('<em style="color:#999;">Select a user above first.</em>')
        u = obj.user
        name = u.get_full_name() or '—'
        email = u.email or '—'
        username = u.username
        location = '—'
        if hasattr(u, 'profile') and u.profile.location:
            location = u.profile.location
        return format_html(
            '<div style="background:#f8f9fc; padding:12px 16px; border-radius:10px; '
            'border:1px solid #e5e7eb; font-size:0.9rem; line-height:1.8;">'
            '<strong>Username:</strong> {} &nbsp;|&nbsp; '
            '<strong>Full Name:</strong> {} &nbsp;|&nbsp; '
            '<strong>Email:</strong> {} &nbsp;|&nbsp; '
            '<strong>Location:</strong> {}'
            '</div>',
            username, name, email, location
        )
    user_info_display.short_description = 'User Account Info'

    def flag_preview_large(self, obj):
        """Shows a larger flag preview of the selected country."""
        code = (obj.recipient_country_code or 'us').lower()
        label = obj.get_recipient_country_code_display() if obj.recipient_country_code else 'United States'
        return format_html(
            '<div style="display:flex; align-items:center; gap:12px;">'
            '<img src="https://flagcdn.com/80x60/{}.png" alt="{}" '
            'style="border:2px solid #ddd; border-radius:4px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">'
            '<span style="font-size:1.1rem; font-weight:600; color:#1a1a2e;">{}</span>'
            '</div>',
            code, code, label
        )
    flag_preview_large.short_description = 'Flag Preview (on certificate)'

    def preview_certificate(self, obj):
        if obj.pk:
            url = reverse('dashboard:certificate_print', args=[obj.pk])
            return format_html(
                '<a href="{}" target="_blank" class="button" '
                'style="background:#1428A0; color:#fff; padding:10px 24px; '
                'border-radius:8px; text-decoration:none; display:inline-block; '
                'font-weight:600; font-size:0.95rem;">'
                '🖨️ Open Printable Certificate</a>'
                '<p style="color:#888; font-size:0.8rem; margin-top:8px;">'
                'Opens in a new tab. Use Ctrl+P to print or save as PDF.</p>',
                url
            )
        return format_html(
            '<em style="color:#999;">💡 Save the certificate first, then you can preview it here.</em>'
        )
    preview_certificate.short_description = 'Certificate Preview'

    # ---- Auto-fill on save ----

    def save_model(self, request, obj, form, change):
        """Auto-populate recipient name from user if left blank."""
        if not obj.recipient_name:
            full_name = obj.user.get_full_name()
            obj.recipient_name = full_name if full_name else obj.user.username
        if not obj.recipient_location and hasattr(obj.user, 'profile'):
            obj.recipient_location = obj.user.profile.location or ''
        super().save_model(request, obj, form, change)

