from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse, FileResponse
from django.utils import timezone
from ..models import Note, Report, Rating, Tag, Comment
from ..forms import NoteForm, ReportForm, RatingForm, CommentForm
from ..mixins import RegisteredUserRequiredMixin

class NoteListView(ListView):
    model = Note
    template_name = 'notes_core/note_list.html'
    context_object_name = 'notes'
    paginate_by = 10

    def get_queryset(self):
        queryset = Note.objects.filter(is_public=True).order_by('-created_at')
        return queryset

class NoteDetailView(DetailView):
    model = Note
    template_name = 'notes_core/note_detail.html'
    context_object_name = 'note'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get comments
        context['comments'] = self.object.comments.all().order_by('-created_at')
        
        # Get rating information
        if self.request.user.is_authenticated:
            context['user_rating'] = self.object.ratings.filter(user=self.request.user).first()
            context['comment_form'] = CommentForm()
            context['report_form'] = ReportForm()
        
        # Calculate average rating
        ratings = self.object.ratings.all()
        if ratings.exists():
            context['avg_rating'] = sum(r.value for r in ratings) / ratings.count()
            context['total_ratings'] = ratings.count()
        else:
            context['avg_rating'] = 0
            context['total_ratings'] = 0
            
        return context

class NoteCreateView(RegisteredUserRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes_core/note_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _('Note created successfully!'))
        return super().form_valid(form)

class NoteUpdateView(RegisteredUserRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes_core/note_form.html'
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, _('Note updated successfully!'))
        return super().form_valid(form)

class NoteDeleteView(RegisteredUserRequiredMixin, DeleteView):
    model = Note
    template_name = 'notes_core/note_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Note deleted successfully!'))
        return super().delete(request, *args, **kwargs)

class ReportNoteView(RegisteredUserRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'notes_core/note_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['note'] = get_object_or_404(Note, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        note = get_object_or_404(Note, pk=self.kwargs['pk'])
        form.instance.user = self.request.user
        form.instance.note = note
        response = super().form_valid(form)
        messages.success(self.request, _('Report submitted successfully!'))
        return response

    def get_success_url(self):
        return reverse_lazy('note_detail', kwargs={'pk': self.kwargs['pk']})

class RateNoteView(LoginRequiredMixin, View):
    """View for handling note ratings."""
    
    def post(self, request, pk):
        note = get_object_or_404(Note, pk=pk)
        rating_value = request.POST.get('rating')
        
        if not rating_value or not rating_value.isdigit() or not (1 <= int(rating_value) <= 5):
            messages.error(request, _('Please provide a valid rating between 1 and 5.'))
            return redirect('note_detail', pk=pk)
        
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            note=note,
            defaults={'value': rating_value}
        )
        
        messages.success(request, _('Rating updated successfully!'))
        return redirect('note_detail', pk=pk)

    def get(self, request, pk):
        return redirect('note_detail', pk=pk)

class NotesByTagView(ListView):
    model = Note
    template_name = 'notes_core/note_list.html'
    context_object_name = 'notes'
    paginate_by = 10

    def get_queryset(self):
        tag_name = self.kwargs.get('tag_name')
        tag = get_object_or_404(Tag, name=tag_name)
        return Note.objects.filter(tags=tag, is_public=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_name'] = self.kwargs.get('tag_name')
        return context

class NoteDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        note = get_object_or_404(Note, pk=pk)
        # Increment download count
        note.download_count = note.download_count + 1 if hasattr(note, 'download_count') else 1
        note.save(update_fields=['download_count'])
        
        response = FileResponse(note.file, as_attachment=True)
        return response

class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    http_method_names = ['post']

    def form_valid(self, form):
        note = get_object_or_404(Note, pk=self.kwargs['pk'])
        form.instance.user = self.request.user
        form.instance.note = note
        response = super().form_valid(form)
        messages.success(self.request, _('Comment added successfully!'))
        return response

    def form_invalid(self, form):
        messages.error(self.request, _('Error adding comment. Please try again.'))
        return redirect('note_detail', pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('note_detail', kwargs={'pk': self.kwargs['pk']}) 