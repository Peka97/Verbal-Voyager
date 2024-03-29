from django.shortcuts import render, HttpResponse

# Create your views here.


def user_auth(request):
    return HttpResponse('user_auth')


def user_sign_up(request):
    return HttpResponse('sign_up')


def user_profile(request):
    return HttpResponse('profile')


def user_logout(request):
    return HttpResponse('logout')
