from rest_framework import generics, mixins
from django.shortcuts import render
from urllib.parse import urlencode

from allauth.socialaccount.providers.microsoft.views import MicrosoftGraphOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.serializers import SocialLoginSerializer
from allauth.account.adapter import get_adapter
from rest_auth.views import LoginView
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from .models import UserModel
from InnoClubs import settings


class SocialLoginView(LoginView):
    serializer_class = SocialLoginSerializer

    def process_login(self):
        get_adapter(self.request).login(self.request, self.user)


class OutlookLogin(SocialLoginView):
    adapter_class = MicrosoftGraphOAuth2Adapter

    # if socket.gethostname() != 'khron':
    callback_url = settings.CALLBACK_URL
    # else:
    #     callback_url = 'https://khron.ru/googleauth'

    client_class = OAuth2Client
    queryset = ''


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def get_auth_url(request):
    url = settings.AUTHENTICATION_URL
    params = {'client_id': settings.CLIENT_ID,
              'redirect_uri': settings.CALLBACK_URL,
              'scope': 'User.Read',
              'response_type': 'code'}
    data = {
        'auth_url': url + '?' + urlencode(params)
    }
    return Response(data)


def home(request):
    return render(request, 'api/home.html')
