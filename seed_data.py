"""
Seed script to populate the Samsung Promotion Portal with sample data.
Run: python manage.py shell < seed_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsung_promo.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Device, Testimonial, SiteSettings, Announcement
from promotions.models import Campaign, Task
from payments.models import MembershipPlan
from support.models import ContactMessage
from django.utils import timezone
from datetime import timedelta

print("🌱 Seeding Samsung Promotion Portal...")

now = timezone.now()

# ── Site Settings ──
site, _ = SiteSettings.objects.get_or_create(
    pk=1,
    defaults={
        'site_name': 'Samsung Promotion Portal',
        'hero_title': 'Promote. Earn. Win Amazing Samsung Devices!',
        'hero_subtitle': 'Join thousands of Samsung ambassadors earning real rewards through our exclusive promotion program.',
        'promo_countdown': now + timedelta(days=30),
        'total_participants': 12500,
        'total_rewards': 3200,
        'is_promo_active': True,
    }
)
print("✅ Site Settings created")

# ── Announcements ──
Announcement.objects.get_or_create(
    title="🎉 Grand Launch Promotion!",
    defaults={
        'content': 'Join our grand launch and earn 2x points on all tasks this week! Limited time offer.',
        'is_active': True,
    }
)
print("✅ Announcements created")

# ── Featured Devices ──
devices_data = [
    {
        'name': 'Samsung Galaxy S24 Ultra',
        'description': 'The ultimate smartphone with AI-powered features, 200MP camera, and S Pen.',
        'price': 1899999.00,
        'is_featured': True,
    },
    {
        'name': 'Samsung Galaxy Z Fold 5',
        'description': 'Unfold your world with the revolutionary foldable phone experience.',
        'price': 1599999.00,
        'is_featured': True,
    },
    {
        'name': 'Samsung Galaxy Watch 6 Classic',
        'description': 'Premium smartwatch with rotating bezel, health monitoring, and sleek design.',
        'price': 459999.00,
        'is_featured': True,
    },
    {
        'name': 'Samsung Galaxy Buds 3 Pro',
        'description': 'Immersive sound with intelligent ANC and 360 Audio for an unmatched experience.',
        'price': 299999.00,
        'is_featured': True,
    },
    {
        'name': 'Samsung 65" Neo QLED 4K TV',
        'description': 'Stunning visuals with Quantum Matrix Technology and Dolby Atmos sound.',
        'price': 2499999.00,
        'is_featured': False,
    },
    {
        'name': 'Samsung Galaxy Tab S9+',
        'description': 'The ultimate Android tablet with AMOLED display and S Pen included.',
        'price': 999999.00,
        'is_featured': True,
    },
]

for d in devices_data:
    Device.objects.get_or_create(name=d['name'], defaults=d)
print(f"✅ {len(devices_data)} Devices created")

# ── Testimonials ──
testimonials_data = [
    {
        'name': 'Adebayo Johnson',
        'location': 'Lagos, Nigeria',
        'quote': 'I earned my Galaxy S24 Ultra in just 3 months! The referral system is amazing. I started by sharing with friends and it snowballed from there.',
        'device_received': 'Galaxy S24 Ultra',
        'rating': 5,
        'status': 'approved',
    },
    {
        'name': 'Chioma Okafor',
        'location': 'Abuja, Nigeria',
        'quote': 'This platform changed how I see promotions. Real rewards for real effort. Already redeemed Galaxy Buds and working towards the Watch!',
        'device_received': 'Galaxy Buds 3 Pro',
        'rating': 5,
        'status': 'approved',
    },
    {
        'name': 'Ibrahim Musa',
        'location': 'Kano, Nigeria',
        'quote': 'Started 2 weeks ago and already accumulated 800 points. The tasks are fun and the community is supportive. Highly recommend!',
        'device_received': '',
        'rating': 4,
        'status': 'approved',
    },
    {
        'name': 'Funke Akindele',
        'location': 'Ibadan, Nigeria',
        'quote': 'The best promotion platform in Nigeria! I have referred over 50 people and the rewards keep coming. Samsung devices are top quality.',
        'device_received': 'Galaxy Watch 6',
        'rating': 5,
        'status': 'approved',
    },
    {
        'name': 'Emeka Nwosu',
        'location': 'Port Harcourt, Nigeria',
        'quote': 'I was skeptical at first, but after receiving my first reward, I became a believer. Transparent, fair, and exciting!',
        'device_received': 'Galaxy Buds 3 Pro',
        'rating': 4,
        'status': 'approved',
    },
    {
        'name': 'Aisha Mohammed',
        'location': 'Kaduna, Nigeria',
        'quote': 'As a top ambassador, I can say this platform truly delivers. Multiple devices redeemed and the support team is always helpful.',
        'device_received': 'Galaxy Z Fold 5',
        'rating': 5,
        'status': 'approved',
    },
]

for t in testimonials_data:
    Testimonial.objects.get_or_create(name=t['name'], defaults=t)
print(f"✅ {len(testimonials_data)} Testimonials created")

# ── Membership Plans ──
plans_data = [
    {
        'name': 'Starter',
        'slug': 'starter',
        'price': 2500.00,
        'description': 'Perfect for beginners who want to explore the Samsung promotion program.',
        'benefits': 'Access to basic campaigns\nEarn up to 500 points/month\n5 referral slots\nEmail support\nBasic dashboard',
        'is_popular': False,
        'order': 1,
    },
    {
        'name': 'Pro',
        'slug': 'pro',
        'price': 5000.00,
        'description': 'For serious promoters ready to maximize their earnings and rewards.',
        'benefits': 'Access to all campaigns\nEarn up to 2000 points/month\n25 referral slots\nPriority support\nFull dashboard\n2x point multiplier\nExclusive promotions',
        'is_popular': True,
        'order': 2,
    },
    {
        'name': 'Elite',
        'slug': 'elite',
        'price': 10000.00,
        'description': 'The ultimate plan for top ambassadors seeking maximum rewards and VIP access.',
        'benefits': 'Access to all campaigns + VIP\nUnlimited points earning\nUnlimited referral slots\n24/7 dedicated support\nAdvanced analytics\n3x point multiplier\nFirst access to new devices\nAmbassador badge\nMonthly bonus rewards',
        'is_popular': False,
        'order': 3,
    },
]

for p in plans_data:
    MembershipPlan.objects.get_or_create(slug=p['slug'], defaults=p)
print(f"✅ {len(plans_data)} Membership Plans created")

# ── Campaigns ──
campaigns_data = [
    {
        'title': 'Galaxy S24 Ultra Launch Campaign',
        'description': 'Celebrate the launch of the Galaxy S24 Ultra! Complete tasks, share on social media, and earn massive points. Top performers win a free Galaxy S24 Ultra!',
        'start_date': now - timedelta(days=5),
        'end_date': now + timedelta(days=25),
        'reward_description': 'Win a Galaxy S24 Ultra + 500 bonus points',
        'status': 'active',
        'max_participants': 1000,
    },
    {
        'title': 'Refer-a-Friend Mega Bonus',
        'description': 'Refer your friends and earn double points for every successful referral this month! The more friends you bring, the closer you get to your dream Samsung device.',
        'start_date': now - timedelta(days=3),
        'end_date': now + timedelta(days=27),
        'reward_description': '2x referral points + 300 bonus points',
        'status': 'active',
        'max_participants': 500,
    },
    {
        'title': 'Social Media Challenge',
        'description': 'Share Samsung content on your social media platforms and earn points! Post reviews, unboxing videos, or creative content featuring Samsung products.',
        'start_date': now,
        'end_date': now + timedelta(days=14),
        'reward_description': 'Galaxy Buds 3 Pro + 200 bonus points',
        'status': 'active',
        'max_participants': 2000,
    },
    {
        'title': 'Galaxy Z Fold 5 Experience Week',
        'description': 'An exclusive campaign for our premium members. Share your Galaxy Z Fold 5 experience and stand a chance to win exciting accessories!',
        'start_date': now + timedelta(days=10),
        'end_date': now + timedelta(days=24),
        'reward_description': 'Exclusive Samsung accessories + 400 bonus points',
        'status': 'upcoming',
        'max_participants': 300,
    },
    {
        'title': 'Valentine Special - Share the Love',
        'description': 'This Valentine season, share the love of Samsung with someone special. Complete love-themed tasks and win a pair of Galaxy Buds 3 Pro!',
        'start_date': now - timedelta(days=30),
        'end_date': now - timedelta(days=2),
        'reward_description': 'Galaxy Buds 3 Pro pair + 350 bonus points',
        'status': 'ended',
        'max_participants': 800,
    },
]

for c in campaigns_data:
    campaign, created = Campaign.objects.get_or_create(title=c['title'], defaults=c)
    if created:
        # Add tasks to active campaigns
        if c['status'] in ['active', 'upcoming']:
            Task.objects.create(
                campaign=campaign,
                title='Share campaign on social media',
                description='Share this campaign post on Facebook, Twitter, or Instagram with the hashtag #SamsungPromo',
                task_type='social',
                points=50,
                order=1,
            )
            Task.objects.create(
                campaign=campaign,
                title='Refer 3 friends to join',
                description='Invite 3 friends to register on the platform using your referral link.',
                task_type='refer',
                points=100,
                order=2,
            )
            Task.objects.create(
                campaign=campaign,
                title='Write a product review',
                description='Write a genuine review of any Samsung product you own or have used.',
                task_type='review',
                points=75,
                order=3,
            )
            Task.objects.create(
                campaign=campaign,
                title='Follow Samsung on all platforms',
                description='Follow our official Samsung social media accounts on Facebook, Twitter, Instagram, and TikTok.',
                task_type='follow',
                points=30,
                order=4,
            )

print(f"✅ {len(campaigns_data)} Campaigns created with tasks")

print("\n🎉 Seeding complete! Your Samsung Promotion Portal is ready.")
print("━" * 50)
print("🔑 Admin Login:")
print("   URL: http://127.0.0.1:8000/admin/")
print("   Username: admin")
print("   Password: admin123")
print("━" * 50)
