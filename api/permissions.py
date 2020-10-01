from rest_framework import permissions
from rest_framework import exceptions
from .models import User, Club


class IsValidEmail(permissions.DjangoModelPermissions):
    def has_permission(self, request, view):
        if not User.objects.filter(email__iexact=request.data.get('email', None)).count():
            raise exceptions.APIException('Invalid email')
        return True


class IsValidTitle(permissions.DjangoModelPermissions):
    def has_permission(self, request, view):
        if not Club.objects.filter(title__iexact=request.data.get('title', None)).count():
            raise exceptions.APIException('Invalid title')
        return True


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.email == request.user.email


class IsClubOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.head_of_the_club.email == request.user.email


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.status == 2
