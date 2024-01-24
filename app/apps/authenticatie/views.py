import logging
from urllib import parse

import requests
from apps.authenticatie.serializers import GebruikerSerializer
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


def provider_logout(request):
    logout_url = settings.OIDC_OP_LOGOUT_ENDPOINT
    oidc_id_token = request.session.get("oidc_id_token", None)
    redirect_url = request.build_absolute_uri(
        location=request.GET.get("next", settings.LOGOUT_REDIRECT_URL)
    )
    if oidc_id_token:
        logout_url = (
            settings.OIDC_OP_LOGOUT_ENDPOINT
            + "?"
            + parse.urlencode(
                {
                    "id_token_hint": oidc_id_token,
                    "post_logout_redirect_uri": redirect_url,
                }
            )
        )
    logout_response = requests.get(logout_url)
    if logout_response.status_code != 200:
        logger.error(
            f"provider_logout: status code: {logout_response.status_code}, logout_url: {logout_url}"
        )
    return redirect_url


class GetGebruikerAPIView(APIView):
    serializer_class = GebruikerSerializer

    def get(self, request, email=None):
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {"email": "is not a valid email address"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        get_gebruiker = cache.get(f"gebruiker_{email}", {})
        get_gebruiker.update({"email": email})
        get_gebruiker_serializer = GebruikerSerializer(data=get_gebruiker)
        if get_gebruiker_serializer.is_valid():
            logger.info(
                f"Get gebruiker info: email={email}, data={get_gebruiker_serializer.validated_data}"
            )
            return Response(
                get_gebruiker_serializer.validated_data, status=status.HTTP_200_OK
            )
        return Response(
            get_gebruiker_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class SetGebruikerAPIView(APIView):
    serializer_class = GebruikerSerializer

    def post(self, request):
        serializer = GebruikerSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            logger.info(f"Set gebruiker info: data={serializer.validated_data}")
            cache.set(
                f"gebruiker_{serializer.data.get('email')}", serializer.validated_data
            )
            return Response({}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
