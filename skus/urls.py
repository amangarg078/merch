from django.urls import path
from .views import SKUListAPIView, SKUDetailAPIView, NoteCreateAPIView, NoteRetrieveUpdateAPIView,\
    SKUDashboardView, SKUDetailView

urlpatterns = [
    # API URLs
    path('api/skus/', SKUListAPIView.as_view(), name='api_sku_list'),
    path('api/skus/<str:sku_id>/', SKUDetailAPIView.as_view(), name='api_sku_detail'),
    path('api/skus/<str:sku_id>/notes/', NoteCreateAPIView.as_view(), name='api_note_create'),
    path('api/notes/<str:pk>/', NoteRetrieveUpdateAPIView.as_view(), name='api_note_update'),
    
    path('', SKUDashboardView.as_view(), name='sku_list'),
    path('skus/<str:sku_id>/', SKUDetailView.as_view(), name='sku_detail'),
]