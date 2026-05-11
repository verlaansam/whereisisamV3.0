from rest_framework import serializers
from . models import *
from core.models import Comment
from django.contrib.auth.models import User
from .models import Profile
from .models import WeatherVlieland, Location, Tides
import re
from django.conf import settings


def build_absolute_media_url(request, file_field):
    if not file_field:
        return None
    url = getattr(file_field, "url", None) or str(file_field)
    if request and isinstance(url, str) and url.startswith("/"):
        return request.build_absolute_uri(url)
    return url


def strip_media_for_preview(html):
    if not html:
        return ""
    try:
        content = str(html)
        content = re.sub(r"<figure[\s\S]*?<\/figure>", "", content, flags=re.IGNORECASE)
        content = re.sub(r"<(iframe|video)[\s\S]*?<\/\1>", "", content, flags=re.IGNORECASE)
        content = re.sub(r"<img[^>]*>", "", content, flags=re.IGNORECASE)
        return content
    except Exception:
        return str(html)


def build_excerpt(html, max_length=220):
    plain_text = re.sub(r"<[^>]+>", " ", strip_media_for_preview(html))
    plain_text = re.sub(r"\s+", " ", plain_text).strip()
    if len(plain_text) <= max_length:
        return plain_text
    return f"{plain_text[: max_length - 1].rstrip()}…"


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
    image = serializers.ImageField()

    class Meta:
        model = Photo
        fields = ["id", "album", "image", "caption", "uploaded_at"]
        read_only_fields = ["uploaded_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = build_absolute_media_url(self.context.get("request"), instance.image)
        return data


class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)  # nested: alle foto's in album
    post_title = serializers.ReadOnlyField(source="post.title")
    cover_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Album
        fields = ["id", "title", "description", "author", "post", "post_title", "cover_image", "created_at", "photos"]
        read_only_fields = ["author", "created_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["cover_image"] = build_absolute_media_url(self.context.get("request"), instance.cover_image)
        return data

class AlbumListSerializer(serializers.ModelSerializer):
    photos = serializers.SerializerMethodField()
    cover_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Album
        fields = ["id", "title", "description", "cover_image", "created_at", "photos"]

    def get_photos(self, obj):
        photos = obj.photos.order_by("-uploaded_at")[:3]
        return PhotoSerializer(photos, many=True, context=self.context).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["cover_image"] = build_absolute_media_url(self.context.get("request"), instance.cover_image)
        return data

class AlbumMiniSerializer(serializers.ModelSerializer):
    photos = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = ["id", "title", "cover_image", "photos"]

    def get_photos(self, obj):
        request = self.context.get('request')
        photos = obj.photos.order_by("-uploaded_at")[:3]
        result = []
        for photo in photos:
            if photo.image:
                if request:
                    result.append(request.build_absolute_uri(photo.image.url))
                else:
                    result.append(photo.image.url)
        return result
        

class PostSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    windspeed = WindSpeedSerializer(read_only=True)
    winddirection = WindDirectionSerializer(read_only=True)
    seastate = SeastateSerializer(read_only=True)
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    albums = AlbumMiniSerializer(many=True, read_only=True) 
    image = serializers.SerializerMethodField()

    content = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content',
            'categories', 'windspeed', 'winddirection', 'seastate',
            'image', 'author', 'created_at', 'comments', 'albums'
        ]

    def get_content(self, obj):
        """Return content with root-relative image src paths converted to absolute URLs."""
        request = self.context.get('request')
        content = obj.content or ""
        if not request:
            return content
        # Be defensive: ensure content is a str and handle quoted and unquoted src=
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8', 'replace')
            content = str(content)

            pattern = re.compile(r'src=(["\']?)(/[^"\'\s>]*)\1?')

            def repl(match):
                quote = match.group(1) or '"'
                path = match.group(2)
                # leave absolute URLs untouched
                if path.startswith('http'):
                    return f'src={quote}{path}{quote}'
                # convert root-relative paths (/media/..., /uploads/...) to absolute URLs
                if path.startswith('/'):
                    abs_url = request.build_absolute_uri(path)
                    return f'src={quote}{abs_url}{quote}'
                return match.group(0)

            return pattern.sub(repl, content)
        except Exception:
            # If anything goes wrong, return original content unchanged
            return content

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class PostListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "title", "slug", "image", "created_at", "excerpt"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_excerpt(self, obj):
        return build_excerpt(obj.content)

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', required=False)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['username', 'user_id', 'email', 'first_name', 'last_name', 'avatar']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

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
