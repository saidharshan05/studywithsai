from django.contrib import admin
from django.urls import path, include 
from django.contrib.auth import views as auth_views
from django.conf import settings # <-- ADD THIS IMPORT
from django.conf.urls.static import static
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include authentication URLs
    #path('account/', include('django.contrib.auth.urls')),
    path('account/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # 🛑 FINAL FIX: Use absolute path for template_name
    path('account/logout/', 
         auth_views.LogoutView.as_view(
             template_name=os.path.join(settings.BASE_DIR, 'templates', 'registration', 'logout.html')
         ), 
         name='logout'),
    path('', include('store.urls')),
    path('account/', include('django.contrib.auth.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)