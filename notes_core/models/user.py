from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model with role-based permissions."""
    
    class Role(models.TextChoices):
        VISITOR = 'VISITOR', _('Visitor')
        REGISTERED = 'REGISTERED', _('Registered User')
        ADMINISTRATOR = 'ADMINISTRATOR', _('Administrator')

    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VISITOR,
        verbose_name=_('role')
    )
    email_verified = models.BooleanField(
        default=False,
        verbose_name=_('email verified')
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_visitor(self):
        return self.role == self.Role.VISITOR

    @property
    def is_registered(self):
        return self.role == self.Role.REGISTERED

    @property
    def is_administrator(self):
        return self.role == self.Role.ADMINISTRATOR

    def save(self, *args, **kwargs):
        # Ensure administrators are staff and superusers
        if self.role == self.Role.ADMINISTRATOR:
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs) 