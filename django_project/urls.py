from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Changed to avoid conflict
]

# Add language prefix to all URLs
urlpatterns += i18n_patterns(
    path('', include('notes_core.urls')),  # All app URLs in one place
    prefix_default_language=False
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))] 