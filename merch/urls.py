"""
URL configuration for merch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView # Import RedirectView
from django.contrib.auth import views as auth_views # Import auth views
from skus.views import SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('skus.urls')),

    # Django Auth URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),

    # Redirect root URL to SKU list if logged in, or login page if not
    # This will be handled by LoginRequiredMixin on SKUListView
    # path('', RedirectView.as_view(pattern_name='sku_list'), name='home'),
]