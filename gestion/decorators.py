from django.shortcuts import redirect
from functools import wraps

def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'role') and request.user.role == role:
                return view_func(request, *args, **kwargs)
            return redirect('login')  # ou une autre page d'erreur/accès refusé
        return _wrapped_view
    return decorator
