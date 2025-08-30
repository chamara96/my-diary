from urllib.parse import urlencode

from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import path, reverse

from budget.admin import admin_site

from .forms import GenerateFromTemplateForm
from .models import Income, Source


class SourceAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]


class IncomeForm(forms.ModelForm):
    def clean_exchange_rate_lkr(self):
        cleaned_data = super().clean()
        currency = cleaned_data.get("currency")
        is_template = cleaned_data.get("is_template", False)
        exchange_rate = cleaned_data.get("exchange_rate_lkr")
        if currency != "LKR" and not is_template:
            if not exchange_rate or exchange_rate <= 0:
                raise forms.ValidationError(
                    "Exchange rate must be a positive number for non-LKR currencies."
                )
        return exchange_rate


class IncomeAdmin(admin.ModelAdmin):
    form = IncomeForm
    list_display = (
        "get_income_month",
        "user",
        "source",
        "get_currency",
        "date",
        "type",
        "basic_amount",
        "allowance",
        "tax",
        "epf_user",
        "epf_employer",
        "etf_employer",
        "take_home",
    )
    list_display_links = ("user", "source")
    fields = (
        "is_template",
        "user",
        "source",
        "currency",
        "exchange_rate_lkr",
        "date",
        "type",
        "note",
        "basic_amount",
        "allowance",
        "is_allowance_for_funds",
        "tax",
        "stamp_duty",
        "other_deductions",
        "is_tax_paid",
        # read-only calculated fields
        "epf_user",
        "epf_employer",
        "etf_employer",
        "take_home",
    )
    ordering = ["-date__year", "-date__month", "user__username", "source__name"]
    readonly_fields = ("epf_user", "epf_employer", "etf_employer", "take_home")
    list_filter = ("user", "date", "is_template")
    date_hierarchy = "date"
    # change_list_template = "income_changelist.html"
    change_list_template = "admin/income/income_change_list.html"

    def get_income_month(self, obj):
        return obj.date.strftime("%Y %B") if obj.date else "No Date"

    def get_currency(self, obj):
        return obj.currency

    def save_model(self, request, obj, form, change):
        self._recalculate_fields(obj)
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "generate-from-template/",
                self.admin_site.admin_view(self.generate_from_template_view),
                name="income-generate-template",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context["generate_template_url"] = reverse(
            "admin:income-generate-template"
        )

        if "is_template__exact" not in request.GET:
            q = request.GET.copy()
            q["is_template__exact"] = "0"
            return HttpResponseRedirect(f"{request.path}?{urlencode(q)}")
        return super().changelist_view(request, extra_context=extra_context)

    def generate_from_template_view(self, request):
        if request.method == "POST":
            form = GenerateFromTemplateForm(request.POST)
            if form.is_valid():
                template = form.cleaned_data["template"]
                date = form.cleaned_data["date"]

                new_income = Income.objects.get(pk=template.pk)
                new_income.pk = None
                new_income.date = date
                new_income.is_template = False
                # self._recalculate_fields(new_income)
                new_income.save()

                self.message_user(
                    request,
                    f"Income record generated successfully from template '{template}'.",
                    level=messages.SUCCESS,
                )
                return redirect("..")
        else:
            form = GenerateFromTemplateForm()

        return render(
            request,
            "admin/income/income_generate_form.html",
            {
                "form": form,
                "title": "Generate Income From Template",
                "opts": self.model._meta,
            },
        )

    def _recalculate_fields(self, obj):
        is_salary_in_lkr = obj.type == "Salary" and obj.currency == "LKR"

        if is_salary_in_lkr:
            if obj.is_allowance_for_funds:
                obj.epf_user = (float(obj.basic_amount) + float(obj.allowance)) * 0.08
                obj.epf_employer = (
                    float(obj.basic_amount) + float(obj.allowance)
                ) * 0.12
                obj.etf_employer = (
                    float(obj.basic_amount) + float(obj.allowance)
                ) * 0.03
            else:
                obj.epf_user = float(obj.basic_amount) * 0.08
                obj.epf_employer = float(obj.basic_amount) * 0.12
                obj.etf_employer = float(obj.basic_amount) * 0.03
        else:
            obj.epf_user = 0
            obj.epf_employer = 0
            obj.etf_employer = 0

        obj.take_home = (
            float(obj.basic_amount)
            + float(obj.allowance)
            - float(obj.epf_user)
            - float(obj.stamp_duty)
            - float(obj.other_deductions)
        )
        if obj.is_tax_paid:
            obj.take_home -= float(obj.tax)


admin_site.register(Income, IncomeAdmin)
admin_site.register(Source, SourceAdmin)
