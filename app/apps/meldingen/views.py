from apps.auth.authentication import AuthenticationClass
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden


def serve_protected_media(request):
    user = AuthenticationClass().authenticate(request)
    if user or settings.ALLOW_UNAUTHORIZED_MEDIA_ACCESS:
        url = request.path.replace("media", "media-protected")
        response = HttpResponse("")
        response["X-Accel-Redirect"] = url
        response["Content-Type"] = ""
        return response
    return HttpResponseForbidden()
