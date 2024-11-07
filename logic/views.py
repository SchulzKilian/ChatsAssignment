# views.py
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import UserSerializer, ChatSerializer, MessageSerializer
from .models import User, Chat, Message

class SessionView(views.APIView):
    """Handles authentication"""
    permission_classes = [AllowAny]

    class Login(TokenObtainPairView):
        pass

    class Logout(views.APIView):
        permission_classes = [IsAuthenticated]
        
        def post(self, request):
            # Blacklist the token if using JWT blacklist
            return Response(status=status.HTTP_204_NO_CONTENT)

class UserView(viewsets.ModelViewSet):
    """Handles user operations"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'create':  # registration
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        return User.objects.all()

    @action(detail=False, methods=['delete'])
    def delete_account(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        """Handle registration"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

class ChatView(viewsets.ModelViewSet):
    """Handles chat operations"""
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)

    def retrieve(self, request, pk=None):
        """Get specific chat with messages"""
        chat = self.get_object()
        serializer = self.get_serializer(chat, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in a specific chat"""
        chat = self.get_object()
        serializer = MessageSerializer(data=request.data)
        
        if serializer.is_valid():
            message = serializer.save(
                sender=request.user,
                chat=chat
            )
            return Response(
                MessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def list_chats(self, request):
        """Get all chats for current user"""
        chats = request.user.get_all_chats()
        serializer = self.get_serializer(
            chats, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)