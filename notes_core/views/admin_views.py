from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db.models import Count, Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    ListView, DetailView, UpdateView, DeleteView, TemplateView
)

from ..mixins import AdminRequiredMixin
from ..models import User, Note, Report, AdminAction, Tag


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """Admin dashboard showing system statistics and recent activity."""
    template_name = 'notes_core/admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # System statistics
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        context['total_notes'] = Note.objects.count()
        context['pending_reports'] = Report.objects.filter(resolved=False).count()
        
        # Recent reports
        context['reports'] = Report.objects.select_related(
            'user', 'note'
        ).order_by('-created_at')[:5]
        
        # Recent users
        context['recent_users'] = User.objects.order_by('-date_joined')[:5]
        
        # Activity statistics for chart
        context['chart_data'] = self.get_chart_data()
        
        return context

    def get_chart_data(self):
        """Get data for the activity chart."""
        # Implementation for chart data...
        return {
            'labels': ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'],
            'new_users': [3, 7, 5, 9, 6],
            'new_notes': [5, 12, 8, 15, 10]
        }


class UserManagementView(AdminRequiredMixin, ListView):
    """List and manage users."""
    model = User
    template_name = 'notes_core/admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        role = self.request.GET.get('role', '')
        
        if search:
            queryset = queryset.filter(username__icontains=search)
        if role:
            queryset = queryset.filter(role=role)
            
        return queryset.annotate(
            notes_count=Count('notes'),
            avg_rating=Avg('notes__ratings__value')
        )


class ToggleUserStatusView(AdminRequiredMixin, UpdateView):
    """Toggle user active status (block/unblock)."""
    model = User
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()

        # Create audit log
        AdminAction.objects.create(
            admin=request.user,
            action_type=AdminAction.ActionType.USER_BLOCK if not user.is_active 
                       else AdminAction.ActionType.USER_UNBLOCK,
            content_type=ContentType.objects.get_for_model(user),
            object_id=user.id,
            description=f"{'Blocked' if not user.is_active else 'Unblocked'} user: {user.username}"
        )

        # Send email notification
        if not user.is_active:
            send_mail(
                _('Your NoteShare Account Has Been Suspended'),
                render_to_string('notes_core/emails/account_suspended.html', {
                    'user': user
                }),
                None,
                [user.email],
                fail_silently=True
            )

        messages.success(
            request,
            _('User has been {status}').format(
                status=_('blocked') if not user.is_active else _('unblocked')
            )
        )
        return JsonResponse({'status': 'success'})


class ReportManagementView(AdminRequiredMixin, ListView):
    """List and manage reports."""
    model = Report
    template_name = 'notes_core/admin/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user', 'note')
        status = self.request.GET.get('status')
        
        if status == 'pending':
            queryset = queryset.filter(resolved=False)
        elif status == 'resolved':
            queryset = queryset.filter(resolved=True)
            
        return queryset.order_by('-created_at')


class ResolveReportView(AdminRequiredMixin, UpdateView):
    """Resolve a report and optionally delete the reported note."""
    model = Report
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        report = self.get_object()
        action = request.POST.get('action')
        
        if action == 'delete_note':
            note = report.note
            note.delete()
            
            # Create audit log
            AdminAction.objects.create(
                admin=request.user,
                action_type=AdminAction.ActionType.NOTE_DELETE,
                content_type=ContentType.objects.get_for_model(note),
                object_id=note.id,
                description=f"Deleted note: {note.title} due to report"
            )
            
            # Notify user
            send_mail(
                _('Your Note Has Been Removed'),
                render_to_string('notes_core/emails/note_removed.html', {
                    'note': note,
                    'user': note.user
                }),
                None,
                [note.user.email],
                fail_silently=True
            )

        report.resolved = True
        report.save()
        
        # Create audit log
        AdminAction.objects.create(
            admin=request.user,
            action_type=AdminAction.ActionType.REPORT_RESOLVE,
            content_type=ContentType.objects.get_for_model(report),
            object_id=report.id,
            description=f"Resolved report on note: {report.note.title}"
        )

        messages.success(request, _('Report has been resolved'))
        return JsonResponse({'status': 'success'})


class AuditLogView(AdminRequiredMixin, ListView):
    """View admin action audit logs."""
    model = AdminAction
    template_name = 'notes_core/admin/audit_log.html'
    context_object_name = 'actions'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related('admin')
        action_type = self.request.GET.get('action_type')
        
        if action_type:
            queryset = queryset.filter(action_type=action_type)
            
        return queryset.order_by('-created_at')


class TagSuggestionView(AdminRequiredMixin, ListView):
    """AJAX view for tag suggestions."""
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        if not query:
            return JsonResponse({'results': []})
            
        tags = Tag.objects.filter(name__icontains=query)[:10].values('id', 'name')
        return JsonResponse({
            'results': [{'id': tag['id'], 'text': tag['name']} for tag in tags]
        })


class UserManagementView(TemplateView):
    template_name = 'notes_core/admin/user_list.html'


class ToggleUserStatusView(TemplateView):
    template_name = 'notes_core/admin/user_toggle.html'


class ReportManagementView(TemplateView):
    template_name = 'notes_core/admin/report_list.html'


class ResolveReportView(TemplateView):
    template_name = 'notes_core/admin/report_resolve.html'


class AuditLogView(TemplateView):
    template_name = 'notes_core/admin/audit_log.html'


class TagSuggestionView(TemplateView):
    template_name = 'notes_core/admin/tag_suggest.html' 