from django.urls import path
from .views import SKUListAPIView, SKUDetailAPIView, NoteCreateAPIView

urlpatterns = [
    # API URLs
    path('api/skus/', SKUListAPIView.as_view(), name='api_sku_list'), # API to list all SKUs
    path('api/skus/<str:sku_id>/', SKUDetailAPIView.as_view(), name='api_sku_detail'), # API to get SKU details
    path('api/skus/<str:sku_id>/notes/', NoteCreateAPIView.as_view(), name='api_note_create'), # API to add notes
]