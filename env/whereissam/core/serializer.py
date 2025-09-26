from rest_framework import serializers
from . models import *
from core.models import Comment


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

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_username', 'content', 'created_at']
        read_only_fields = ['author', 'created_at']


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
