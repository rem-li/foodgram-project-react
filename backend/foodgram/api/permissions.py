from rest_framework import permissions

class IsRecipeAuthor(permissions.BasePermission):
    """
    Object-level permission to only allow authors of an recipe to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `author`.
        return obj.author == request.user
