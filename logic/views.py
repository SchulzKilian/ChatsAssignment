# views.py
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import UserSerializer, ChatSerializer, MessageSerializer
from .models import User, Chat, Message
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken


class SessionView(views.APIView):
    """Handles authentication"""
    permission_classes = [AllowAny]

    class Login(TokenObtainPairView):
        pass

    class Logout(views.APIView):
        permission_classes = [IsAuthenticated]
        
        def post(self, request):
            try:
                # Get the refresh token from request
                refresh_token = request.data.get('refresh')
                if refresh_token:
                    # Blacklist the specific token
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                    
                    # Optional: Blacklist all user's tokens for complete logout
                    user = request.user
                    tokens = OutstandingToken.objects.filter(user_id=user.id)
                    for token in tokens:
                        BlacklistedToken.objects.get_or_create(token=token)
                    
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

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
        # Blacklist all tokens for this user
        tokens = OutstandingToken.objects.filter(user_id=user.id)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)
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