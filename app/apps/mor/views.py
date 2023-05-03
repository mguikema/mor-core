from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework.authentication import TokenAuthentication


def serve_media(request):
    user = TokenAuthentication().authenticate(request)
    if user or settings.ALLOW_UNAUTHORIZED_MEDIA_ACCESS:
        url = request.path.replace("media", "media-protected")
        response = HttpResponse("")
        response["X-Accel-Redirect"] = url
        response["Content-Type"] = ""
        return response
    return HttpResponseForbidden()
