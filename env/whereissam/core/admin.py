from django.contrib import admin
from .models import Post, Category, WindSpeed, WindDirection, Seastate
from .models import Post, Category, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(WindSpeed)
class WindSpeedAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(WindDirection)
class WindDirectionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Seastate)
class SeastateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'windspeed', 'winddirection', 'seastate', 'created_at', 'image')
    list_filter = ('categories', 'windspeed', 'winddirection', 'seastate', 'author', 'created_at')
    search_fields = ('title', 'content')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at", "content_short")
    list_filter = ("created_at", "author")
    search_fields = ("content", "author__username", "post__title")
    ordering = ("-created_at",)

    def content_short(self, obj):
        return obj.content[:50] + ("..." if len(obj.content) > 50 else "")
    content_short.short_description = "Commentaar"
