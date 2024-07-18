from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from dashboard.admin import custom_admin
from .analytics.fetch_analytics import fetch_week_data, fetch_monthly_data, fetch_top_media

class stats(LoginRequiredMixin, TemplateView):
    template_name = 'graphs/week_graph.html'
    login_url = '/login/'  # Optional: specify login URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(custom_admin.each_context(self.request))
        context['sidebar_closed'] = True
        week_data = fetch_week_data()
        year_data = fetch_monthly_data()
        context['week_data'] = week_data
        context['year_data'] = year_data
        return context

class top_media(LoginRequiredMixin, TemplateView):
    template_name = 'top_media.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context  = super().get_context_data(**kwargs)
        context.update(custom_admin.each_context(self.request))
        context['sidebar_closed'] = True
        data = fetch_top_media()
        context['top_movies'] = data["top_movies"]
        context['top_tv_shows'] = data["top_tv_shows"]
        return context