from django.db import models


class Vehicle(models.Model):
    name = models.CharField(max_length=100)
    plate_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name}"


class Garage(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

    class Meta:
        ordering = ["name"]
        verbose_name = "Garage"
        verbose_name_plural = "Garages"

    def __str__(self):
        return f"{self.name} - {self.location}"


class Shop(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

    class Meta:
        ordering = ["name"]
        verbose_name = "Shop"
        verbose_name_plural = "Shops"

    def __str__(self):
        return f"{self.name} - {self.location}"


class VehicleService(models.Model):
    SERVICE_TYPES = [
        ("maintenance", "Regular Maintenance"),
        ("repair", "Repair"),
        ("inspection", "Inspection"),
        ("oil_change", "Oil Change"),
        ("tire_change", "Tire Change"),
        ("other", "Other"),
    ]

    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="services"
    )
    service_date = models.DateField()
    service_type = models.CharField(
        max_length=20, choices=SERVICE_TYPES, default="maintenance"
    )
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    mileage = models.PositiveIntegerField(
        null=True, blank=True, help_text="Vehicle mileage at time of service"
    )
    garage = models.ForeignKey(
        Garage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="services",
    )

    class Meta:
        ordering = ["-service_date"]
        verbose_name = "Vehicle Service"
        verbose_name_plural = "Vehicle Services"

    def __str__(self):
        return f"{self.vehicle} - {self.service_date} "


class ServicePart(models.Model):
    service = models.ForeignKey(
        VehicleService, on_delete=models.CASCADE, related_name="parts"
    )
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="parts_sold")
    part_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["service", "part_name"]
        verbose_name = "Service Part"
        verbose_name_plural = "Service Parts"

    def __str__(self):
        return f"{self.service} - {self.part_name} (x{self.quantity})"


class VehicleServiceDocument(models.Model):
    service = models.ForeignKey(
        VehicleService, on_delete=models.CASCADE, related_name="documents"
    )
    document = models.FileField(upload_to="vehicle_service_docs/")

    def __str__(self):
        return f"{self.service} - {self.document.name}"
