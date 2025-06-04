import datetime
from collections import defaultdict
from rest_framework import serializers
from .models import SKU, Note, SKUDailyMetric

class NoteSerializer(serializers.ModelSerializer):
    """
    Serializer for the Note model.
    Used for displaying and creating notes via the API.
    """
    created_by_username = serializers.SerializerMethodField() # New field to display username

    class Meta:
        model = Note
        fields = ['id', 'sku', 'text', 'created_at', 'created_by_username']
        read_only_fields = ['id', 'sku', 'created_at', 'created_by', 'created_by_username'] # created_at and created_by are set automatically

    def get_created_by_username(self, obj):
        """
        Returns the username of the user who created the note.
        """
        return obj.created_by.username if obj.created_by else 'Anonymous'

class SKUDailyMetricSerializer(serializers.ModelSerializer):
    """
    Serializer for the SKUDailyMetric model.
    """
    class Meta:
        model = SKUDailyMetric
        fields = ['date', 'sales_units']


class SKUDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for the SKU model.
    Includes nested notes and daily metrics for the detail view.
    """
    notes = serializers.SerializerMethodField()
    daily_metrics = serializers.SerializerMethodField()

    
    def get_notes(self, obj):
        """
        Conditionally returns notes based on user's permissions.
        Only users in the 'merch_ops' group can see all notes.
        Other authenticated users will see an empty list.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.groups.filter(name='merch_ops').exists():
                # If user is in 'merch_ops' group, return all notes
                return NoteSerializer(obj.notes.all(), many=True, context={'request': request}).data
            
            if request.user.groups.filter(name='brand_user').exists():
                return NoteSerializer(obj.notes.filter(created_by=request.user), many=True, context={'request': request}).data
        else:
            # Otherwise, return an empty list
            return []
    
    def get_daily_metrics(self, obj):
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=7)

        daily_metrics_queryset = obj.daily_metrics.filter(date__gte=start_date).order_by('date')
        # Fetch existing daily metrics within the calculated time range
        daily_metrics_queryset = obj.daily_metrics.filter(date__gte=start_date, date__lte=today).order_by('date')
        
        # Create a dictionary for quick lookup of existing data
        existing_data = {metric.date: metric.sales_units for metric in daily_metrics_queryset}

        # Generate a complete list of dates for the period
        all_dates_in_period = []
        current_date = start_date
        while current_date <= today:
            all_dates_in_period.append(current_date)
            current_date += datetime.timedelta(days=1)
        
        # Build the final list with null for missing entries
        formatted_metrics = []
        for d in all_dates_in_period:
            sales_units = existing_data.get(d, 0) # Use 0 for missing entries
            formatted_metrics.append({
                'date': d.isoformat(), # Format date as ISO string
                'sales_units': sales_units
            })
        
        return formatted_metrics


    class Meta:
        model = SKU
        fields = ['id', 'sku_id', 'name', 'sales', 'return_percentage', 'content_score', 'notes', 'daily_metrics']


class SKUListSerializer(serializers.ModelSerializer):
    """
    Serializer for the SKU model.
    """
    class Meta:
        model = SKU
        fields = ['sku_id', 'name', 'sales', 'return_percentage', 'content_score']
