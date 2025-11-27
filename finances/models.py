from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q, F
from django.utils import timezone


class Unit(models.Model):
    code = models.CharField(max_length=8, unique=True)                 # "PLN", "USD", "XAU"
    symbol = models.CharField(max_length=8)                            # "z\u0142", "$", "oz"
    name = models.CharField(max_length=64)
    decimals = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(12)],      # allow fiat/crypto/commodities
        help_text="Number of fractional digits used for this unit."
    )

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


class OwningSubject(models.Model):
    class Type(models.TextChoices):
        PERSON = "PERSON", "Person"
        HOUSEHOLD = "GROUP", "Group"
        ORGANIZATION = "ORGANIZATION", "Organization"
        OTHER = "OTHER", "Other"


    name = models.CharField(max_length=128)
    type = models.CharField(max_length=16, choices=Type.choices, blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Project(models.Model):
    subject = models.ForeignKey(OwningSubject, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = [("subject", "name")]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.subject})"


class AssetSource(models.Model):
    class Type(models.TextChoices):
        CASH_WALLET = "CASH_WALLET", "Cash wallet"
        BANK_ACCOUNT = "BANK_ACCOUNT", "Bank account"
        PHYSICAL_ASSET = "PHYSICAL_ASSET" "Physical Asset"
        INVESTMENT_ACCOUNT = "INVESTMENT_ACCOUNT" "INVESTMENT_ACCOUNT"
        CARD_ACCOUNT = "CARD_ACCOUNT", "Card Account"
        LIABILITY_ACCOUNT = "LIABILITY_ACCOUNT", "Liability Account"
        CRYPTO_WALLET = "CRYPTO_WALLET", "Crypto Wallet"
        OTHER = "OTHER", "Other"

    subject = models.ForeignKey(OwningSubject, on_delete=models.CASCADE, related_name="asset_sources")
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=64, choices=Type.choices)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="asset_sources")
    external_id = models.CharField(max_length=64, blank=True, null=True, help_text="IBAN, last4, etc.")
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("subject", "name")]
        indexes = [
            models.Index(fields=["subject", "active"]),
            models.Index(fields=["unit"]),
        ]
        ordering = ["subject__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.subject})"


class ExchangeRate(models.Model):
    from_unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="rates_from")
    to_unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="rates_to")
    rate = models.DecimalField(max_digits=24, decimal_places=12, validators=[MinValueValidator(0.000000000001)])
    valid_at = models.DateTimeField()

    class Meta:
        unique_together = [("from_unit", "to_unit", "valid_at")]
        constraints = [
            models.CheckConstraint(
                name="exchange_rate_from_ne_to",
                check=~Q(from_unit=F("to_unit")),
            ),
        ]
        indexes = [
            models.Index(fields=["from_unit", "to_unit", "valid_at"]),
        ]
        ordering = ["-valid_at"]

    def __str__(self):
        return f"{self.from_unit.code}->{self.to_unit.code} @ {self.valid_at:%Y-%m-%d}"


class Transaction(models.Model):
    class Type(models.TextChoices):
        INCOME = "INCOME", "Income"
        EXPENSE = "EXPENSE", "Expense"
        TRANSFER = "TRANSFER", "Transfer"

    class Category(models.TextChoices):
        HOME_MAINTENANCE = "HOME_MAINTENANCE", "Home & maintenance"
        FOOD_GROCERIES = "FOOD_GROCERIES", "Food & groceries"
        HOUSEHOLD_UTILITIES = "HOUSEHOLD_UTILITIES", "Household & utilities"
        CLOTHES_EDC = "CLOTHES_EDC", "Clothes & EDC"
        MOBILITY_TRANSPORT = "MOBILITY_TRANSPORT", "Mobility & Transport"
        FUN_TRAVEL = "FUN_TRAVEL", "Fun & Travel"
        LIFESTYLE_HOBBY = "LIFESTYLE_HOBBY", "Lifestyle & Hobby"
        WORK_EDUCATION = "WORK_EDUCATION", "Work & Education"
        BUSINESS_FINANCE = "BUSINESS_FINANCE", "Business & Finance"
        TAX_FEES = "TAX_FEES", "Tax & Fees"
        GIFTS_FAMILY = "GIFTS_FAMILY", "Gifts & Family"
        OTHER = "OTHER", "Other"

    subject = models.ForeignKey(OwningSubject, on_delete=models.CASCADE, related_name="transactions")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    type = models.CharField(max_length=8, choices=Type.choices)
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(0.00000001)],
        help_text="Always positive. Direction is implied by type."
    )
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="transactions")

    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    category = models.CharField(max_length=32, choices=Category.choices)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name="transactions", null=True, blank=True)

    from_asset_source = models.ForeignKey(
        AssetSource, on_delete=models.PROTECT, null=True, blank=True, related_name="outgoing_transactions"
    )
    to_asset_source = models.ForeignKey(
        AssetSource, on_delete=models.PROTECT, null=True, blank=True, related_name="incoming_transactions"
    )

    class Meta:
        ordering = ["-occurred_at", "-id"]
        indexes = [
            models.Index(fields=["subject", "occurred_at"]),
            models.Index(fields=["type"]),
            models.Index(fields=["category"]),
            models.Index(fields=["project"]),
        ]
        constraints = [
            models.CheckConstraint(name="transaction_amount_gt_zero", check=Q(amount__gt=0)),
            models.CheckConstraint(
                name="transaction_from_to_by_type",
                check=(
                    (Q(type="INCOME") & Q(to_asset_source__isnull=False) & Q(from_asset_source__isnull=True))
                    |
                    (Q(type="EXPENSE") & Q(from_asset_source__isnull=False) & Q(to_asset_source__isnull=True))
                    |
                    (Q(type="TRANSFER") & Q(from_asset_source__isnull=False) & Q(to_asset_source__isnull=False))
                ),
            ),
            models.CheckConstraint(
                name="transaction_transfer_from_ne_to",
                check=(~Q(type="TRANSFER")) | (~Q(from_asset_source=F("to_asset_source"))),
            ),
        ]

    def clean(self):
        """
        Cross-object validation:
        - Any referenced AssetSource(s) must belong to the same subject as the transaction.
        - If project is set, it must belong to the same subject.
        """
        from django.core.exceptions import ValidationError

        if self.from_asset_source and self.from_asset_source.subject_id != self.subject_id:
            raise ValidationError("from_asset_source must belong to the same subject as the transaction.")

        if self.to_asset_source and self.to_asset_source.subject_id != self.subject_id:
            raise ValidationError("to_asset_source must belong to the same subject as the transaction.")

        if self.project and self.project.subject_id != self.subject_id:
            raise ValidationError("project must belong to the same subject as the transaction.")

    def __str__(self):
        return f"{self.get_type_display()} {self.amount} {self.unit.code} \u2014 {self.title}"


class UserPreferences(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="preferences")
    default_unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    timezone = models.CharField(max_length=64, default="Europe/Warsaw")
    locale = models.CharField(max_length=16, default="pl_PL")

    def __str__(self):
        return f"Prefs({self.user})"


class SubjectUserAccess(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        EDITOR = "EDITOR", "Editor"
        VIEWER = "VIEWER", "Viewer"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subject_access")
    subject = models.ForeignKey(OwningSubject, on_delete=models.CASCADE, related_name="user_access")
    role = models.CharField(max_length=8, choices=Role.choices)

    class Meta:
        unique_together = [("user", "subject")]
        indexes = [
            models.Index(fields=["subject", "role"]),
        ]

    def __str__(self):
        return f"{self.user} \u2192 {self.subject} ({self.get_role_display()})"
