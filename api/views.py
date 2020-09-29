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
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated

from .serializers import RUDUserInfoSerializer, CreateClubSerializer, RetrieveClubsSerializer, JoinClubSerializer, LeaveClubSerializer, ChangeClubHeaderSerializer
from .models import User, Club
from .permissions import IsOwnerOrReadOnly, IsClubOwnerOrReadOnly, IsAdmin
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


class UserProfileRUDView(RetrieveUpdateDestroyAPIView):

    serializer_class = RUDUserInfoSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        for obj in User.objects.all():
            if obj.email == self.request.query_params.get('email', None):
                return obj
        raise APIException(detail='There is no user with this email address')

    def get(self, request, *args, **kwargs):
        self.kwargs['email'] = request.query_params.get('email', None)
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):  # update
        self.kwargs['email'] = request.query_params.get('email', None)
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.kwargs['email'] = request.query_params.get('email', None)
        self.destroy(request, *args, **kwargs)
        return response.Response(data={'result': 'ok'}, status=status.HTTP_200_OK)


class CreateClubView(CreateAPIView):

    serializer_class = CreateClubSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Club.objects.create()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListClubsView(ListAPIView):

    serializer_class = RetrieveClubsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Club.objects.all()


class RUDClubView(RetrieveUpdateDestroyAPIView):

    serializer_class = RetrieveClubsSerializer
    permission_classes = [IsAuthenticated, IsClubOwnerOrReadOnly]
    lookup_field = 'title'

    def get_queryset(self):
        return Club.objects.all()

    def get(self, request, *args, **kwargs):
        self.kwargs['title'] = request.query_params.get('title', None)
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):  # update
        self.kwargs['title'] = request.query_params.get('title', None)
        return self.update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):  # update
        self.kwargs['title'] = request.query_params.get('title', None)
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.kwargs['title'] = request.query_params.get('title', None)
        self.destroy(request, *args, **kwargs)
        return response.Response(data={'status': 'success'}, status=status.HTTP_200_OK)


class JoinClubView(RetrieveUpdateAPIView):

    serializer_class = JoinClubSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'title'

    def get_queryset(self):
        return Club.objects.all()

    def get(self, request, *args, **kwargs):
        self.kwargs['title'] = request.query_params.get('title', None)
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self.kwargs['title'] = request.query_params.get('title', None)
        self.update(request, *args, **kwargs)
        return response.Response(data={'status': 'success'}, status=status.HTTP_200_OK)


class LeaveClubView(RetrieveUpdateAPIView):

    serializer_class = LeaveClubSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'title'

    def get_queryset(self):
        return Club.objects.all()

    def get(self, request, *args, **kwargs):
        self.kwargs['title'] = request.query_params.get('title', None)
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self.kwargs['title'] = request.query_params.get('title', None)
        self.update(request, *args, **kwargs)
        return response.Response(data={'status': 'success'}, status=status.HTTP_200_OK)


class ChangeClubHeaderView(RetrieveUpdateAPIView):

    serializer_class = ChangeClubHeaderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'title'

    def get_queryset(self):
        return Club.objects.all()

    def get(self, request, *args, **kwargs):
        self.kwargs['title'] = request.query_params.get('title', None)
        self.kwargs['head_of_the_club'] = request.query_params.get('head_of_the_club', None)
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self.kwargs['title'] = request.query_params.get('title', None)
        self.kwargs['head_of_the_club'] = request.query_params.get('head_of_the_club', None)
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
