"""
URL configuration for logic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SessionView, UserView, ChatView

router = DefaultRouter()
router.register(r'users', UserView, basename='user')
router.register(r'chats', ChatView, basename='chat')

urlpatterns = [
    path('', include(router.urls)),
    # Session endpoints
    path('auth/login/', SessionView.Login.as_view(), name='login'),
    path('auth/logout/', SessionView.Logout.as_view(), name='logout'),
    
    # For ViewSets, we need to specify the actions
    path('register/', UserView.as_view({
        'post': 'create'
    }), name='register'),
    path('delete-account/', UserView.as_view({
        'delete': 'delete_account'
    }), name='delete-account'),
]