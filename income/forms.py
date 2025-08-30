from django import forms
from django.utils import timezone

from .models import Income


class GenerateFromTemplateForm(forms.Form):
    template = forms.ModelChoiceField(
        queryset=Income.objects.filter(is_template=True),
        label="Template",
        help_text="Select an income template",
    )
    exchange_rate_lkr = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Exchange rate to LKR (if applicable)",
    )
    date = forms.DateField(
        initial=timezone.now().date(),
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Date",
    )
