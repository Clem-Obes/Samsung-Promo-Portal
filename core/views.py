from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Device, Testimonial, SiteSettings, Announcement, TestimonyComment, NewsletterSubscriber
from .forms import TestimonyCommentForm
from payments.models import MembershipPlan
from support.models import ContactMessage


def home(request):
    devices = Device.objects.filter(is_featured=True)[:6]
    testimonials = Testimonial.objects.filter(status='approved')[:6]
    announcements = Announcement.objects.filter(is_active=True)[:3]
    plans = MembershipPlan.objects.filter(is_active=True)[:3]

    try:
        settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        settings = None

    context = {
        'devices': devices,
        'testimonials': testimonials,
        'announcements': announcements,
        'plans': plans,
        'site_settings': settings,
    }
    return render(request, 'core/home.html', context)


def testimonials(request):
    testimonials_list = Testimonial.objects.filter(status='approved')
    # Show approved comments to everyone + user's own pending comments
    from django.db.models import Q
    comments_qs = TestimonyComment.objects.select_related('user').prefetch_related('likes')
    if request.user.is_authenticated:
        comments = comments_qs.filter(
            Q(status='approved') | Q(user=request.user)
        ).distinct()
    else:
        comments = comments_qs.filter(status='approved')

    form = TestimonyCommentForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'You must be logged in to share your testimony.')
            return redirect('accounts:login')
        form = TestimonyCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.save()
            messages.success(request, 'Your testimony has been submitted successfully! It will be visible to others after admin approval.')
            return redirect('core:testimonials')

    context = {
        'testimonials': testimonials_list,
        'comments': comments,
        'form': form,
    }
    return render(request, 'core/testimonials.html', context)


@login_required
def like_testimony(request, pk):
    from django.db.models import Q
    comment = get_object_or_404(TestimonyComment, Q(status='approved') | Q(user=request.user), pk=pk)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': comment.like_count})


def how_it_works(request):
    return render(request, 'core/process.html')


def pricing(request):
    plans = MembershipPlan.objects.filter(is_active=True)
    return render(request, 'core/pricing.html', {'plans': plans})


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
            user=request.user if request.user.is_authenticated else None
        )
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('core:contact')

    return render(request, 'core/contact.html')


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')


def terms_of_service(request):
    return render(request, 'core/terms_of_service.html')


def cookie_policy(request):
    return render(request, 'core/cookie_policy.html')


def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Please enter a valid email address.')
        else:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email.lower(),
                defaults={'is_active': True}
            )
            if created:
                messages.success(request, '🎉 You\'ve been subscribed! Watch your inbox for the latest Samsung promos.')
            elif not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save()
                messages.success(request, 'Welcome back! You\'ve been re-subscribed to our newsletter.')
            else:
                messages.info(request, 'You\'re already subscribed to our newsletter.')

    # Redirect back to the page they came from
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)
