from django.urls import path
from .views import CustomLoginView
from django.contrib.auth import logout
from django.shortcuts import redirect
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

def logout_view(request):
    logout(request)
    return redirect('core:home')

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('settings/', views.settings, name='settings'),
    path('switch-role/<str:role>/', views.switch_role, name='switch_role'),
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:user_id>/', views.conversation, name='conversation'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('test-messages/', views.test_messages, name='test_messages'),
    path('conversation-messages/', views.get_conversation_messages, name='conversation'),
    path('send-message/', views.send_message, name='send_message'),
]

# Add built-in password change view
urlpatterns += [
    path('change-password/', auth_views.PasswordChangeView.as_view(), name='change_password'),
    path('delete-account/', views.delete_account, name='delete_account'),
] 