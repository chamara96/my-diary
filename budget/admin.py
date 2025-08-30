from django.contrib import admin
from django.db.models import Sum
from django.template.response import TemplateResponse
from django.urls import path, reverse

from income.models import Income

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


# Add a custom view to AdminSite
def custom_summary_view(request):
    incomes = Income.objects.filter(is_template=False)
    # Calculate total take-home income grouped by user and month and currency
    total_take_home_group = (
        incomes.values(
            "user__username",
            "date__year",
            "date__month",
            "currency",
            "exchange_rate_lkr",
            "tax",
            "is_tax_paid",
        )
        .annotate(total_take_home=Sum("take_home"))
        .order_by("user__username", "date__year", "date__month", "currency")
    )
    formatted_data = []
    for item in total_take_home_group:
        year = item["date__year"]
        month = MONTHS[item["date__month"] - 1]  # Convert month number to name
        user = item["user__username"]
        currency = item["currency"]
        total_take_home = round(item["total_take_home"], 2)

        # Find or create the year-month entry
        year_month_entry = next(
            (
                entry
                for entry in formatted_data
                if entry["year"] == year and entry["month"] == month
            ),
            None,
        )
        if not year_month_entry:
            year_month_entry = {"year": year, "month": month, "users": []}
            formatted_data.append(year_month_entry)

        # Find or create the user entry
        user_entry = next(
            (u for u in year_month_entry["users"] if u["user"] == user), None
        )
        if not user_entry:
            user_entry = {"user": user, "incomes": []}
            year_month_entry["users"].append(user_entry)

        # Add the currency and total to the user's incomes
        sub_income = {"currency": currency, "total": total_take_home}
        if currency != "LKR":
            sub_income["total_lkr"] = total_take_home * item["exchange_rate_lkr"]
            sub_income["payble_tax"] = 0
            if not item["is_tax_paid"]:
                sub_income["payble_tax"] = float(item["tax"])

        user_entry["incomes"].append(sub_income)

        # user total in LKR:
        user_entry["total_income"] = round(
            sum(
                income["total_lkr"] if "total_lkr" in income else income["total"]
                for income in user_entry["incomes"]
            ),
            2,
        )

        # Payble tax
        user_entry["total_payble_tax"] = round(
            sum(
                income["payble_tax"] if "payble_tax" in income else 0
                for income in user_entry["incomes"]
            ),
            2,
        )

        # Add the total income for the user in the year-month
        year_month_entry["total_income"] = round(
            sum(user["total_income"] for user in year_month_entry["users"]), 2
        )

        # Total payble tax in month
        year_month_entry["total_payble_tax"] = round(
            sum(user["total_payble_tax"] for user in year_month_entry["users"]), 2
        )

    context = dict(
        admin_site.each_context(request),
        title="Summary Report",
        summary_data=formatted_data,
    )
    return TemplateResponse(request, "admin/custom_summary.html", context)


class MyAdminSite(admin.AdminSite):
    site_header = "My Budget"
    site_title = "MyBudget"
    index_title = "Welcome to the Admin Portal"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "custom-summary/",
                self.admin_view(custom_summary_view),
                name="custom-summary",
            ),
        ]
        return custom_urls + urls

    def each_context(self, request):
        context = super().each_context(request)

        # Inject fake app + model into app_list for the sidebar
        custom_app = {
            "name": "Reports",
            "app_label": "reports",
            "app_url": "",
            "has_module_perms": True,
            "models": [
                {
                    "name": "Summary Report",
                    "object_name": "SummaryReport",
                    "admin_url": "/admin/custom-summary/",
                    "add_url": None,
                    "perms": {"change": True},
                },
            ],
        }

        # Append to existing apps
        context["available_apps"].append(custom_app)
        return context


# Use your custom AdminSite instead of the default one
admin_site = MyAdminSite(name="myadmin")
