from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, RedirectView

from tweets.models import Tweet

from .forms import SignUpForm
from .models import FollowUser, User


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
        self.user = user
        return Tweet.objects.select_related("user").filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mytweet"] = Tweet.objects.select_related("self.user").filter(user=self.user)
        context["is_following"] = FollowUser.objects.filter(follower=self.request.user, following=self.user)
        context["following_count"] = FollowUser.objects.filter(follower=self.user).count()
        context["follower_count"] = FollowUser.objects.filter(following=self.user).count()


class FollowView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy("tweets:home")

    def post(self, request, *args, **kwargs):
        target_user = get_object_or_404(User, username=self.kwargs["username"])
        if target_user == self.request.user:
            messages.add_message(request, messages.ERROR, "自分自身をフォローすることはできません。")
            return HttpResponseBadRequest("you cannnot follow yourself.")
        if self.request.user.following.filter(following__username=target_user.username).exists():
            messages.add_message(request, messages.INFO, "既にフォローしています。")
        else:
            FollowUser.objects.create(follower=request.user, following=target_user)
            messages.add_message(request, messages.SUCCESS, "フォローしました。")
        return super().post(request, *args, **kwargs)


class UnFollowView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy("tweets:home")

    def post(self, request, *args, **kwargs):
        target_user = get_object_or_404(User, username=self.kwargs["username"])
        if target_user == self.request.user:
            messages.add_message(request, messages.ERROR, "自分自身はフォローできません")
            return HttpResponseBadRequest("you cannnot unfollow yourself.")
        if FollowUser.objects.filter(following=target_user).filter(follower=self.request.user).exists():
            target_follower = get_object_or_404(FollowUser, following=target_user, follower=self.request.user)
            target_follower.delete()
            messages.add_message(request, messages.SUCCESS, "フォロー解除しました。")
        else:
            messages.add_message(request, messages.INFO, "フォローしていないユーザーです")
        return super().post(request, *args, **kwargs)


class FollowingListView(LoginRequiredMixin, ListView):
    template_name = "accounts/followingList.html"
    context_object_name = "following_list"

    def get_queryset(self):
        target_user = get_object_or_404(
            User,
            username=self.kwargs.get("username"),
        )
        return target_user.follower.select_related("following").order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = get_object_or_404(
            User,
            username=self.kwargs["username"],
        )
        return context


class FollowerListView(LoginRequiredMixin, ListView):
    template_name = "accounts/followerList.html"
    context_object_name = "follower_list"

    def get_queryset(self):
        target_user = get_object_or_404(
            User,
            username=self.kwargs.get("username"),
        )
        return target_user.following.select_related("follower").order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = get_object_or_404(
            User,
            username=self.kwargs["username"],
        )
        return context
