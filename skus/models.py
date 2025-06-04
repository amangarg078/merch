from django.db import models


class SKU(models.Model):
    """
    Represents a Stock Keeping Unit (SKU) with various attributes.
    """
    sku_id = models.CharField(max_length=100, unique=True, verbose_name="SKU ID")
    name = models.CharField(max_length=255, verbose_name="Product Name")
    sales = models.IntegerField(default=0, verbose_name="Total Sales")
    return_percentage = models.FloatField(default=0, verbose_name="Returns Percentage")
    content_score = models.FloatField(default=0.0, verbose_name="Content Score")

    class Meta:
        verbose_name = "SKU"
        verbose_name_plural = "SKUs"
        ordering = ['name'] # Order SKUs alphabetically by name by default

    def __str__(self):
        return f"{self.sku_id} - {self.name}"
    
    @staticmethod
    def get_high_return_rate():
        return 5.0

    @staticmethod
    def get_low_content_score():
        return 6.0


class Note(models.Model):
    """
    Represents a follow-up note associated with a specific SKU.
    """
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, related_name='notes', verbose_name="Associated SKU")
    text = models.TextField(verbose_name="Note Content")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='notes_created', 
        verbose_name="Created By"
    )

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ['-created_at'] # Order notes by most recent first

    def __str__(self):
        return f"Note for {self.sku.name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class SKUDailyMetric(models.Model):
    """
    Stores daily sales metrics for a specific SKU.
    """
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, related_name='daily_metrics', verbose_name="Associated SKU")
    date = models.DateField(verbose_name="Date of Metric")
    sales_units = models.IntegerField(default=0, verbose_name="Sales Units")
    returns_units = models.IntegerField(default=0, verbose_name="Returned Units")

    class Meta:
        verbose_name = "SKU Daily Metric"
        verbose_name_plural = "SKU Daily Metrics"
        unique_together = ('sku', 'date') # Ensure only one entry per SKU per day
        ordering = ['date'] # Order metrics by date

    def __str__(self):
        return f"Daily Sales for {self.sku.name} on {self.date}: {self.sales_units} units"


