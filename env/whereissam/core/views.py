from rest_framework import viewsets, permissions
from .models import Category, WindSpeed, WindDirection, Seastate, Post, Comment
from .serializer import (
    CategorySerializer, WindSpeedSerializer, WindDirectionSerializer, 
    SeastateSerializer, PostSerializer, CommentSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class WindSpeedViewSet(viewsets.ModelViewSet):
    queryset = WindSpeed.objects.all()
    serializer_class = WindSpeedSerializer
    permission_classes = [permissions.AllowAny]


class WindDirectionViewSet(viewsets.ModelViewSet):
    queryset = WindDirection.objects.all()
    serializer_class = WindDirectionSerializer
    permission_classes = [permissions.AllowAny]


class SeastateViewSet(viewsets.ModelViewSet):
    queryset = Seastate.objects.all()
    serializer_class = SeastateSerializer
    permission_classes = [permissions.AllowAny]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
