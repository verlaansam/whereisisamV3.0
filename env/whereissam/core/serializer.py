from rest_framework import serializers
from . models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class WindSpeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = WindSpeed
        fields = ['id', 'name']

class WindDirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WindDirection
        fields = ['id', 'name']

class SeastateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seastate
        fields = ['id', 'name']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    windspeed = WindSpeedSerializer(read_only=True)
    winddirection = WindDirectionSerializer(read_only=True)
    seastate = SeastateSerializer(read_only=True)
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content',
            'categories', 'windspeed', 'winddirection', 'seastate',
            'image', 'author', 'created_at', 'comments'
        ]
