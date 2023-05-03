from django.http import HttpResponse


def serve_media(request):
    request.path.replace("media", "protected")
    print(request.path)
    response = HttpResponse("")
    # response['X-Accel-Redirect'] = url
    response["X-Accel-Redirect"] = request.path
    response["Content-Type"] = ""
    return response
