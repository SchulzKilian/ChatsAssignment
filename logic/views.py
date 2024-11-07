# views.py
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from .models import User, Chat, Message
from .forms import UserRegistrationForm

class SessionView(View):
    """Handles all session-related views"""
    
    class Login(LoginView):
        template_name = 'login.html'
        success_url = reverse_lazy('chat-list')
        redirect_authenticated_user = True

    class Logout(LoginRequiredMixin, LogoutView):
        next_page = reverse_lazy('login')

class UserView(View):
    """Handles all user-related views"""
    
    def get(self, request, *args, **kwargs):
        """Handle GET request - show registration form"""
        return render(request, 'register.html', {'form': UserRegistrationForm()})

    def post(self, request, *args, **kwargs):
        """Handle POST request - process registration or deletion"""
        action = kwargs.get('action')
        
        if action == 'register':
            return self.register(request)
        elif action == 'delete':
            return self.delete_account(request)
    
    def register(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat-list')
        return render(request, 'register.html', {'form': form})

    @method_decorator(login_required)
    def delete_account(self, request):
        request.user.delete()
        return redirect('login')

class ChatView(LoginRequiredMixin, View):
    """Handles all chat-related views"""

    def get(self, request, *args, **kwargs):
        """Handle GET requests for chat list and detail views"""
        chat_id = kwargs.get('chat_id')
        
        if chat_id:
            return self.chat_detail(request, chat_id)
        return self.chat_list(request)

    def post(self, request, *args, **kwargs):
        """Handle POST requests for sending messages"""
        return self.send_message(request)

    def chat_list(self, request):
        """Show list of all chats"""
        chats = request.user.get_all_chats()
        return render(request, 'chat_list.html', {'chats': chats})

    def chat_detail(self, request, chat_id):
        """Show detail of specific chat"""
        chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
        context = {
            'chat': chat,
            'messages': chat.get_chat_messages(),
            'other_user': chat.get_other_participant(request.user)
        }
        return render(request, 'chat_detail.html', context)

    def send_message(self, request):
        """Handle message sending"""
        recipient_id = request.POST.get('recipient_id')
        content = request.POST.get('content')
        content_type = request.POST.get('content_type', 'text')
        media = request.FILES.get('media', None)

        try:
            recipient = User.objects.get(id=recipient_id)
            message = Message.send_message(
                sender=request.user,
                recipient=recipient,
                content=content,
                content_type=content_type,
                media=media
            )
            return JsonResponse({
                'status': 'success',
                'message_id': str(message.id),
                'timestamp': message.timestamp.isoformat()
            })
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Recipient not found'
            }, status=404)