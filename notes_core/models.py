from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        VISITOR = 'VISITOR', _('Visitor')
        REGISTERED = 'REGISTERED', _('Registered')
        ADMINISTRATOR = 'ADMINISTRATOR', _('Administrator')

    role = models.CharField(
        max_length=13,
        choices=Role.choices,
        default=Role.VISITOR,
        verbose_name=_('Role')
    )
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_administrator(self):
        return self.role == self.Role.ADMINISTRATOR

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Name'))
    slug = models.SlugField(max_length=50, unique=True, verbose_name=_('Slug'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name']


class Note(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('Author')
    )
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    subject = models.CharField(max_length=100, verbose_name=_('Subject'))
    description = models.TextField(verbose_name=_('Description'))
    file = models.FileField(
        upload_to='notes/%Y/%m/%d/',
        verbose_name=_('File'),
        help_text=_('Upload PDF or image files')
    )
    is_public = models.BooleanField(default=True, verbose_name=_('Public'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    tags = models.ManyToManyField(Tag, related_name='notes', verbose_name=_('Tags'))
    download_count = models.PositiveIntegerField(default=0, verbose_name=_('Download Count'))

    def __str__(self):
        return f"{self.title} - {self.subject} ({self.user.username})"

    class Meta:
        verbose_name = _('Note')
        verbose_name_plural = _('Notes')
        ordering = ['-created_at']


class Comment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Author')
    )
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Note')
    )
    text = models.TextField(verbose_name=_('Comment text'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    def __str__(self):
        return f"Comment by {self.user.username} on {self.note.title}"

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ['-created_at']


class Rating(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_('User')
    )
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_('Note')
    )
    value = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Rating'),
        help_text=_('Rate from 1 to 5 stars')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    def __str__(self):
        return f"{self.note.title}: {self.value}★ by {self.user.username}"

    class Meta:
        verbose_name = _('Rating')
        verbose_name_plural = _('Ratings')
        unique_together = ['user', 'note']  # One rating per user per note
        ordering = ['-created_at']


class Report(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_('Reporter')
    )
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_('Reported Note')
    )
    reason = models.TextField(verbose_name=_('Reason'))
    resolved = models.BooleanField(default=False, verbose_name=_('Resolved'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Resolved at'))

    def __str__(self):
        return f"Report on {self.note.title} by {self.user.username}"

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        ordering = ['-created_at']


class AdminAction(models.Model):
    class ActionType(models.TextChoices):
        USER_BLOCK = 'USER_BLOCK', _('User Blocked')
        USER_UNBLOCK = 'USER_UNBLOCK', _('User Unblocked')
        NOTE_DELETE = 'NOTE_DELETE', _('Note Deleted')
        NOTE_APPROVE = 'NOTE_APPROVE', _('Note Approved')
        REPORT_RESOLVE = 'REPORT_RESOLVE', _('Report Resolved')

    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions', verbose_name=_('Admin'))
    action_type = models.CharField(max_length=20, choices=ActionType.choices, verbose_name=_('Action Type'))
    description = models.TextField(verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    def __str__(self):
        return f"{self.get_action_type_display()} by {self.admin.username}"

    class Meta:
        verbose_name = _('Admin Action')
        verbose_name_plural = _('Admin Actions')
        ordering = ['-created_at']
