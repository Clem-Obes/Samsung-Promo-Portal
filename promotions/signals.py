from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import UserTask


@receiver(pre_save, sender=UserTask)
def award_points_on_task_verification(sender, instance, **kwargs):
    """
    When admin changes a UserTask status to 'verified', automatically
    award the task's points to the user's profile.
    When admin changes status to 'rejected' from 'verified', remove points.
    """
    if not instance.pk:
        return  # New object, skip

    try:
        old_instance = UserTask.objects.get(pk=instance.pk)
    except UserTask.DoesNotExist:
        return

    old_status = old_instance.status
    new_status = instance.status

    if old_status == new_status:
        return  # No change

    try:
        profile = instance.user.profile
    except Exception:
        return

    # Award points when task becomes verified
    if new_status == 'verified' and old_status != 'verified':
        profile.points += instance.task.points
        profile.save()

    # Remove points if task gets un-verified (rejected after being verified)
    elif old_status == 'verified' and new_status in ['rejected', 'pending']:
        profile.points = max(0, profile.points - instance.task.points)
        profile.save()
