from django.contrib import admin
from django.utils.html import format_html
from .models import Campaign, Task, UserTask, Referral, RewardClaim


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1
    fields = ['title', 'task_type', 'points', 'order']
    ordering = ['order']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['title', 'status_badge', 'start_date', 'end_date', 'task_count', 'claims_count', 'max_participants', 'status', 'created_at']
    list_display_links = ['title']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['title', 'description']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    inlines = [TaskInline]
    fieldsets = (
        ('📋 Campaign Details', {
            'fields': ('title', 'description', 'image', 'status'),
            'description': 'Name your campaign and describe what users need to do. Set status to "Active" to go live.',
        }),
        ('📅 Schedule & Limits', {
            'fields': ('start_date', 'end_date', 'max_participants'),
            'description': 'Set start/end dates. Max participants = 0 means unlimited.',
        }),
        ('🎁 Rewards', {
            'fields': ('reward_description',),
            'description': 'Describe what participants will win (e.g., "Galaxy S24 Ultra").',
        }),
    )

    def task_count(self, obj):
        count = obj.tasks.count()
        return format_html(
            '<span style="background:#17a2b8;color:#fff;padding:2px 10px;border-radius:10px;font-weight:600;">{}</span>',
            count
        )
    task_count.short_description = 'Tasks'

    def claims_count(self, obj):
        return obj.claims.count()
    claims_count.short_description = 'Claims'

    def status_badge(self, obj):
        colors = {'active': '#28a745', 'upcoming': '#ffc107', 'ended': '#6c757d'}
        icons = {'active': 'fa-play-circle', 'upcoming': 'fa-clock', 'ended': 'fa-stop-circle'}
        color = colors.get(obj.status, '#6c757d')
        icon = icons.get(obj.status, 'fa-circle')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 12px;border-radius:12px;font-size:0.8em;font-weight:600;">'
            '<i class="fas {}"></i> {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'campaign', 'type_badge', 'formatted_points', 'submissions_count', 'order', 'points']
    list_filter = ['task_type', 'campaign']
    list_editable = ['points', 'order']
    search_fields = ['title', 'campaign__title']

    def type_badge(self, obj):
        colors = {
            'share': '#17a2b8', 'follow': '#6f42c1', 'refer': '#28a745',
            'review': '#fd7e14', 'social': '#e83e8c'
        }
        color = colors.get(obj.task_type, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:10px;font-size:0.8em;font-weight:600;">{}</span>',
            color, obj.get_task_type_display()
        )
    type_badge.short_description = 'Type'

    def formatted_points(self, obj):
        return format_html(
            '<span style="color:#28a745;font-weight:bold;">+{} pts</span>', obj.points
        )
    formatted_points.short_description = 'Points'
    formatted_points.admin_order_field = 'points'

    def submissions_count(self, obj):
        count = obj.user_tasks.count()
        verified = obj.user_tasks.filter(status='verified').count()
        return format_html(
            '{} total <span style="color:#28a745;">({} verified)</span>', count, verified
        )
    submissions_count.short_description = 'Submissions'


