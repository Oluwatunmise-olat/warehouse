from rest_framework import permissions
from django.contrib.auth import get_user_model

USER = get_user_model()

class IsPermitted(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated & 
            (request.user.is_admin | request.user.is_worker))

