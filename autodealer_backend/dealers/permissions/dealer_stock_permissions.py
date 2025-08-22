from rest_framework import permissions


class IsDealerStockOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.dealer.user == request.user
