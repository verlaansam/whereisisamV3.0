from rest_framework import serializers
from . models import *
from core.models import Comment
from django.contrib.auth.models import User
from .models import Profile
from .models import WeatherVlieland, Location, Tides


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
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    post_title = serializers.CharField(source='post.title', read_only=True)
    post_slug = serializers.CharField(source='post.slug', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'content',
            'author_username',
            'author_avatar',
            'created_at',
            'post',
            'post_title',
            'post_slug',
        ]

    def get_author_avatar(self, obj):
        request = self.context.get('request')
        profile = getattr(obj.author, 'profile', None)  # veilig ophalen van profiel
        if profile and profile.avatar:
            return request.build_absolute_uri(profile.avatar.url)
        return None


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ["id", "album", "image", "caption", "uploaded_at"]


class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)  # nested: alle foto's in album
    post_title = serializers.ReadOnlyField(source="post.title")

    class Meta:
        model = Album
        fields = ["id", "title", "description", "author", "post", "post_title", "cover_image", "created_at", "photos"]

class AlbumMiniSerializer(serializers.ModelSerializer):
    photos = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = ["id", "title", "cover_image", "photos"]

    def get_photos(self, obj):
        return [photo.image.url for photo in obj.photos.all()[:3]]  # max 3 foto’s preview
        

class PostSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    windspeed = WindSpeedSerializer(read_only=True)
    winddirection = WindDirectionSerializer(read_only=True)
    seastate = SeastateSerializer(read_only=True)
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    albums = AlbumMiniSerializer(many=True, read_only=True) 

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content',
            'categories', 'windspeed', 'winddirection', 'seastate',
            'image', 'author', 'created_at', 'comments', 'albums'
        ]

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', required=False)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)

    class Meta:
        model = Profile
        fields = ['username', 'user_id', 'email', 'first_name', 'last_name', 'avatar']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        return super().update(instance, validated_data)


class WeatherVlielandSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherVlieland
        fields = [
            "id",
            "recorded_at",
            "wind_direction",
            "temperature",
            "wind_speed",
            "wind_gusts",
            "sea_temperature",
            "sight",
            "wave_height",
            "verwachting",
            "weather_warnings",
        ]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "location"]


class TideSerializer(serializers.ModelSerializer):
    location = serializers.CharField(source="location.location", read_only=True)
    type = serializers.CharField(source="tide_type", read_only=True)
    height = serializers.FloatField(source="waterheight", read_only=True, allow_null=True)
    time = serializers.DateTimeField(source="timestamp", read_only=True, allow_null=True)

    class Meta:
        model = Tides
        fields = ["id", "location", "type", "height", "time"]
