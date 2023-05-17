from rest_framework import permissions


class IsRecipeAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.author == request.user
        return True
