from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from pages.views import Handler403, Handler404, Handler500


handler403 = Handler403.as_view()
handler404 = Handler404.as_view()
handler500 = Handler500.as_view()

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),

    path('', include('pages.urls'), name='main'),
    path('users/', include('users.urls')),
    path('dictionary/', include('dictionary.urls')),
    path('exercises/', include('exercises.urls')),
    path('exercise_result/', include('exercise_result.urls')),
    path('event_calendar/', include('event_calendar.urls')),
    path('lesson_plan/', include('lesson_plan.urls')),
    path('constructor/', include('constructor.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns = [
        *urlpatterns,
        path("__debug__/", include("debug_toolbar.urls")),
        path('403', Handler403.as_view(), name='err_403'),
        path('404', Handler404.as_view(), name='err_404'),
        path('500', Handler500.as_view(), name='err_500'),
    ]

# if settings.admin_tools_enabled:
#     urlpatterns = [
#         *urlpatterns,
#         path('admin_tools/', include('admin_tools.urls'), name='admin'),
#     ]
