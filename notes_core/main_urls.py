from django.urls import path
from django.contrib.auth import views as auth_views
from .views import note_views, user_views

urlpatterns = [
    # Home and Note Views
    path('', note_views.NoteListView.as_view(), name='home'),
    path('notes/create/', note_views.NoteCreateView.as_view(), name='note_create'),
    path('notes/<int:pk>/', note_views.NoteDetailView.as_view(), name='note_detail'),
    path('notes/<int:pk>/edit/', note_views.NoteUpdateView.as_view(), name='note_edit'),
    path('notes/<int:pk>/delete/', note_views.NoteDeleteView.as_view(), name='note_delete'),
    path('notes/<int:pk>/report/', note_views.ReportNoteView.as_view(), name='note_report'),
    path('notes/<int:pk>/rate/', note_views.RateNoteView.as_view(), name='note_rate'),
    
    # User Views
    path('dashboard/', user_views.DashboardView.as_view(), name='dashboard'),
    path('profile/', user_views.ProfileView.as_view(), name='profile'),
    path('register/', user_views.RegisterView.as_view(), name='register'),
    path('verify-email/<str:uidb64>/<str:token>/', user_views.VerifyEmailView.as_view(), name='verify_email'),
    
    # Authentication Views
    path('login/', auth_views.LoginView.as_view(template_name='notes_core/auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='notes_core/auth/password_reset.html',
        email_template_name='notes_core/emails/password_reset_email.html',
        subject_template_name='notes_core/emails/password_reset_subject.txt'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='notes_core/auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='notes_core/auth/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='notes_core/auth/password_reset_complete.html'
    ), name='password_reset_complete'),
] 