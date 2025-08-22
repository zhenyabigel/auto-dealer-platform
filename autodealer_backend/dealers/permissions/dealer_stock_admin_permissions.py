from rest_framework import permissions


class IsAdminOrDealerStockOwner(permissions.BasePermission):
    """
    Custom permission to allow access if the user is either:
    - An admin (is_staff=True)
    - The owner of the dealer profile associated with the stock item
    """

    def has_permission(self, request, view):
        if view.action == "create":
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.dealer.user == request.user
