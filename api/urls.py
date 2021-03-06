"""InnoClubs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . import views


urlpatterns = [

    path('get_auth_url/', views.get_auth_url, name='get-auth-url'),
    path('microsoft/login/', views.OutlookLogin.as_view(), name='user-login'),

    path('user_profile/', views.UserProfileRUDView.as_view(), name='user-profile'),

    path('get_clubs/', views.ListClubsView.as_view(), name='clubs-view'),
    path('club_profile/', views.RUDClubView.as_view(), name='club-view'),

    path('create_club/', views.CreateClubView.as_view(), name='club-create'),
    path('join_club/', views.JoinClubView.as_view(), name='join-club'),
    path('leave_club/', views.LeaveClubView.as_view(), name='leave-club'),
    path('change_club_header/', views.ChangeClubHeaderView.as_view(), name='change-club-header')

]
