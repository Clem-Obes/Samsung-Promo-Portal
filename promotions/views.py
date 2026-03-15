from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Campaign, Task, UserTask, RewardClaim


def campaigns_list(request):
    campaigns = Campaign.objects.all()
    return render(request, 'promotions/campaigns.html', {'campaigns': campaigns})


def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    tasks = campaign.tasks.all()
    user_tasks = {}
    user_claim = None
    can_claim = False

    if request.user.is_authenticated:
        user_tasks = {
            ut.task_id: ut for ut in UserTask.objects.filter(
                user=request.user, task__campaign=campaign
            )
        }
        user_claim = RewardClaim.objects.filter(user=request.user, campaign=campaign).first()
        # Check if all tasks are verified
        total_tasks = tasks.count()
        verified_tasks = UserTask.objects.filter(
            user=request.user, task__campaign=campaign, status='verified'
        ).count()
        can_claim = total_tasks > 0 and verified_tasks == total_tasks and not user_claim

    return render(request, 'promotions/campaign_detail.html', {
        'campaign': campaign,
        'tasks': tasks,
        'user_tasks': user_tasks,
        'user_claim': user_claim,
        'can_claim': can_claim,
    })


@login_required
def join_task(request, task_id):
    """User joins/starts a task — creates a pending UserTask."""
    task = get_object_or_404(Task, pk=task_id)

    if task.campaign.status != 'active':
        messages.warning(request, 'This campaign is not currently active.')
        return redirect('promotions:campaign_detail', pk=task.campaign.pk)

    user_task, created = UserTask.objects.get_or_create(
        user=request.user,
        task=task,
        defaults={'status': 'pending'}
    )

    if created:
        messages.success(request, f'You joined the task: "{task.title}". Complete it and submit proof!')
    else:
        messages.info(request, 'You already joined this task.')

    return redirect('promotions:campaign_detail', pk=task.campaign.pk)


@login_required
def complete_task(request, task_id):
    """User submits proof that a task is completed."""
    task = get_object_or_404(Task, pk=task_id)

    try:
        user_task = UserTask.objects.get(user=request.user, task=task)
    except UserTask.DoesNotExist:
        messages.error(request, 'You need to join this task first.')
        return redirect('promotions:campaign_detail', pk=task.campaign.pk)

    if user_task.status in ['completed', 'verified']:
        messages.info(request, 'This task is already submitted.')
        return redirect('promotions:campaign_detail', pk=task.campaign.pk)

    if user_task.status not in ['pending', 'rejected']:
        messages.info(request, 'This task cannot be resubmitted.')
        return redirect('promotions:campaign_detail', pk=task.campaign.pk)

    if request.method == 'POST':
        proof = request.POST.get('proof', '')
        if not proof.strip():
            messages.error(request, 'Please provide proof of completion (link, screenshot URL, or description).')
            return redirect('promotions:campaign_detail', pk=task.campaign.pk)

        user_task.status = 'completed'
        user_task.proof = proof
        user_task.completed_at = timezone.now()
        user_task.save()
        messages.success(request, f'Task "{task.title}" submitted for verification! Admin will review your proof.')
    else:
        messages.error(request, 'Invalid request.')

    return redirect('promotions:campaign_detail', pk=task.campaign.pk)


@login_required
def claim_reward(request, campaign_id):
    """User claims a reward after all campaign tasks are verified."""
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    tasks = campaign.tasks.all()
    total_tasks = tasks.count()
    verified_tasks = UserTask.objects.filter(
        user=request.user, task__campaign=campaign, status='verified'
    ).count()

    # Check if already claimed
    existing_claim = RewardClaim.objects.filter(user=request.user, campaign=campaign).first()
    if existing_claim:
        messages.info(request, 'You have already claimed a reward for this campaign.')
        return redirect('promotions:campaign_detail', pk=campaign.pk)

    # Check all tasks verified
    if total_tasks == 0 or verified_tasks < total_tasks:
        messages.warning(request, 'You need all tasks verified before claiming a reward.')
        return redirect('promotions:campaign_detail', pk=campaign.pk)

    # Create the claim
    RewardClaim.objects.create(
        user=request.user,
        campaign=campaign,
        reward_description=campaign.reward_description,
        status='pending',
    )
    messages.success(request, f'Reward claim submitted for "{campaign.title}"! Our team will review and process it.')
    return redirect('dashboard:rewards')
