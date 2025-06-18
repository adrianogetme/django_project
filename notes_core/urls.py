from django.urls import path
from .views import admin_views
from .views.main_views import HomeView, DashboardView, NoteDetailView, NoteCreateView
from .views.user_views import ProfileView
from .views.note_views import (
    NoteUpdateView, NoteDeleteView, ReportNoteView, 
    RateNoteView, NotesByTagView, NoteDownloadView,
    AddCommentView
)

# Main URLs
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('notes/create/', NoteCreateView.as_view(), name='note_create'),
    path('notes/<int:pk>/', NoteDetailView.as_view(), name='note_detail'),
    path('notes/<int:pk>/edit/', NoteUpdateView.as_view(), name='note_edit'),
    path('notes/<int:pk>/delete/', NoteDeleteView.as_view(), name='note_delete'),
    path('notes/<int:pk>/report/', ReportNoteView.as_view(), name='note_report'),
    path('notes/<int:pk>/rate/', RateNoteView.as_view(), name='note_rate'),
    path('notes/<int:pk>/download/', NoteDownloadView.as_view(), name='note_download'),
    path('notes/<int:pk>/comment/', AddCommentView.as_view(), name='add_comment'),
    path('notes/tag/<str:tag_name>/', NotesByTagView.as_view(), name='notes_by_tag'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # Admin URLs
    path('admin/dashboard/', admin_views.AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # User Management
    path('admin/users/', admin_views.UserManagementView.as_view(), name='admin_users'),
    path('admin/users/<int:pk>/toggle/', admin_views.ToggleUserStatusView.as_view(), name='admin_toggle_user'),
    
    # Report Management
    path('admin/reports/', admin_views.ReportManagementView.as_view(), name='admin_reports'),
    path('admin/reports/<int:pk>/resolve/', admin_views.ResolveReportView.as_view(), name='admin_resolve_report'),
    
    # Audit Log
    path('admin/audit-log/', admin_views.AuditLogView.as_view(), name='admin_audit_log'),
    
    # Tag Suggestions (AJAX)
    path('admin/tags/suggest/', admin_views.TagSuggestionView.as_view(), name='admin_tag_suggest'),
] 