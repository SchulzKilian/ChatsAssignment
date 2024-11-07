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
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SessionView, UserView, ChatView

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserView, basename='user')
router.register(r'chats', ChatView, basename='chat')

# The API URLs are determined automatically by the router
urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),

    # Session management
    path('auth/login/', SessionView.Login.as_view(), name='login'),
    path('auth/logout/', SessionView.Logout.as_view(), name='logout'),
]



# User endpoints:
# POST /users/ - create user (register)
# GET /users/ - list users
# GET /users/{id}/ - get specific user
# PUT /users/{id}/ - update user
# PATCH /users/{id}/ - partial update user
# DELETE /users/{id}/ - delete user
# DELETE /users/delete_account/ - delete current user account (custom action)

# Chat endpoints:
# GET /chats/ - list all chats
# POST /chats/ - create new chat
# GET /chats/{id}/ - get specific chat with messages
# PUT /chats/{id}/ - update chat
# PATCH /chats/{id}/ - partial update chat
# DELETE /chats/{id}/ - delete chat
# POST /chats/{id}/send_message/ - send message in specific chat (custom action)
# GET /chats/list_chats/ - get all chats with last message (custom action)