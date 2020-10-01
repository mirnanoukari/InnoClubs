from django.shortcuts import render
from urllib.parse import urlencode

from allauth.socialaccount.providers.microsoft.views import MicrosoftGraphOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.serializers import SocialLoginSerializer
from allauth.account.adapter import get_adapter
from rest_auth.views import LoginView

from rest_framework import response, status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import RUDUserInfoSerializer, CreateClubSerializer, RetrieveClubsSerializer, JoinClubSerializer, LeaveClubSerializer, ChangeClubHeaderSerializer
from .models import User, Club
from .permissions import IsOwnerOrReadOnly, IsClubOwnerOrReadOnly, IsAdmin, IsValidEmail, IsValidTitle
from InnoClubs import settings


class SocialLoginView(LoginView):
    serializer_class = SocialLoginSerializer

    def process_login(self):
        get_adapter(self.request).login(self.request, self.user)


class OutlookLogin(SocialLoginView):
    adapter_class = MicrosoftGraphOAuth2Adapter

    callback_url = settings.CALLBACK_URL

    client_class = OAuth2Client
    queryset = ''


"""
Login process:
- get login url from /api/get_auth_url/
- go to that page and get code finally
- POST request to /api/microsoft/login/ with body {'code': code} and get 'key'
"""


class UserProfileRUDView(RetrieveUpdateDestroyAPIView):

    """
        NEED AUTHENTICATION:
        headers - {'Authorization': f'Token {token itself}'}

        GET:
        body - {'email': 'user email'}

        PUT:
        Body - {'email': 'user email',
                'first_name': 'new first name / empty string',
                'last_name': 'new last name / empty string',
                'telegram_alias': 'new telegram alias / empty string'}

        DELETE:
        body - {'email': 'user email'}
    """

    serializer_class = RUDUserInfoSerializer
    permission_classes = [IsAuthenticated, IsValidEmail, IsOwnerOrReadOnly]

    def get_object(self):
        email = self.request.data.get('email', None)
        self.check_permissions(self.request)
        self.check_object_permissions(self.request, User.objects.filter(email__iexact=email).first())
        return User.objects.filter(email__iexact=email).first()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):  # update
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.destroy(request, *args, **kwargs)
        return response.Response(data={'result': 'ok'}, status=status.HTTP_200_OK)


class CreateClubView(CreateAPIView):

    """
        NEED ADMIN RULES

        NEED AUTHENTICATION:
        headers - {'Authorization': f'Token {token itself}'}

        POST:
        body - {'title': 'title of the club (must be unique)',
                'description': 'description of the club / empty string'}
    """

    serializer_class = CreateClubSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListClubsView(ListAPIView):

    """
        NEED AUTHENTICATION:
        headers - {'Authorization': f'Token {token itself}'}

        GET
    """

    serializer_class = RetrieveClubsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Club.objects.all()


class RUDClubView(RetrieveUpdateDestroyAPIView):

    """
        NEED AUTHENTICATION:
        headers - {'Authorization': f'Token {token itself}'}

        GET:
        body - {'title': 'title of the club'}

        PUT:
        Body - {'title': 'title of the club (must be unique)',
                'new_title': 'new title of the club (must be unique)'
                'new_description': 'new club description / empty string'}

        DELETE:
        body - {'title': 'title of the club'}
    """

    serializer_class = RetrieveClubsSerializer
    permission_classes = [IsAuthenticated, IsClubOwnerOrReadOnly, IsValidTitle]

    def get_object(self):
        title = self.request.data.get('title', None)
        self.check_permissions(self.request)
        self.check_object_permissions(self.request, Club.objects.filter(title__iexact=title).first())
        return Club.objects.filter(title__iexact=title).first()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):  # update
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.destroy(request, *args, **kwargs)
        return response.Response(data={'status': 'success'}, status=status.HTTP_200_OK)


class JoinClubView(RetrieveUpdateAPIView):

    """
        NEED AUTHENTICATION:
        headers - {'Authorization': f'Token {token itself}'}

        PUT:
        body - {'title': 'title of the club'}
    """

    serializer_class = JoinClubSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        title = self.request.data.get('title', None)
        return Club.objects.filter(title__iexact=title).first()

    def put(self, request, *args, **kwargs):
        self.update(request, *args, **kwargs)
        return response.Response(data={'status': 'success'}, status=status.HTTP_200_OK)


class LeaveClubView(RetrieveUpdateAPIView):

    """
        NEED AUTHENTICATION:
        headers - {'Authorization': f'Token {token itself}'}

        PUT:
        body - {'title': 'title of the club'}
    """

    serializer_class = LeaveClubSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        title = self.request.data.get('title', None)
        return Club.objects.filter(title__iexact=title).first()

    def put(self, request, *args, **kwargs):
        self.update(request, *args, **kwargs)
        return response.Response(data={'status': 'success'}, status=status.HTTP_200_OK)


class ChangeClubHeaderView(RetrieveUpdateAPIView):

    """
        NEED AUTHENTICATION:
        headers - {'Authorization': f'Token {token itself}'}

        PUT:
        body - {'title': 'title of the club',
                'new_head_of_the_club': 'email of new club header'}
    """

    serializer_class = ChangeClubHeaderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        title = self.request.data.get('title', None)
        return Club.objects.filter(title__iexact=title).first()

    def put(self, request, *args, **kwargs):
        self.update(request, *args, **kwargs)
        return response.Response(data={'status': 'success'}, status=status.HTTP_200_OK)


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
