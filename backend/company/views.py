from django.views.generic import DetailView
from django.http import FileResponse

from .models import StableDocument

class StableDocumentDetailView(DetailView):
    model = StableDocument

    def render_to_response(self, context, **kwargs):
        file_object = self.object
        return FileResponse(
            file_object.file,
            filename=file_object.file_name + file_object.extension()
        )
