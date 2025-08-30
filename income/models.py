from django.contrib.auth.models import User
from django.db import models


class Currency:
    LKR = "LKR"
    EUR = "EUR"
    AUD = "AUD"

    CHOICES = [
        (LKR, "Sri Lankan Rupee"),
        (EUR, "Euro"),
        (AUD, "Australian Dollar"),
    ]


class Type:
    SALARY = "Salary"
    BONUS = "Bonus"
    OTHER = "Other"

    CHOICES = [
        (SALARY, "Salary"),
        (BONUS, "Bonus"),
        (OTHER, "Other"),
    ]


class Source(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    currency = models.CharField(
        max_length=6, choices=Currency.CHOICES, default=Currency.LKR
    )
    exchange_rate_lkr = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    date = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=Type.CHOICES, default=Type.SALARY)
    note = models.TextField(blank=True, null=True)
    is_template = models.BooleanField(default=False)
    # Earnings
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_allowance_for_funds = models.BooleanField(default=False)
    # Deductions
    stamp_duty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    epf_user = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_tax_paid = models.BooleanField(default=True)
    other_deductions = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    # Net Income
    take_home = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # Employer Contributions
    epf_employer = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    etf_employer = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.source.name}({self.currency}) - {self.type}"

    class Meta:
        verbose_name_plural = "Incomes"
