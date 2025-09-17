from rest_framework import viewsets, permissions
from .models import Category, WindSpeed, WindDirection, Seastate, Post, Comment
from .serializer import (
    CategorySerializer, WindSpeedSerializer, WindDirectionSerializer, 
    SeastateSerializer, PostSerializer, CommentSerializer
)
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

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

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")  # nieuw veld

        if not username or not password or not email:
            return Response({"detail": "Username, password en email zijn verplicht."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"detail": "Gebruikersnaam bestaat al."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"detail": "Email bestaat al."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        return Response({"detail": "Account aangemaakt."}, status=status.HTTP_201_CREATED)
    

