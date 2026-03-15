from django.contrib import admin
from django.utils.html import format_html
from .models import MembershipPlan, Payment, UserMembership


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'formatted_price', 'popular_badge', 'active_badge', 'order', 'price', 'is_popular', 'is_active']
    list_editable = ['price', 'is_popular', 'is_active', 'order']
    list_display_links = ['name']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    fieldsets = (
        ('💎 Plan Details', {
            'fields': ('name', 'slug', 'price', 'description'),
            'description': 'Create or edit a membership plan. The slug is auto-filled from the name.',
        }),
        ('🎯 Benefits List', {
            'fields': ('benefits',),
            'description': 'Type one benefit per line. These appear as bullet points on the pricing page.',
        }),
        ('⚙️ Display Settings', {
            'fields': ('is_popular', 'is_active', 'order'),
            'description': '"Popular" adds a highlight badge. "Active" controls visibility. "Order" sets position.',
        }),
    )

    def formatted_price(self, obj):
        return format_html(
            '<span style="color:#28a745;font-weight:bold;font-size:1.1em;">${}</span>',
            f'{obj.price:,.2f}'
        )
    formatted_price.short_description = 'Price'
    formatted_price.admin_order_field = 'price'

    def popular_badge(self, obj):
        if obj.is_popular:
            return format_html(
                '<span style="background:linear-gradient(135deg,#ffc107,#ff8c00);color:#000;padding:2px 10px;'
                'border-radius:10px;font-size:0.8em;font-weight:700;">🔥 Popular</span>'
            )
        return format_html('<span style="color:#666;">—</span>')
    popular_badge.short_description = 'Popular'

    def active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background:#28a745;color:#fff;padding:2px 10px;border-radius:10px;font-size:0.85em;">Active</span>'
            )
        return format_html(
            '<span style="background:#dc3545;color:#fff;padding:2px 10px;border-radius:10px;font-size:0.85em;">Inactive</span>'
        )
    active_badge.short_description = 'Status'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'formatted_amount', 'reference_short', 'status_badge', 'status', 'created_at']
    list_filter = ['status', 'plan', 'created_at']
    search_fields = ['reference', 'user__username', 'user__email']
    list_editable = ['status']
    readonly_fields = ['user', 'plan', 'amount', 'reference', 'paystack_response', 'created_at']
    date_hierarchy = 'created_at'
    list_per_page = 30
    fieldsets = (
        ('💳 Payment Details', {
            'fields': ('user', 'plan', 'amount', 'reference', 'status'),
            'description': 'Review this payment. You can update the status if needed.',
        }),
        ('🔧 Technical Details', {
            'fields': ('paystack_response',),
            'classes': ('collapse',),
            'description': 'Raw payment gateway data (click to expand — for technical staff only).',
        }),
        ('🕐 Date', {
            'fields': ('created_at',),
        }),
    )

    def formatted_amount(self, obj):
        return format_html(
            '<span style="color:#28a745;font-weight:bold;font-size:1.05em;">${}</span>',
            f'{obj.amount:,.2f}'
        )
    formatted_amount.short_description = 'Amount'
    formatted_amount.admin_order_field = 'amount'

    def reference_short(self, obj):
        return format_html(
            '<code style="background:#f0f0f0;color:#333;padding:2px 8px;border-radius:4px;font-size:0.85em;">{}</code>',
            obj.reference[:20] + '...' if len(obj.reference) > 20 else obj.reference
        )
    reference_short.short_description = 'Reference'

    def status_badge(self, obj):
        colors = {'pending': '#ffc107', 'success': '#28a745', 'failed': '#dc3545'}
        icons = {'pending': 'fa-hourglass-half', 'success': 'fa-check-circle', 'failed': 'fa-times-circle'}
        color = colors.get(obj.status, '#6c757d')
        icon = icons.get(obj.status, 'fa-circle')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 12px;border-radius:12px;font-size:0.8em;font-weight:600;">'
            '<i class="fas {}"></i> {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'


@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'membership_badge', 'start_date', 'end_date']
    list_filter = ['is_active', 'plan', 'start_date']
    search_fields = ['user__username', 'user__email', 'plan__name']
    date_hierarchy = 'start_date'

    def membership_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background:#28a745;color:#fff;padding:2px 10px;border-radius:10px;font-size:0.85em;font-weight:600;">'
                '<i class="fas fa-check"></i> Active</span>'
            )
        return format_html(
            '<span style="background:#dc3545;color:#fff;padding:2px 10px;border-radius:10px;font-size:0.85em;">Expired</span>'
        )
    membership_badge.short_description = 'Status'
