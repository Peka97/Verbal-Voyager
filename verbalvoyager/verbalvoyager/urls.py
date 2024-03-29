from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls'), name='main'),
    path('users/', include('users.urls')),
    # path('calendar/', include('event_calendar.urls')),
    path('exercises/', include('exercises.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
