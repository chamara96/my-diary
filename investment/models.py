from django.contrib.auth.models import User
from django.db import models

from income.models import Currency


class TransactionType:
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"

    CHOICES = [
        (DEPOSIT, "Deposit"),
        (WITHDRAWAL, "Withdrawal"),
    ]


class Bank(models.Model):
    name = models.CharField(max_length=100)
    currency = models.CharField(
        max_length=6, choices=Currency.CHOICES, default=Currency.LKR
    )

    def __str__(self):
        return self.name


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(
        max_length=6, choices=Currency.CHOICES, default=Currency.LKR
    )
    date = models.DateField(auto_now=True)
    note = models.TextField(blank=True, null=True)
    type = models.CharField(
        max_length=20, choices=TransactionType.CHOICES, default=TransactionType.DEPOSIT
    )

    def save(self, *args, **kwargs):
        if self.type == TransactionType.WITHDRAWAL:
            self.amount = -abs(self.amount)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency}"
