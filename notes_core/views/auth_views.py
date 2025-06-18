from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView
from django.contrib import messages

from ..forms import CustomAuthenticationForm, RegistrationForm
from ..models import User
from ..tokens import account_activation_token


class CustomLoginView(LoginView):
    """Custom login view with form."""
    form_class = CustomAuthenticationForm
    template_name = 'notes_core/auth/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        return super().form_valid(form)  # Remove email verification check for testing


class RegistrationView(CreateView):
    """Registration view with automatic login for testing."""
    form_class = RegistrationForm
    template_name = 'notes_core/auth/register.html'
    success_url = reverse_lazy('dashboard')  # Changed to redirect to dashboard

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True
        user.email_verified = True  # Automatically verify email for testing
        user.save()
        
        # Log in the user
        login(self.request, user)
        messages.success(self.request, _('Registration successful! Welcome to NoteShare.'))
        
        return super().form_valid(form)


class RegistrationDoneView(TemplateView):
    """Show registration completion message."""
    template_name = 'notes_core/auth/registration_done.html'


class ActivateAccountView(TemplateView):
    """Handle email verification."""
    template_name = 'notes_core/auth/activation_done.html'

    def get(self, request, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(kwargs['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, kwargs['token']):
            user.email_verified = True
            user.save()
            login(request, user)
            messages.success(request, _('Thank you for confirming your email. You can now access all features.'))
            return super().get(request, *args, **kwargs)
        else:
            messages.error(request, _('Activation link is invalid or has expired.'))
            return redirect('login') 