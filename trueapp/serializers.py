from rest_framework import serializers
from .models import Contact, UserContactMapping, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'name', 'email']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class UserContactMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContactMapping
        fields = '__all__'