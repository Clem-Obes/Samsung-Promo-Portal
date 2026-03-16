from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import UserProfile, EmailVerification, PhoneVerification
from promotions.models import Referral
import uuid
import random
import string
import logging

logger = logging.getLogger(__name__)


def _send_email_otp(user):
    """Create a new email verification and send OTP via email."""
    # Invalidate any previous unused verifications
    EmailVerification.objects.filter(user=user, is_used=False).update(is_used=True)

    verification = EmailVerification.objects.create(user=user)

    try:
        result = send_mail(
            subject='Samsung Promo Portal — Email Verification Code',
            message=(
                f'Hello {user.username},\n\n'
                f'Your email verification code is: {verification.otp_code}\n\n'
                f'This code expires in 30 minutes.\n\n'
                f'If you did not request this, please ignore this email.\n\n'
                f'— Samsung Promo Portal Team'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {user.email} (result: {result})")
    except Exception as e:
        logger.error(f"FAILED to send email to {user.email}: {type(e).__name__}: {str(e)}")
        raise

    return verification


def _send_phone_otp(user, phone_number):
    """Create a phone verification OTP. In production, integrate an SMS API."""
    # Invalidate previous unused codes
    PhoneVerification.objects.filter(user=user, is_used=False).update(is_used=True)

    verification = PhoneVerification.objects.create(user=user, phone_number=phone_number)

    # ---- SMS Integration Point ----
    # In production, replace this with Twilio / Africa's Talking / Termii etc.
    # For development, the OTP is printed to the console.
    print(f'[SMS OTP] Phone verification for {user.username} ({phone_number}): {verification.otp_code}')

    return verification


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    # Capture referral code from GET param (from referral link) or POST
    ref_code = request.GET.get('ref', '') or request.POST.get('referral_code', '')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone', '')
        location = request.POST.get('location', '')
        referral_code = request.POST.get('referral_code', '') or ref_code

        logger.info(f"Registration attempt: username={username}, email={email}")

        if password != password2:
            logger.warning(f"Registration failed for {username}: Passwords do not match")
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html', {'ref_code': ref_code})

        if User.objects.filter(username=username).exists():
            logger.warning(f"Registration failed: Username '{username}' already exists")
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/register.html', {'ref_code': ref_code})

        if User.objects.filter(email=email).exists():
            logger.warning(f"Registration failed: Email '{email}' already registered")
            messages.error(request, 'Email already registered.')
            return render(request, 'accounts/register.html', {'ref_code': ref_code})

        user = User.objects.create_user(username=username, email=email, password=password)

        # Create profile
        referred_by_profile = None
        if referral_code:
            try:
                referred_by_profile = UserProfile.objects.get(referral_code=referral_code)
            except UserProfile.DoesNotExist:
                pass

        profile = UserProfile.objects.create(
            user=user,
            phone=phone,
            location=location,
            referred_by=referred_by_profile
        )

        # Create the Referral record and award points
        if referred_by_profile:
            Referral.objects.create(
                referrer=referred_by_profile.user,
                referred=user,
            )
            referred_by_profile.points += 100
            referred_by_profile.save()
            profile.points += 50
            profile.save()

        # Send email verification OTP
        _send_email_otp(user)

        login(request, user)
        messages.success(request, 'Account created! Please verify your email to unlock all features.')
        return redirect('accounts:verify_email_page')

    return render(request, 'accounts/register.html', {'ref_code': ref_code})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.save()

        profile.phone = request.POST.get('phone', '')
        profile.location = request.POST.get('location', '')
        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']
        profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {'profile': profile})


# ─── EMAIL VERIFICATION ─────────────────────────────────────

@login_required
def verify_email_page(request):
    """Page where user enters the 6-digit OTP sent to their email."""
    profile = request.user.profile

    if profile.email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('dashboard:home')

    if request.method == 'POST':
        otp_input = request.POST.get('otp_code', '').strip()

        if not otp_input or len(otp_input) != 6:
            messages.error(request, 'Please enter a valid 6-digit code.')
            return render(request, 'accounts/verify_email.html')

        # Find the most recent unused, non-expired verification
        verification = EmailVerification.objects.filter(
            user=request.user,
            otp_code=otp_input,
            is_used=False,
        ).order_by('-created_at').first()

        if not verification:
            messages.error(request, 'Invalid verification code. Please check and try again.')
            return render(request, 'accounts/verify_email.html')

        if verification.is_expired:
            messages.error(request, 'This code has expired. Please request a new one.')
            return render(request, 'accounts/verify_email.html')

        # Mark as used and verify email
        verification.is_used = True
        verification.save()

        profile.email_verified = True
        profile.save()

        # Award bonus points for verifying email
        profile.points += 25
        profile.save()

        messages.success(request, '🎉 Email verified successfully! +25 bonus points awarded.')

        # If phone is also verified, user is fully verified
        if profile.phone_verified:
            messages.success(request, '✅ You are now fully verified!')
            return redirect('dashboard:home')

        # Redirect to phone verification if phone number exists
        if profile.phone:
            return redirect('accounts:verify_phone_page')

        return redirect('dashboard:home')

    return render(request, 'accounts/verify_email.html')


@login_required
def resend_email_otp(request):
    """Resend a new email OTP."""
    profile = request.user.profile

    if profile.email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('dashboard:home')

    # Rate limiting: check if a code was sent in the last 60 seconds
    recent = EmailVerification.objects.filter(
        user=request.user,
        is_used=False,
        created_at__gte=timezone.now() - timezone.timedelta(seconds=60)
    ).exists()

    if recent:
        messages.warning(request, 'Please wait at least 60 seconds before requesting a new code.')
    else:
        _send_email_otp(request.user)
        messages.success(request, 'A new verification code has been sent to your email.')

    return redirect('accounts:verify_email_page')


def verify_email_link(request, token):
    """Verify email via a direct link (alternative to OTP)."""
    try:
        verification = EmailVerification.objects.get(token=token, is_used=False)
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
        return redirect('dashboard:home')

    if verification.is_expired:
        messages.error(request, 'This verification link has expired. Please request a new code.')
        return redirect('accounts:verify_email_page')

    verification.is_used = True
    verification.save()

    profile = verification.user.profile
    profile.email_verified = True
    profile.save()
    profile.points += 25
    profile.save()

    messages.success(request, '🎉 Email verified successfully! +25 bonus points awarded.')
    return redirect('dashboard:home')


# ─── PHONE VERIFICATION ─────────────────────────────────────

@login_required
def verify_phone_page(request):
    """Page where user enters phone number and then the OTP."""
    profile = request.user.profile

    if profile.phone_verified:
        messages.info(request, 'Your phone number is already verified.')
        return redirect('dashboard:home')

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'send_otp':
            # User submits their phone number to receive an OTP
            phone_number = request.POST.get('phone_number', '').strip()
            if not phone_number or len(phone_number) < 7:
                messages.error(request, 'Please enter a valid phone number.')
                return render(request, 'accounts/verify_phone.html', {'step': 'enter_phone', 'phone': phone_number})

            # Save phone to profile if not set
            if not profile.phone:
                profile.phone = phone_number
                profile.save()

            _send_phone_otp(request.user, phone_number)
            messages.success(request, f'A verification code has been sent to {phone_number}.')
            return render(request, 'accounts/verify_phone.html', {
                'step': 'enter_otp',
                'phone': phone_number,
            })

        elif action == 'verify_otp':
            # User submits the OTP they received
            otp_input = request.POST.get('otp_code', '').strip()
            phone_number = request.POST.get('phone_number', '')

            if not otp_input or len(otp_input) != 6:
                messages.error(request, 'Please enter a valid 6-digit code.')
                return render(request, 'accounts/verify_phone.html', {
                    'step': 'enter_otp',
                    'phone': phone_number,
                })

            verification = PhoneVerification.objects.filter(
                user=request.user,
                otp_code=otp_input,
                is_used=False,
            ).order_by('-created_at').first()

            if not verification:
                messages.error(request, 'Invalid verification code.')
                return render(request, 'accounts/verify_phone.html', {
                    'step': 'enter_otp',
                    'phone': phone_number,
                })

            if verification.is_expired:
                messages.error(request, 'This code has expired. Please request a new one.')
                return render(request, 'accounts/verify_phone.html', {
                    'step': 'enter_otp',
                    'phone': phone_number,
                })

            # Mark as used and verify phone
            verification.is_used = True
            verification.save()

            profile.phone = verification.phone_number
            profile.phone_verified = True
            profile.save()

            # Award bonus points
            profile.points += 25
            profile.save()

            messages.success(request, '🎉 Phone number verified! +25 bonus points awarded.')

            if profile.email_verified:
                messages.success(request, '✅ You are now fully verified!')

            return redirect('dashboard:home')

    # Default: show phone entry step
    return render(request, 'accounts/verify_phone.html', {
        'step': 'enter_phone',
        'phone': profile.phone or '',
    })


@login_required
def resend_phone_otp(request):
    """Resend phone OTP."""
    profile = request.user.profile

    if profile.phone_verified:
        messages.info(request, 'Your phone is already verified.')
        return redirect('dashboard:home')

    phone_number = profile.phone
    if not phone_number:
        messages.error(request, 'No phone number on file. Please enter your phone number first.')
        return redirect('accounts:verify_phone_page')

    # Rate limiting
    recent = PhoneVerification.objects.filter(
        user=request.user,
        is_used=False,
        created_at__gte=timezone.now() - timezone.timedelta(seconds=60)
    ).exists()

    if recent:
        messages.warning(request, 'Please wait at least 60 seconds before requesting a new code.')
    else:
        _send_phone_otp(request.user, phone_number)
        messages.success(request, f'A new code has been sent to {phone_number}.')

    return redirect('accounts:verify_phone_page')
