"""firebase_test_by_sdk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
# from django.contrib import admin
from django.urls import path
from smauth import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('sign_up/', views.sign_up_post, name='sign_up'),
    path('sign_up_submit/', views.sign_up, name='sign_up_submit'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('logout/', views.logout, name='logout'),
    path('api_test/', views.api_test, name='api_test'),
    path('create_claim/', views.create_claim, name='create_claim'),
    path('delete_claim/', views.delete_claim, name='delete_claim'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('synchronization/', views.auth_db_synchronization, name='synchronization'),
    path('user_update/', views.user_update_post, name='user_update'),
    path('user_update_submit/', views.user_update, name='user_update_submit'),
    path('user_delete/', views.user_delete, name='user_delete'),
    path('user_token_info/', views.user_token_info, name='user_token_info')
]
