from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Count
from ..forms import ProfileForm
from ..models import User, Note

class DashboardView(TemplateView):
    template_name = 'notes_core/dashboard.html'

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'notes_core/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not kwargs.get('instance'):
            kwargs['instance'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's notes with aggregated data
        notes = Note.objects.filter(user=user)
        context.update({
            'total_notes': notes.count(),
            'public_notes': notes.filter(is_public=True).count(),
            'avg_rating': notes.aggregate(avg=Avg('ratings__value'))['avg'] or 0,
            'total_comments': notes.aggregate(total=Count('comments'))['total'] or 0,
            'recent_notes': notes.order_by('-created_at')[:5]
        })
        
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Profile updated successfully!'))
        return super().form_valid(form)

class RegisterView(TemplateView):
    template_name = 'notes_core/auth/register.html'

class VerifyEmailView(TemplateView):
    template_name = 'notes_core/auth/verify_email.html' 