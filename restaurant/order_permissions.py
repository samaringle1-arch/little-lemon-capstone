
from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated
            and (
                user.is_staff
                or user.groups.filter(name="Manager").exists()
            )
        )


class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated
            and user.groups.filter(name="Delivery Crew").exists()
        )
