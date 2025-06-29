from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from pages.views import handler_403, handler_404, handler_500


handler403 = handler_403
handler404 = handler_404
handler500 = handler_500

urlpatterns = [
    path('auth', views.user_auth, name='auth'),
    path('register', views.user_register, name='register'),
    # path('account/json/update/timezone', views.json_update_timezone, name='update_timezone'),
    path('account', views.user_account, name='account'),
    path('logout', views.user_logout, name='logout'),

    path(
        'reset_password/',
        views.CustomPasswordResetView.as_view(),
        name='reset_password'
    ),
    path(
        'password_reset_done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'password_reset_complete/',
        views.CustomPasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),
]
