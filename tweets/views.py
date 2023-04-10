from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class HomeView(TemplateView, LoginRequiredMixin):
    template_name = "tweets/home.html"
