from django.contrib import admin
from django.db.models import Sum

from budget.admin import admin_site

from .models import Bank, Transaction

# def fetch_currency_exchange_rate_live


EXCHANGE_RATES = {
    "LKR": 1,
    "EUR": 344.9,  # example rate
    "AUD": 191.7,  # example rate
}


class BankAdmin(admin.ModelAdmin):
    list_display = ("name", "currency")
    search_fields = ("name",)
    list_filter = ("currency",)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "user", "bank", "amount", "currency", "type")
    list_filter = ("currency", "type", "date", "bank")
    change_list_template = "admin/investment/transaction_changelist.html"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        try:
            queryset = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response

        # Calculate summary per user & bank
        summary_data = (
            queryset.values("user__username", "bank__name", "currency")
            .annotate(total_amount=Sum("amount"))
            .order_by("user__username", "bank__name")
        )

        # Convert to LKR
        for row in summary_data:
            currency = row["currency"]
            rate = EXCHANGE_RATES.get(currency, 1)
            row["amount_lkr"] = float(row["total_amount"] or 0) * rate

        # Calculate grand total in LKR
        grand_total_lkr = sum(row["amount_lkr"] for row in summary_data)

        extra_context = extra_context or {}
        extra_context["summary_data"] = summary_data
        extra_context["grand_total_lkr"] = grand_total_lkr

        response.context_data.update(extra_context)
        return response


admin_site.register(Bank, BankAdmin)
admin_site.register(Transaction, TransactionAdmin)
