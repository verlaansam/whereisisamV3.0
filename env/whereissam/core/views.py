from rest_framework import viewsets, permissions, status
from .models import (
    Category,
    WindSpeed,
    WindDirection,
    Seastate,
    Post,
    Comment,
    Album,
    Photo,
    WeatherVlieland,
    Location,
    Tides,
)
from .serializer import (
    CategorySerializer, WindSpeedSerializer, WindDirectionSerializer, 
    SeastateSerializer, PostSerializer, PostListSerializer, CommentSerializer, AlbumSerializer, AlbumListSerializer, PhotoSerializer, ProfileSerializer,
    WeatherVlielandSerializer, LocationSerializer, TideSerializer,
)
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from .models import Profile
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone


class IsOwnerOrAlbumOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        owner = getattr(obj, "author", None)
        if owner is not None:
            return owner == request.user
        album = getattr(obj, "album", None)
        return album is not None and album.author == request.user


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
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer

    def get_queryset(self):
        queryset = Post.objects.all().order_by('-created_at')
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'author']

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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAlbumOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return AlbumListSerializer
        return AlbumSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.select_related("album", "album__author").all().order_by("-uploaded_at")
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAlbumOwnerOrReadOnly]

    def perform_create(self, serializer):
        album = serializer.validated_data["album"]
        if not self.request.user.is_staff and album.author != self.request.user:
            raise PermissionDenied("You cannot upload photos to this album.")
        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class WeatherVlielandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WeatherVlieland.objects.all()
    serializer_class = WeatherVlielandSerializer
    permission_classes = [permissions.AllowAny]


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all().order_by("location")
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]


class TidesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TideSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Tides.objects.select_related("location").filter(timestamp__gte=timezone.now()).order_by("timestamp")
        location_slug = self.request.query_params.get("location")
        if location_slug:
            qs = qs.filter(location__location__iexact=location_slug)
        limit = self.request.query_params.get("limit")
        try:
            limit_value = int(limit) if limit is not None else 4
        except (TypeError, ValueError):
            limit_value = 4
        if limit_value > 0:
            qs = qs[:limit_value]
        return qs


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
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
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
