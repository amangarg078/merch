from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from .serializers import SKUListSerializer, NoteSerializer, SKUDetailsSerializer
from .models import SKU, Note


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 25


class SKUListAPIView(generics.ListAPIView):
    """
    API View to list all SKUs with pagination, search, and filtering.
    GET /api/skus/
    - Pagination: ?page=1&page_size=10
    - Search: ?search=<query> (searches by SKU name)
    - Filter by high return rate: ?high_return_rate=true (e.g., > 5%)
    - Filter by low content score: ?low_content_score=true (e.g., < 6.0)
    """
    serializer_class = SKUListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['name']
    ordering_fields = ['sales', 'return_percentage', 'content_score']
    
    def get_queryset(self):
        """
        Optionally restricts the returned SKUs by applying custom filters
        based on URL query parameters.
        """
        queryset = SKU.objects.all()
        
        # Filter for high return rate
        high_return_rate = self.request.query_params.get('high_return_rate', None)
        if high_return_rate and high_return_rate.lower() == 'true':
            # Define what 'high' means, e.g., > 5%
            queryset = queryset.filter(return_percentage__gt=SKU.get_high_return_rate())

        # Filter for low content score
        low_content_score = self.request.query_params.get('low_content_score', None)
        if low_content_score and low_content_score.lower() == 'true':
            # Define what 'low' means, e.g., < 6.0
            queryset = queryset.filter(content_score__lt=SKU.get_low_content_score())
            
        return queryset

class SKUDetailAPIView(generics.RetrieveAPIView):
    """
    API View to retrieve details of a single SKU.
    GET /api/skus/<sku_id>/
    """
    queryset = SKU.objects.all()
    serializer_class = SKUDetailsSerializer
    lookup_field = 'sku_id' # Use sku_id from the URL to lookup the SKU
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        """
        Passes the request object to the serializer context,
        which is needed by SKUSerializer.get_notes to check user groups.
        """
        return {'request': self.request}


class NoteCreateAPIView(generics.CreateAPIView):
    """
    API View to create a new note for a specific SKU.
    POST /api/skus/<sku_id>/notes/
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Overrides perform_create to associate the note with the correct SKU
        and set the created_by user based on the authenticated user.
        Also adds a permission check for the 'brand_user' group.
        """
        # Check if the authenticated user is in the 'brand_user' group
        if not self.request.user.groups.filter(name='brand_user').exists():
            raise PermissionDenied("You do not have permission to add notes.")

        sku_id = self.kwargs.get('sku_id')
        sku = get_object_or_404(SKU, sku_id=sku_id)
        # Set created_by to the current authenticated user
        serializer.save(sku=sku, created_by=self.request.user)

