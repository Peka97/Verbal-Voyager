from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path('auth', views.user_auth, name='auth'),
    path('sign_up', views.user_sign_up, name='sign_up'),
    path('profile', views.user_profile, name='profile'),
    path('logout', views.user_logout, name='logout'),

    # path(
    #     'reset_password/',
    #     auth_views.PasswordResetView.as_view(),
    #     name='reset_password'
    # ),
    # path(
    #     'password_reset_done/',
    #     auth_views.PasswordResetDoneView.as_view(),
    #     name='password_reset_done'
    # ),
    # path(
    #     'reset/<uidb64>/<token>',
    #     auth_views.PasswordResetConfirmView.as_view(),
    #     name='password_reset_confirm'
    # ),
    # path(
    #     'password_reset_complete/',
    #     views.CustomPasswordResetCompleteView.as_view(),
    #     name='password_reset_complete'
    # ),
]
