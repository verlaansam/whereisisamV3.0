from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from ckeditor_uploader import views as ckeditor_views

from core.ckeditor_views import upload as ckeditor_upload

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),   # 👈 API endpoints (DRF)
    path('api-auth/', include('rest_framework.urls')),  # browsable API login/logout
]

# CKEditor uploader URLs (handles /media/uploads/ file upload browsing and posting)
urlpatterns += [
    path('ckeditor/upload/', staff_member_required(ckeditor_upload), name='ckeditor_upload'),
    path('ckeditor/browse/', never_cache(staff_member_required(ckeditor_views.browse)), name='ckeditor_browse'),
]

# JWT auth (indien je simplejwt installeert)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns += [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
