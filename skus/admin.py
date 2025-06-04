from django.contrib import admin

# Register your models here.
from .models import SKU, Note, SKUDailyMetric


class SKUAdmin(admin.ModelAdmin):
    list_display = ('sku_id', 'name', 'sales', 'return_percentage', 'content_score')
    search_fields = ('sku_id', 'name')
    list_filter = ('return_percentage',)
    ordering = ('name',)


class NoteAdmin(admin.ModelAdmin):
    list_display = ('sku', 'created_at', 'created_by')
    search_fields = ('sku__name', 'text')
    list_filter = ('created_at', 'created_by')

class SKUDailyMetricAdmin(admin.ModelAdmin):
    list_display = ('sku', 'date', 'sales_units', 'returns_units')
    search_fields = ('sku__name',)
    list_filter = ('date',)


admin.site.register(SKU, SKUAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(SKUDailyMetric, SKUDailyMetricAdmin)
