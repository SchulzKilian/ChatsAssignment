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
from django.contrib import admin
from django.urls import path
from .views import SessionView, UserView, ChatView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Session URLs
    path('login/', SessionView.Login.as_view(), name='login'),
    path('logout/', SessionView.Logout.as_view(), name='logout'),
    
    # User URLs
    path('register/', UserView.as_view(), kwargs={'action': 'register'}, name='register'),
    path('delete-account/', UserView.as_view(), kwargs={'action': 'delete'}, name='delete-account'),
    
    # Chat URLs
    path('chats/', ChatView.as_view(), name='chat-list'),
    path('chat/<uuid:chat_id>/', ChatView.as_view(), name='chat-detail'),
    path('message/send/', ChatView.as_view(), name='send-message'),
]