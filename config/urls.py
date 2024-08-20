"""
URL configuration for autosubmit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.urls import api_url
from apps.user.urls import urlpatterns as user_urls
from apps.payment.urls import urlpatterns as payment_urls
from apps.setup.urls import urlpatterns as setup_urls
from apps.job_applying.urls import urlpatterns as job_applying_urls
from config.yasg_config import schema_view

urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('google', TemplateView.as_view(template_name="index.html")),
    path('admin/', admin.site.urls),
    api_url('user/', include(user_urls)),
    api_url('payment/', include(payment_urls)),
    api_url('setup/', include(setup_urls)),
    api_url('job-apply/', include(job_applying_urls)),
    api_url('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    api_url('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
