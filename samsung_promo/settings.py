"""
Django settings for samsung_promo project.
Samsung Promotion Portal
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-vow1q2$6hdhjr7ip)5q_7uzieq*7=wsbxr&3hwc@+6&k@+*lcj'

DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Third party
    'crispy_forms',
    'crispy_bootstrap5',
    # Local apps
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'dashboard.apps.DashboardConfig',
    'promotions.apps.PromotionsConfig',
    'payments.apps.PaymentsConfig',
    'support.apps.SupportConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'samsung_promo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'samsung_promo.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Auth settings
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'core:home'

# Paystack settings (configure later)
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY', '')
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY', '')

# Email settings (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Samsung Promo Portal <noreply@samsungpromo.com>'

# =============================================================================
# JAZZMIN ADMIN THEME CONFIGURATION
# =============================================================================
JAZZMIN_SETTINGS = {
    # Title & Branding
    'site_title': 'Samsung Promos',
    'site_header': 'Samsung Promos',
    'site_brand': '📱 Samsung Promos',
    'site_logo': 'images/worker/support/samsung building.jpg',
    'login_logo': 'images/worker/support/samsung building.jpg',
    'login_logo_dark': 'images/worker/support/samsung building.jpg',
    'site_logo_classes': '',
    'site_icon': None,
    'welcome_sign': 'Welcome! Sign in to manage your Samsung Promotions',
    'copyright': 'Samsung Promo Portal © 2026',

    # Search — users can search these from the top bar
    'search_model': ['auth.User', 'accounts.UserProfile', 'promotions.Campaign'],
    'search_placeholder': 'Search users, profiles, campaigns...',

    # Top Menu Links — quick shortcuts at the top
    'topmenu_links': [
        {'name': '🏠 Dashboard', 'url': 'admin:index', 'permissions': ['auth.view_user']},
        {'name': '🌐 View Website', 'url': '/', 'new_window': True},
        {'name': '📨 Support Inbox', 'url': '/admin/support/contactmessage/', 'permissions': ['auth.view_user']},
        {'name': '👥 All Users', 'url': '/admin/auth/user/'},
    ],

    # User Menu Links (top-right avatar dropdown)
    'usermenu_links': [
        {'name': '🌐 View Website', 'url': '/', 'new_window': True, 'icon': 'fas fa-globe'},
        {'model': 'auth.User'},
    ],

    # Side Menu Configuration
    'show_sidebar': True,
    'navigation_expanded': True,
    'hide_apps': [],
    'hide_models': [],

    # Custom ordering of apps and models in sidebar
    'order_with_respect_to': [
        'auth',
        'accounts',
        'core',
        'promotions',
        'payments',
        'support',
    ],

    # Custom app icons (Font Awesome 5)
    'icons': {
        'auth': 'fas fa-shield-alt',
        'auth.User': 'fas fa-users',
        'auth.Group': 'fas fa-user-tag',
        'accounts': 'fas fa-id-card',
        'accounts.UserProfile': 'fas fa-user-circle',
        'accounts.EmailVerification': 'fas fa-envelope-open-text',
        'accounts.PhoneVerification': 'fas fa-mobile-alt',
        'core': 'fas fa-tv',
        'core.Device': 'fas fa-mobile-alt',
        'core.Testimonial': 'fas fa-star',
        'core.SiteSettings': 'fas fa-sliders-h',
        'core.Announcement': 'fas fa-bullhorn',
        'core.TestimonyComment': 'fas fa-comments',
        'promotions': 'fas fa-rocket',
        'promotions.Campaign': 'fas fa-flag',
        'promotions.Task': 'fas fa-tasks',
        'promotions.UserTask': 'fas fa-clipboard-check',
        'promotions.Referral': 'fas fa-people-arrows',
        'promotions.RewardClaim': 'fas fa-gift',
        'payments': 'fas fa-credit-card',
        'payments.MembershipPlan': 'fas fa-gem',
        'payments.Payment': 'fas fa-money-bill-wave',
        'payments.UserMembership': 'fas fa-id-badge',
        'support': 'fas fa-headset',
        'support.ContactMessage': 'fas fa-inbox',
        'support.ChatMessage': 'fas fa-comment-dots',
        'support.Comment': 'fas fa-comment-alt',
    },
    'default_icon_parents': 'fas fa-folder',
    'default_icon_children': 'fas fa-circle',

    # Related Modal (popup for FK selection)
    'related_modal_active': True,

    # UI Tweaks
    'custom_css': 'css/admin-custom.css',
    'custom_js': None,
    'use_google_fonts_cdn': True,
    'show_ui_builder': False,

    # Change view
    'changeform_format': 'horizontal_tabs',
    'changeform_format_overrides': {
        'auth.user': 'collapsible',
        'auth.group': 'vertical_tabs',
    },

    'language_chooser': False,
}

JAZZMIN_UI_TWEAKS = {
    'navbar_small_text': False,
    'footer_small_text': True,
    'body_small_text': False,
    'brand_small_text': False,
    'brand_colour': 'navbar-white',
    'accent': 'accent-primary',
    'navbar': 'navbar-white navbar-light',
    'no_navbar_border': False,
    'navbar_fixed': True,
    'layout_boxed': False,
    'footer_fixed': False,
    'sidebar_fixed': True,
    'sidebar': 'sidebar-light-primary',
    'sidebar_nav_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_child_indent': True,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style': False,
    'theme': 'cosmo',
    'dark_mode_theme': None,
    'button_classes': {
        'primary': 'btn-primary',
        'secondary': 'btn-outline-secondary',
        'info': 'btn-info',
        'warning': 'btn-warning',
        'danger': 'btn-danger',
        'success': 'btn-success',
    },
    'actions_sticky_top': True,
}
