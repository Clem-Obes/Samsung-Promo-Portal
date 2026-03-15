from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import hashlib


class Certificate(models.Model):
    """Auto-generated ownership certificate for Samsung Promo Portal winners."""

    CERTIFICATE_TYPES = [
        ('lottery_award', 'Samsung Lottery Award'),
        ('promo_winner', 'Online Promo Winner'),
        ('ambassador', 'Ambassador Recognition'),
        ('referral_champion', 'Referral Champion'),
        ('task_completion', 'Task Completion Award'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('revoked', 'Revoked'),
    ]

    COUNTRY_CHOICES = [
        ('US', '🇺🇸 United States'),
        ('GB', '🇬🇧 United Kingdom'),
        ('CA', '🇨🇦 Canada'),
        ('AU', '🇦🇺 Australia'),
        ('NG', '🇳🇬 Nigeria'),
        ('GH', '🇬🇭 Ghana'),
        ('KE', '🇰🇪 Kenya'),
        ('ZA', '🇿🇦 South Africa'),
        ('TZ', '🇹🇿 Tanzania'),
        ('UG', '🇺🇬 Uganda'),
        ('CM', '🇨🇲 Cameroon'),
        ('SN', '🇸🇳 Senegal'),
        ('CI', '🇨🇮 Ivory Coast'),
        ('ET', '🇪🇹 Ethiopia'),
        ('RW', '🇷🇼 Rwanda'),
        ('BB', '🇧🇧 Barbados'),
        ('JM', '🇯🇲 Jamaica'),
        ('TT', '🇹🇹 Trinidad & Tobago'),
        ('IN', '🇮🇳 India'),
        ('PK', '🇵🇰 Pakistan'),
        ('BD', '🇧🇩 Bangladesh'),
        ('PH', '🇵🇭 Philippines'),
        ('MY', '🇲🇾 Malaysia'),
        ('SG', '🇸🇬 Singapore'),
        ('ID', '🇮🇩 Indonesia'),
        ('AE', '🇦🇪 UAE'),
        ('SA', '🇸🇦 Saudi Arabia'),
        ('DE', '🇩🇪 Germany'),
        ('FR', '🇫🇷 France'),
        ('IT', '🇮🇹 Italy'),
        ('ES', '🇪🇸 Spain'),
        ('NL', '🇳🇱 Netherlands'),
        ('BR', '🇧🇷 Brazil'),
        ('MX', '🇲🇽 Mexico'),
        ('CO', '🇨🇴 Colombia'),
        ('AR', '🇦🇷 Argentina'),
        ('KR', '🇰🇷 South Korea'),
        ('JP', '🇯🇵 Japan'),
        ('CN', '🇨🇳 China'),
        ('EG', '🇪🇬 Egypt'),
        ('MA', '🇲🇦 Morocco'),
        ('IE', '🇮🇪 Ireland'),
        ('SE', '🇸🇪 Sweden'),
        ('NO', '🇳🇴 Norway'),
        ('NZ', '🇳🇿 New Zealand'),
        ('TR', '🇹🇷 Turkey'),
        ('PL', '🇵🇱 Poland'),
    ]

    # Unique certificate identification
    certificate_id = models.CharField(
        max_length=30, unique=True, blank=True, editable=False,
        help_text='Auto-generated unique certificate number'
    )
    verification_hash = models.CharField(
        max_length=64, unique=True, blank=True, editable=False,
        help_text='SHA-256 hash for certificate verification'
    )

    # Recipient info
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='certificates',
        help_text='The user this certificate is issued to'
    )
    recipient_name = models.CharField(
        max_length=200, blank=True,
        help_text='Full name as printed on the certificate (leave blank to auto-fill from user)'
    )
    recipient_location = models.CharField(
        max_length=200, blank=True,
        help_text='Country or city of the recipient'
    )
    recipient_country_code = models.CharField(
        max_length=5, choices=COUNTRY_CHOICES, default='US',
        verbose_name='Recipient Flag / Country',
        help_text='Select the country — its flag will appear on the certificate'
    )

    # Certificate details
    certificate_type = models.CharField(
        max_length=20, choices=CERTIFICATE_TYPES, default='promo_winner'
    )
    award_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='The dollar amount awarded'
    )
    award_description = models.TextField(
        blank=True,
        help_text='Custom description text for the certificate body'
    )
    campaign = models.ForeignKey(
        'promotions.Campaign', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='certificates',
        help_text='The campaign this certificate is related to (optional)'
    )

    # Issuer info
    issuer_name = models.CharField(
        max_length=200, default='Samsung Promo Portal',
        help_text='Name of the issuing authority'
    )
    issuer_title = models.CharField(
        max_length=200, default='Senior Online Manager',
        help_text='Title of the issuing authority'
    )
    authorized_signatory = models.CharField(
        max_length=200, default='Steven Smith',
        help_text='Name of the person who signs the certificate'
    )

    # Status & dates
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='issued'
    )
    issued_date = models.DateField(
        default=timezone.now,
        help_text='Date printed on the certificate'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Winner Certificate'
        verbose_name_plural = 'Winner Certificates'

    def __str__(self):
        return f"Certificate #{self.certificate_id} — {self.recipient_name}"

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = self._generate_certificate_id()
        if not self.verification_hash:
            self.verification_hash = self._generate_verification_hash()
        if not self.award_description:
            self.award_description = self._default_description()
        super().save(*args, **kwargs)

    def _generate_certificate_id(self):
        """Generate a unique certificate ID like SPP-2026-A7F3B2."""
        uid = uuid.uuid4().hex[:6].upper()
        year = timezone.now().year
        return f"SPP-{year}-{uid}"

    def _generate_verification_hash(self):
        """Generate a SHA-256 verification hash."""
        seed = f"{uuid.uuid4().hex}{timezone.now().isoformat()}{self.recipient_name}"
        return hashlib.sha256(seed.encode()).hexdigest()

    def _default_description(self):
        type_label = self.get_certificate_type_display()
        return (
            f"The Actual Owner of the {self._amount_in_words()} Dollars "
            f"Issued To Them By The Samsung Company {self.issuer_title} "
            f"{self.authorized_signatory}\n"
            f"SAMSUNG {type_label.upper()}.\nONLINE PROMO"
        )

    def _amount_in_words(self):
        """Convert award_amount to words for display."""
        amount = int(self.award_amount)
        if amount == 0:
            return "Zero"

        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven',
                'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen',
                'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty',
                'Sixty', 'Seventy', 'Eighty', 'Ninety']

        def _convert_chunk(n):
            if n == 0:
                return ''
            elif n < 20:
                return ones[n]
            elif n < 100:
                return tens[n // 10] + ('' if n % 10 == 0 else ' ' + ones[n % 10])
            else:
                return ones[n // 100] + ' Hundred' + ('' if n % 100 == 0 else ' and ' + _convert_chunk(n % 100))

        if amount >= 1_000_000:
            millions = _convert_chunk(amount // 1_000_000)
            remainder = amount % 1_000_000
            if remainder == 0:
                return f"{millions} Million"
            elif remainder < 1000:
                return f"{millions} Million {_convert_chunk(remainder)}"
            else:
                thousands = _convert_chunk(remainder // 1000)
                rest = remainder % 1000
                parts = f"{millions} Million {thousands} Thousand"
                if rest:
                    parts += f" {_convert_chunk(rest)}"
                return parts
        elif amount >= 1000:
            thousands = _convert_chunk(amount // 1000)
            remainder = amount % 1000
            if remainder == 0:
                return f"{thousands} Thousand"
            else:
                return f"{thousands} Thousand {_convert_chunk(remainder)}"
        else:
            return _convert_chunk(amount)

    @property
    def formatted_amount(self):
        return f"${self.award_amount:,.2f}"

    @property
    def verification_url(self):
        return f"/dashboard/certificate/verify/{self.verification_hash[:16]}/"

    @property
    def short_hash(self):
        return self.verification_hash[:16].upper()

