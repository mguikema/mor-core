from django.conf import settings


def general_settings(context):
    return {
        "GIT_SHA": settings.GIT_SHA,
    }
