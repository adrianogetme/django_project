from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Changed to avoid conflict
    path('', include('notes_core.urls')),  # All app URLs in one place
    path('i18n/', include('django.conf.urls.i18n')),  # For language switching
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))] 