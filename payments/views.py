from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import MembershipPlan, Payment, UserMembership
import uuid


@login_required
def subscribe(request, plan_slug):
    plan = get_object_or_404(MembershipPlan, slug=plan_slug, is_active=True)
    reference = f'SAM-{uuid.uuid4().hex[:12].upper()}'

    # Create pending payment
    payment = Payment.objects.create(
        user=request.user,
        plan=plan,
        amount=plan.price,
        reference=reference,
    )

    context = {
        'plan': plan,
        'payment': payment,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
        'reference': reference,
        'amount_kobo': int(plan.price * 100),
        'email': request.user.email,
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def verify_payment(request):
    reference = request.GET.get('reference')
    if not reference:
        messages.error(request, 'No payment reference provided.')
        return redirect('core:pricing')

    try:
        payment = Payment.objects.get(reference=reference, user=request.user)
        # In production, verify with Paystack API here
        payment.status = 'success'
        payment.save()

        # Activate membership
        membership, created = UserMembership.objects.get_or_create(user=request.user)
        membership.plan = payment.plan
        membership.is_active = True
        membership.save()

        messages.success(request, f'Payment successful! You are now on the {payment.plan.name} plan.')
        return redirect('payments:payment_success')

    except Payment.DoesNotExist:
        messages.error(request, 'Payment not found.')
        return redirect('core:pricing')


@login_required
def payment_success(request):
    return render(request, 'payments/success.html')
