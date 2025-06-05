from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework import filters
import json
from .serializers import SKUListSerializer, NoteSerializer, SKUDetailsSerializer
from .models import SKU, Note


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login') # Redirect to login after successful signup
    template_name = 'registration/signup.html'


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
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    search_fields = ['name']
    ordering_fields = ['name', 'sales', 'return_percentage', 'content_score']
    
    def get_queryset(self):
        """
        Optionally restricts the returned SKUs by applying custom filters
        based on URL query parameters.
        """
        queryset = SKU.objects.all()

        filter_type = self.request.query_params.get('filter_type', None)
        if filter_type:
            if filter_type.lower() == 'high_return_rate':
                # Filter for high return rate
                queryset = queryset.filter(return_percentage__gt=SKU.get_high_return_rate())
            elif filter_type.lower() == 'low_content_score':
                # Filter for low content score
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
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    
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
    authentication_classes = [TokenAuthentication, SessionAuthentication]

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


class NoteRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    API View to retrieve or update a specific note.
    GET /api/notes/<int:pk>/
    PATCH /api/notes/<int:pk>/
    PUT /api/notes/<int:pk>/
    Users can only retrieve/update notes they created and must be in 'brand_user' group.
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get_queryset(self):
        """
        Ensures a user can only retrieve/update notes they created
        and are in the 'brand_user' group.
        """
        user = self.request.user
        if user.is_authenticated and user.groups.filter(name='brand_user').exists():
            return self.queryset.filter(created_by=user)
        return self.queryset.none() # Return empty queryset if not authorized

    def perform_update(self, serializer):
        """
        Ensures the note is updated by the correct user.
        """
        # The get_queryset already filters by created_by=user,
        # so we just need to save.
        serializer.save()


class SKUDashboardView(TemplateView):
    """
    Dashboard view to list all SKUs.
    """
    template_name = 'home.html'


class SKUDetailView(LoginRequiredMixin, TemplateView):
    """
    Detail view for a specific SKU.
    """
    template_name = 'sku_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["skuId"] = self.kwargs.get('sku_id')
        context["can_add_note"] = json.dumps(self.request.user.groups.filter(name='brand_user').exists())
        context["is_merch_ops"] = json.dumps(self.request.user.groups.filter(name='merch_ops').exists())
        return context

