from django.views.generic import CreateView, DeleteView
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from ..models import Note, Comment, Rating, Report
from .base import RegisteredUserRequiredMixin, OwnerRequiredMixin


class CommentCreateView(RegisteredUserRequiredMixin, CreateView):
    """View for creating a comment on a note."""
    model = Comment
    fields = ['text']
    http_method_names = ['post']

    def form_valid(self, form):
        note = get_object_or_404(Note, pk=self.kwargs['pk'])
        form.instance.user = self.request.user
        form.instance.note = note
        response = super().form_valid(form)
        messages.success(self.request, _('Comment added successfully!'))
        return response

    def get_success_url(self):
        return reverse('note_detail', kwargs={'pk': self.kwargs['pk']})


class CommentDeleteView(OwnerRequiredMixin, DeleteView):
    """View for deleting a comment."""
    model = Comment
    http_method_names = ['post']

    def get_success_url(self):
        return reverse('note_detail', kwargs={'pk': self.object.note.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Comment deleted successfully!'))
        return super().delete(request, *args, **kwargs)


class RatingCreateUpdateView(RegisteredUserRequiredMixin, View):
    """View for creating or updating a rating."""
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        note = get_object_or_404(Note, pk=kwargs['pk'])
        value = request.POST.get('value')
        
        try:
            value = int(value)
            if not (1 <= value <= 5):
                raise ValueError
        except (TypeError, ValueError):
            return JsonResponse({'error': _('Invalid rating value')}, status=400)

        rating, created = Rating.objects.update_or_create(
            user=request.user,
            note=note,
            defaults={'value': value}
        )

        avg_rating = note.ratings.aggregate(Avg('value'))['value__avg']
        return JsonResponse({
            'message': _('Rating updated successfully!'),
            'avg_rating': round(avg_rating, 1) if avg_rating else 0
        })


class ReportCreateView(RegisteredUserRequiredMixin, CreateView):
    """View for creating a report on a note."""
    model = Report
    fields = ['reason']
    template_name = 'notes_core/report_form.html'

    def form_valid(self, form):
        note = get_object_or_404(Note, pk=self.kwargs['pk'])
        form.instance.user = self.request.user
        form.instance.note = note
        response = super().form_valid(form)
        messages.success(self.request, _('Report submitted successfully!'))
        return response

    def get_success_url(self):
        return reverse('note_detail', kwargs={'pk': self.kwargs['pk']}) 