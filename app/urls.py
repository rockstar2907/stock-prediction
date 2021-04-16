from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('',views.index),
    path('login',views.login),
    path('signup',views.signup),
    path('logout',views.logout),
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name='reset_password.html'),name="reset_password"),
    path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(template_name='password_sent.html'),name="password_reset_done"),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='set_password.html'),name="password_reset_confirm"),
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_done.html'),name="password_reset_complete"),
]