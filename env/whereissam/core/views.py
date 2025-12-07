from rest_framework import viewsets, permissions
from .models import Category, WindSpeed, WindDirection, Seastate, Post, Comment, Album, Photo, WeatherVlieland
from .serializer import (
    CategorySerializer, WindSpeedSerializer, WindDirectionSerializer, 
    SeastateSerializer, PostSerializer, CommentSerializer, AlbumSerializer, PhotoSerializer, ProfileSerializer,
    WeatherVlielandSerializer
)
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework import status, permissions
from django.contrib.auth import update_session_auth_hash
from .models import Profile
from django_filters.rest_framework import DjangoFilterBackend

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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        # 🔑 Hier voeg je de post toe via de request data
        post_id = self.request.data.get('post')
        serializer.save(author=self.request.user, post_id=post_id)

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all().order_by("-created_at")
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all().order_by("-uploaded_at")
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class WeatherVlielandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WeatherVlieland.objects.all()
    serializer_class = WeatherVlielandSerializer
    permission_classes = [permissions.AllowAny]


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
    
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Profiel bijgewerkt."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"detail": "Oude wachtwoord is onjuist."}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 6:
            return Response({"detail": "Nieuw wachtwoord moet minimaal 6 tekens zijn."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        return Response({"detail": "Wachtwoord succesvol gewijzigd."})
