from django.contrib import admin
from django.urls import path, include
from users.views import LoginView
from django.urls import path, include
# 👇 add these
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", LoginView.as_view(), name="api-login"),
    
    path("api/", include("users.urls")),
    
    path('api/users/', include('users.urls')),
    
     
]   

# 👇 serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