@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'task_campaign', 'status_badge', 'points_value', 'proof_preview', 'completed_at', 'status', 'created_at']
    list_filter = ['status', 'task__campaign', 'task__task_type', 'created_at']
    list_editable = ['status']
    search_fields = ['user__username', 'task__title', 'proof']
    readonly_fields = ['user', 'task', 'proof', 'completed_at', 'created_at']
    list_per_page = 50
    date_hierarchy = 'created_at'
    actions = ['verify_tasks', 'reject_tasks', 'reset_to_pending']
    fieldsets = (
        ('📋 Submission Info', {
            'fields': ('user', 'task', 'status'),
            'description': 'Review this task submission. Change status to "Verified" to award points.',
        }),
        ('📝 Proof Submitted', {
            'fields': ('proof',),
            'description': 'This is what the user submitted as evidence of completing the task.',
        }),
        ('🕐 Dates', {
            'fields': ('completed_at', 'created_at'),
            'classes': ('collapse',),
            'description': 'Click to see when this was submitted and completed.',
        }),
    )

    def task_campaign(self, obj):
        return obj.task.campaign.title
    task_campaign.short_description = 'Campaign'

    def points_value(self, obj):
        return format_html(
            '<span style="color:#28a745;font-weight:bold;">+{} pts</span>', obj.task.points
        )
    points_value.short_description = 'Points'

    def proof_preview(self, obj):
        if obj.proof:
            text = obj.proof[:80] + ('...' if len(obj.proof) > 80 else '')
            return format_html('<span title="{}">{}</span>', obj.proof, text)
        return format_html('<span style="color:#ccc;">—</span>')
    proof_preview.short_description = 'Proof'

    def status_badge(self, obj):
        colors = {'pending': '#ffc107', 'completed': '#17a2b8', 'verified': '#28a745', 'rejected': '#dc3545'}
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:0.8em;font-weight:600;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def verify_tasks(self, request, queryset):
        count = 0
        for ut in queryset.filter(status='completed'):
            ut.status = 'verified'
            ut.save()
            count += 1
        self.message_user(request, f'{count} task(s) verified and points awarded.')
    verify_tasks.short_description = '✅ Verify selected (awards points)'

    def reject_tasks(self, request, queryset):
        count = 0
        for ut in queryset.exclude(status='rejected'):
            ut.status = 'rejected'
            ut.save()
            count += 1
        self.message_user(request, f'{count} task(s) rejected.')
    reject_tasks.short_description = '❌ Reject selected'

    def reset_to_pending(self, request, queryset):
        count = 0
        for ut in queryset:
            ut.status = 'pending'
            ut.save()
            count += 1
        self.message_user(request, f'{count} task(s) reset to pending.')
    reset_to_pending.short_description = '🔄 Reset to pending'


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referred', 'reward_badge', 'is_rewarded', 'created_at']
    list_filter = ['is_rewarded', 'created_at']
    list_editable = ['is_rewarded']
    search_fields = ['referrer__username', 'referred__username']
    date_hierarchy = 'created_at'
    actions = ['mark_as_rewarded']

    def reward_badge(self, obj):
        if obj.is_rewarded:
            return format_html(
                '<span style="background:#28a745;color:#fff;padding:2px 10px;border-radius:10px;font-size:0.8em;font-weight:600;">'
                '<i class="fas fa-check"></i> Rewarded</span>'
            )
        return format_html(
            '<span style="background:#ffc107;color:#000;padding:2px 10px;border-radius:10px;font-size:0.8em;font-weight:600;">'
            'Pending</span>'
        )
    reward_badge.short_description = 'Reward'

    def mark_as_rewarded(self, request, queryset):
        count = queryset.update(is_rewarded=True)
        self.message_user(request, f'{count} referral(s) marked as rewarded.')
    mark_as_rewarded.short_description = '✅ Mark as rewarded'


@admin.register(RewardClaim)
class RewardClaimAdmin(admin.ModelAdmin):
    list_display = ['user', 'campaign', 'status_badge', 'reward_short', 'status', 'created_at']
    list_filter = ['status', 'campaign', 'created_at']
    list_editable = ['status']
    search_fields = ['user__username', 'campaign__title', 'reward_description']
    readonly_fields = ['user', 'campaign', 'created_at']
    date_hierarchy = 'created_at'
    actions = ['approve_claims', 'reject_claims', 'mark_delivered']
    fieldsets = (
        ('🎁 Claim Details', {
            'fields': ('user', 'campaign', 'reward_description', 'created_at'),
            'description': 'This user is claiming a reward from the campaign shown below.',
        }),
        ('✏️ Your Decision', {
            'fields': ('status', 'admin_notes'),
            'description': 'Approve or reject this claim. Add notes for your team (not visible to the user).',
        }),
    )

    def status_badge(self, obj):
        colors = {'pending': '#ffc107', 'approved': '#17a2b8', 'rejected': '#dc3545', 'delivered': '#28a745'}
        icons = {'pending': 'fa-hourglass-half', 'approved': 'fa-thumbs-up', 'rejected': 'fa-times-circle', 'delivered': 'fa-truck'}
        color = colors.get(obj.status, '#6c757d')
        icon = icons.get(obj.status, 'fa-circle')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 12px;border-radius:12px;font-size:0.8em;font-weight:600;">'
            '<i class="fas {}"></i> {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def reward_short(self, obj):
        if obj.reward_description:
            return obj.reward_description[:80] + ('...' if len(obj.reward_description) > 80 else '')
        return '—'
    reward_short.short_description = 'Reward'

    def approve_claims(self, request, queryset):
        count = queryset.filter(status='pending').update(status='approved')
        self.message_user(request, f'{count} claim(s) approved.')
    approve_claims.short_description = '✅ Approve selected'

    def reject_claims(self, request, queryset):
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} claim(s) rejected.')
    reject_claims.short_description = '❌ Reject selected'

    def mark_delivered(self, request, queryset):
        count = queryset.filter(status='approved').update(status='delivered')
        self.message_user(request, f'{count} claim(s) marked as delivered.')
    mark_delivered.short_description = '📦 Mark as delivered'
