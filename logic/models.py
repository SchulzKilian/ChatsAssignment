from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Max, Q
import uuid

class User(AbstractUser):
    """
    Extended User model with additional fields
    """
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    def get_all_chats(self):
        """Returns all chats for the user with last message and participant info"""
        return Chat.objects.filter(
            participants=self
        ).annotate(
            last_message_time=Max('messages__timestamp')
        ).prefetch_related(
            'participants', 
            'messages'
        ).order_by('-last_message_time')

    def start_chat_with(self, other_user):
        """Creates or returns existing chat with another user"""
        chat = Chat.objects.filter(participants=self).filter(participants=other_user).first()
        if not chat:
            chat = Chat.objects.create()
            chat.participants.add(self, other_user)
        return chat

    class Meta:
        db_table = 'auth_user'

class Chat(models.Model):
    """
    Chat model to represent a conversation between users
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_chat_messages(self, user, page_size=50, page=1):
        """Returns paginated messages for this chat and marks them as read"""
        messages = self.messages.all().order_by('-timestamp')
        
        # Mark unread messages as read
        messages.filter(
            is_read=False
        ).exclude(
            sender=user
        ).update(is_read=True)
        
        return messages[(page-1)*page_size:page*page_size]

    def get_last_message(self):
        """Returns the most recent message in the chat"""
        return self.messages.order_by('-timestamp').first()

    def get_other_participants(self, user):
        """Returns the other participant in a two-person chat"""
        return self.participants.exclude(id=user.id)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat {self.id} between {', '.join([str(user) for user in self.participants.all()])}"

class Message(models.Model):
    """
    Message model for storing chat messages
    """
    CONTENT_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('audio', 'Audio'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content_type = models.CharField(max_length=5, choices=CONTENT_TYPES, default='text')
    text_content = models.TextField(blank=True, null=True)
    media_content = models.FileField(upload_to='chat_media/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


    @classmethod
    def send_message(cls, sender, recipient, content, content_type='text', media=None):
        """Creates and sends a new message"""
        # Get or create chat between sender and recipient
        chat = sender.start_chat_with(recipient)
        
        # Create message
        message = cls.objects.create(
            chat=chat,
            sender=sender,
            content_type=content_type,
            text_content=content if content_type == 'text' else None,
            media_content=media if media else None
        )
        
        # Update chat timestamp
        chat.save()  # This updates the updated_at field
        
        return message

    def mark_as_read(self):
        """Marks message as read"""
        self.is_read = True
        self.save()

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender} in {self.chat}"