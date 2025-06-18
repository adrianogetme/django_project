from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Note, Tag, Comment, Rating, Report


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Role'), {'fields': ('role',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'user', 'created_at')
    list_filter = ('subject', 'created_at', 'tags')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'created_at'
    filter_horizontal = ('tags',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'note', 'created_at', 'short_text')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__username', 'note__title')
    date_hierarchy = 'created_at'

    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = _('Comment preview')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('note', 'user', 'value', 'created_at')
    list_filter = ('value', 'created_at')
    search_fields = ('user__username', 'note__title')
    date_hierarchy = 'created_at'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('note', 'user', 'short_reason', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('reason', 'user__username', 'note__title')
    date_hierarchy = 'created_at'

    def short_reason(self, obj):
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    short_reason.short_description = _('Reason preview')
