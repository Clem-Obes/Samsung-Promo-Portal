from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage, ChatMessage, Comment


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject_short', 'status_badge', 'has_reply', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['status']
    readonly_fields = ['name', 'email', 'subject', 'message', 'user', 'created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    actions = ['mark_read', 'mark_replied']
    fieldsets = (
        ('📨 Incoming Message', {
            'fields': ('name', 'email', 'subject', 'message', 'user', 'created_at'),
            'description': 'This message was sent through the contact form on the website.',
        }),
        ('✏️ Your Reply', {
            'fields': ('status', 'admin_reply'),
            'classes': ('wide',),
            'description': 'Type your reply and set status to "Replied". The user will receive an email.',
        }),
    )

    def subject_short(self, obj):
        return obj.subject[:60] + ('...' if len(obj.subject) > 60 else '')
    subject_short.short_description = 'Subject'

    def status_badge(self, obj):
        colors = {'unread': '#dc3545', 'read': '#ffc107', 'replied': '#28a745'}
        icons = {'unread': 'fa-envelope', 'read': 'fa-envelope-open', 'replied': 'fa-reply'}
        color = colors.get(obj.status, '#6c757d')
        icon = icons.get(obj.status, 'fa-circle')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 12px;border-radius:12px;font-size:0.8em;font-weight:600;">'
            '<i class="fas {}"></i> {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def has_reply(self, obj):
        if obj.admin_reply:
            return format_html('<i class="fas fa-check-circle" style="color:#28a745;"></i>')
        return format_html('<i class="fas fa-minus-circle" style="color:#666;"></i>')
    has_reply.short_description = 'Replied'

    def mark_read(self, request, queryset):
        count = queryset.filter(status='unread').update(status='read')
        self.message_user(request, f'{count} message(s) marked as read.')
    mark_read.short_description = '📖 Mark as read'

    def mark_replied(self, request, queryset):
        count = queryset.update(status='replied')
        self.message_user(request, f'{count} message(s) marked as replied.')
    mark_replied.short_description = '✅ Mark as replied'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'sender_badge', 'message_short', 'read_status', 'created_at']
    list_filter = ['sender', 'is_read', 'created_at']
    search_fields = ['user__username', 'message']
    date_hierarchy = 'created_at'
    list_per_page = 50
    actions = ['mark_as_read']

    def sender_badge(self, obj):
        if obj.sender == 'admin':
            return format_html(
                '<span style="background:#6f42c1;color:#fff;padding:2px 10px;border-radius:10px;font-size:0.8em;font-weight:600;">'
                '<i class="fas fa-headset"></i> Admin</span>'
            )
        return format_html(
            '<span style="background:#17a2b8;color:#fff;padding:2px 10px;border-radius:10px;font-size:0.8em;font-weight:600;">'
            '<i class="fas fa-user"></i> User</span>'
        )
    sender_badge.short_description = 'From'

    def message_short(self, obj):
        return obj.message[:80] + ('...' if len(obj.message) > 80 else '')
    message_short.short_description = 'Message'

    def read_status(self, obj):
        if obj.is_read:
            return format_html('<i class="fas fa-check-double" style="color:#28a745;" title="Read"></i>')
        return format_html('<i class="fas fa-check" style="color:#ffc107;" title="Unread"></i>')
    read_status.short_description = 'Read'

    def mark_as_read(self, request, queryset):
        count = queryset.update(is_read=True)
        self.message_user(request, f'{count} message(s) marked as read.')
    mark_as_read.short_description = '✅ Mark as read'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_short', 'page_badge', 'status_badge', 'has_reply', 'status', 'created_at']
    list_filter = ['status', 'page', 'created_at']
    list_editable = ['status']
    search_fields = ['user__username', 'content']
    date_hierarchy = 'created_at'
    actions = ['approve_comments', 'reject_comments']
    fieldsets = (
        ('💬 Comment Details', {
            'fields': ('user', 'content', 'page', 'created_at'),
            'description': 'This comment was left by a user on the website.',
        }),
        ('✏️ Moderation', {
            'fields': ('status', 'admin_reply'),
            'description': 'Set to "Approved" to publish, or "Rejected" to hide. You can also reply.',
        }),
    )

    def content_short(self, obj):
        return obj.content[:80] + ('...' if len(obj.content) > 80 else '')
    content_short.short_description = 'Comment'

    def page_badge(self, obj):
        return format_html(
            '<span style="background:#6f42c1;color:#fff;padding:2px 8px;border-radius:8px;font-size:0.75em;">{}</span>',
            obj.page
        )
    page_badge.short_description = 'Page'

    def status_badge(self, obj):
        colors = {'approved': '#28a745', 'pending': '#ffc107', 'rejected': '#dc3545'}
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:0.8em;font-weight:600;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def has_reply(self, obj):
        if obj.admin_reply:
            return format_html('<i class="fas fa-check-circle" style="color:#28a745;"></i>')
        return format_html('<i class="fas fa-minus-circle" style="color:#666;"></i>')
    has_reply.short_description = 'Replied'

    def approve_comments(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f'{count} comment(s) approved.')
    approve_comments.short_description = '✅ Approve selected'

    def reject_comments(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f'{count} comment(s) rejected.')
    reject_comments.short_description = '❌ Reject selected'
