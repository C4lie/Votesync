from django.shortcuts import redirect
from functools import wraps

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.userprofile.role == required_role:
                return view_func(request, *args, **kwargs)
            return redirect('home')  # or render a 403 error page
        return _wrapped_view
    return decorator
