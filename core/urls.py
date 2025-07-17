from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('freelancer-dashboard/', views.freelancer_dashboard, name='freelancer_dashboard'),
    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),
    path('admin/disputes/', views.admin_disputes, name='admin_disputes'),
    path('admin-action/ban_user/', views.admin_ban_user, name='admin_ban_user'),
    path('admin-action/timeout_user/', views.admin_timeout_user, name='admin_timeout_user'),
    path('manage-users/', views.admin_manage_users, name='admin_manage_users'),
    path('admin-action/send_message/', views.admin_send_message, name='admin_send_message'),
    path('admin-action/unban_user/', views.admin_unban_user, name='admin_unban_user'),
    path('banned/', views.banned_info, name='banned_info'),
    path('admin-action/wallet_adjust/', views.admin_wallet_adjust, name='admin_wallet_adjust'),
    path('request-withdrawal/', views.request_withdrawal, name='request_withdrawal'),
] 