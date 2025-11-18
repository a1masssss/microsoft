from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.views import View


class FrontendAppView(View):
    """Serve the compiled frontend entry point without using the template engine."""

    def _missing_frontend_response(self):
        message = (
            "Frontend build not found. Run `npm install` and `npm run build` in the frontend "
            "directory, then make sure `frontend/dist` is mounted into the backend container."
        )
        return HttpResponse(message, status=503, content_type="text/plain")

    def get(self, request, *args, **kwargs):
        index_path = settings.FRONTEND_INDEX_FILE
        if not index_path.exists():
            return self._missing_frontend_response()

        return FileResponse(open(index_path, "rb"), content_type="text/html")
