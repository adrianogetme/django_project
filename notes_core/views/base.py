from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from ..models import User


class RegisteredUserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to require a registered user (not visitor) for a view."""
    
    def test_func(self):
        return self.request.user.role in [User.Role.REGISTERED, User.Role.ADMINISTRATOR]

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied(_("You must be a registered user to perform this action."))
        return super().handle_no_permission()


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to require administrator role for a view."""
    
    def test_func(self):
        return self.request.user.role == User.Role.ADMINISTRATOR

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied(_("You must be an administrator to access this page."))
        return super().handle_no_permission()


class OwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to require the user to be the owner of an object."""
    
    def test_func(self):
        obj = self.get_object()
        return (obj.user == self.request.user or 
                self.request.user.role == User.Role.ADMINISTRATOR) 