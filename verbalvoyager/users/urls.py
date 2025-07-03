from django.contrib.auth import views as auth_views
from django.urls import path

from pages.views import handler_403, handler_404, handler_500

# , UserRegisterView, UserAccountView, UserLogoutView, CustomPasswordResetView, CustomPasswordResetCompleteView
from .views import (
    CustomPasswordResetCompleteView,
    CustomPasswordResetView,
    SetUserTimezoneView,
    UserAccountView,
    UserAuthRegisterView,
    UserLogoutView,
)


handler403 = handler_403
handler404 = handler_404
handler500 = handler_500

urlpatterns = [
    path('auth/', UserAuthRegisterView.as_view(), name='auth'),
    path('account/', UserAccountView.as_view(), name='account'),
    path('account/timezone/update/', SetUserTimezoneView.as_view(),
         name='account_timezone_update'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    path(
        'reset_password/',
        CustomPasswordResetView.as_view(),
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
        CustomPasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),
]
