from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from properties.models import Property
from .models import Feed


class FeedDetailView(DetailView):
    content_type = "application/xml"
    context_object_name = "feed"

    def get_queryset(self):
        return Feed.objects.filter_active()

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug', '')
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.get(slug=slug)
        except Feed.DoesNotExist:
            raise Http404("Фид с указанным slug не найден")

    def get_template_names(self):
        template_type = self.kwargs.get('template_slug', '')
        feed = self.get_object()
        template_name = f"feed/{template_type}/{feed.property_type}.xml"
        return template_name

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_list"] = Property.objects.filter_feed(feed=self.get_object()).annotate_feed()
        return ctx
