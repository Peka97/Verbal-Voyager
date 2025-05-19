from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from pages.views import handler_403, handler_404, handler_500

# TODO: rename handler_\d+ to error_\d+_view
handler403 = handler_403
handler404 = handler_404
handler500 = handler_500

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),

    path('', include('pages.urls'), name='main'),
    path('users/', include('users.urls')),
    path('dictionary/', include('dictionary.urls')),
    path('exercises/', include('exercises.urls')),
    path('exercise_result/', include('exercise_result.urls')),
    path('event_calendar/', include('event_calendar.urls')),
    path('lesson_plan/', include('lesson_plan.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns = [
        *urlpatterns,
        path("__debug__/", include("debug_toolbar.urls")),
    ]

# if settings.admin_tools_enabled:
#     urlpatterns = [
#         *urlpatterns,
#         path('admin_tools/', include('admin_tools.urls'), name='admin'),
#     ]
