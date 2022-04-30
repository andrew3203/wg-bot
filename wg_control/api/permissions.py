from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticatedOrReadOnly, IsAuthenticated


class IsNotAuthenticated(BasePermission):

    def has_permission(self, request, view):
        if request.method== 'POST':
            try:
                user = request.user
            except:
                return True
            
            return not user.is_authenticated
        else:
            return True


class IsClientOwnerOrReadOnly(IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj == request.user


class IsUsertOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.client.id == request.user.id


class IsReferralOwnerOrReadOnly(IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        return obj.owner.client.id == request.user.id


class IsOrderOwner(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        return obj.user.client.id == request.user.id


class ReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
