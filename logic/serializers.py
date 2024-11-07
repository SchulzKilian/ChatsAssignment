# serializers.py
from rest_framework import serializers
from .models import User, Chat, Message

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar', 'bio', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        if 'password' not in validated_data:
            raise serializers.ValidationError({
                'password': 'Password is required'
            })
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
    other_participants = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'last_message', 
                 'other_participants', 'messages', 'created_at']

    def get_last_message(self, obj):
        return MessageSerializer(obj.get_last_message()).data
    
    def get_other_participants(self, obj):
        current_user = self.context['request'].user
        # Get all participants except the current user
        other_participants = obj.get_other_participants(current_user)
        return UserSerializer(other_participants, many=True).data
