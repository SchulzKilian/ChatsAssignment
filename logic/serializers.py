# serializers.py
from rest_framework import serializers
from .models import User, Chat, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar', 'bio']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content_type', 'text_content', 
                 'media_content', 'timestamp', 'is_read']
        read_only_fields = ['sender', 'timestamp']

class ChatSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'last_message', 
                 'other_participant', 'messages', 'created_at']

    def get_last_message(self, obj):
        return MessageSerializer(obj.get_last_message()).data

    def get_other_participant(self, obj):
        user = self.context['request'].user
        other_user = obj.get_other_participant(user)
        return UserSerializer(other_user).data
