from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from accounts.models import UserProfile
from promotions.models import UserTask, Referral, RewardClaim, Campaign
from core.models import Announcement
from dashboard.models import Certificate


@login_required
def dashboard_home(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_tasks = UserTask.objects.filter(user=request.user)
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(status__in=['completed', 'verified']).count()
    verified_tasks = user_tasks.filter(status='verified').count()
    pending_tasks = user_tasks.filter(status='pending').count()
    referral_count = Referral.objects.filter(referrer=request.user).count()
    reward_claims = RewardClaim.objects.filter(user=request.user)
    active_campaigns = Campaign.objects.filter(status='active')[:5]
    announcements = Announcement.objects.filter(is_active=True)[:5]

    # Calculate total points earned from tasks
    total_points_from_tasks = sum(
        ut.task.points for ut in user_tasks.filter(status='verified').select_related('task')
    )

    context = {
        'profile': profile,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'verified_tasks': verified_tasks,
        'pending_tasks': pending_tasks,
        'referral_count': referral_count,
        'reward_claims': reward_claims,
        'active_campaigns': active_campaigns,
        'announcements': announcements,
        'total_points_from_tasks': total_points_from_tasks,
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def tasks_view(request):
    user_tasks = UserTask.objects.filter(user=request.user).select_related('task', 'task__campaign')
    return render(request, 'dashboard/tasks.html', {'user_tasks': user_tasks})


@login_required
def referrals_view(request):
    profile = request.user.profile
    referrals = Referral.objects.filter(referrer=request.user).select_related('referred')
    return render(request, 'dashboard/referrals.html', {'referrals': referrals, 'profile': profile})


@login_required
def rewards_view(request):
    claims = RewardClaim.objects.filter(user=request.user).select_related('campaign')
    return render(request, 'dashboard/rewards.html', {'claims': claims})


@login_required
def certificates_list(request):
    """Show all certificates belonging to the logged-in user."""
    certificates = Certificate.objects.filter(user=request.user, status='issued')
    return render(request, 'dashboard/certificates.html', {'certificates': certificates})


@login_required
def certificate_view(request, pk):
    """View a single certificate within the site layout."""
    certificate = get_object_or_404(Certificate, pk=pk, user=request.user)
    description_lines = certificate.award_description.split('\n') if certificate.award_description else []
    return render(request, 'dashboard/certificate_view.html', {
        'certificate': certificate,
        'description_lines': description_lines,
    })


@login_required
def certificate_print(request, pk):
    """Standalone printable certificate page (no site chrome)."""
    certificate = get_object_or_404(Certificate, pk=pk, user=request.user)
    description_lines = certificate.award_description.split('\n') if certificate.award_description else []
    return render(request, 'dashboard/certificate_print.html', {
        'certificate': certificate,
        'description_lines': description_lines,
    })


def certificate_verify(request, hash_prefix):
    """Public verification page — anyone can verify a certificate by hash."""
    try:
        certificate = Certificate.objects.get(
            verification_hash__startswith=hash_prefix,
            status='issued'
        )
        is_valid = True
    except (Certificate.DoesNotExist, Certificate.MultipleObjectsReturned):
        certificate = None
        is_valid = False
    return render(request, 'dashboard/certificate_verify.html', {
        'certificate': certificate,
        'is_valid': is_valid,
        'hash_prefix': hash_prefix,
    })
