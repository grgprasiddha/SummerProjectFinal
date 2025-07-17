from django.shortcuts import redirect
from django.urls import reverse

class BannedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow access to static, media, banned info, and logout URLs
        allowed_paths = [reverse('core:banned_info'), reverse('users:logout')]
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)
        if request.user.is_authenticated:
            if hasattr(request.user, 'profile') and getattr(request.user.profile, 'is_banned', False):
                if request.path not in allowed_paths:
                    return redirect('core:banned_info')
        return self.get_response(request) 