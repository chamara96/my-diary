from django.contrib import admin
from django.utils.html import mark_safe

from budget.admin import admin_site

from .models import ServicePart, VehicleService, VehicleServiceDocument


class VehicleServiceDocumentInline(admin.TabularInline):
    model = VehicleServiceDocument
    extra = 0
    fields = ("document",)


class ServicePartInline(admin.TabularInline):
    model = ServicePart
    extra = 0  # No extra forms by default since focus is on list view
    fields = ("shop", "part_name", "quantity", "total_cost")
    verbose_name = "Service Part"
    verbose_name_plural = "Service Parts"


class VehicleServiceAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle",
        "service_date",
        "service_type",
        "cost",
        "get_parts_summary",
        "get_parts_total_cost",
        "get_total_cost_with_parts",
        "garage",
    )
    date_hierarchy = "service_date"
    ordering = ("-service_date",)
    fields = (
        "vehicle",
        "service_date",
        "service_type",
        "description",
        "cost",
        "mileage",
        "garage",
    )
    inlines = [ServicePartInline, VehicleServiceDocumentInline]
    list_per_page = 25
    actions = None

    class Media:
        css = {"all": ("admin/css/changelists.css",)}

    def get_parts_total_cost(self, obj):
        """Calculate total cost of all parts for this service"""
        return sum(part.total_cost for part in obj.parts.all())

    def get_total_cost_with_parts(self, obj):
        """Calculate total cost including service cost and parts cost"""
        parts_cost = self.get_parts_total_cost(obj)
        return obj.cost + parts_cost

    def get_parts_summary(self, obj):
        """Display parts summary with better formatting for admin"""
        parts = obj.parts.all()
        if not parts:
            return "No parts"
        parts_info = []
        for part in parts:
            parts_info.append(
                f"""<li>
                <strong>{part.part_name}</strong> - LKR {part.total_cost}
                </li>"""
            )
        # wrap the parts_info in a ul tag
        parts_info = "<ul>" + "".join(parts_info) + "</ul>"
        # html render the parts_info
        return mark_safe(parts_info)

    get_parts_summary.short_description = "Parts Details"
    get_parts_total_cost.short_description = "Parts Total"
    get_total_cost_with_parts.short_description = "Total (Service + Parts)"


admin_site.register(VehicleService, VehicleServiceAdmin)
