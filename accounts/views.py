from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from tweets.models import Tweet

from .forms import SignUpForm
from .models import User


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"


class LogoutView(auth_views.LogoutView):
    pass


class UserProfileView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "accounts/profile.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "tweets"

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return Tweet.objects.select_related("user").filter(user=user)
