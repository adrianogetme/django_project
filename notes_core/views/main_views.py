from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg
from ..models import Note
from ..forms import NoteForm, CommentForm

class HomeView(TemplateView):
    template_name = 'notes_core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_notes'] = Note.objects.filter(is_public=True).order_by('-created_at')[:5]
        return context

class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'notes_core/dashboard.html'
    context_object_name = 'notes'
    paginate_by = 10
    
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_notes'] = self.get_queryset().count()
        context['avg_rating'] = self.get_queryset().aggregate(avg=Avg('ratings__value'))['avg']
        return context

class NoteDetailView(DetailView):
    model = Note
    template_name = 'notes_core/note_detail.html'
    context_object_name = 'note'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all().order_by('-created_at')
        context['comment_form'] = CommentForm()
        if self.request.user.is_authenticated:
            context['user_rating'] = self.object.ratings.filter(user=self.request.user).first()
        return context

class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes_core/note_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _('Note created successfully!'))
        return super().form_valid(form) 