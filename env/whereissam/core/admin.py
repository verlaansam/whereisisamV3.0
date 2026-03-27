from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.urls import reverse
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import (
    Post,
    Category,
    WindSpeed,
    WindDirection,
    Seastate,
    Comment,
    Album,
    Photo,
    WeatherVlieland,
    Tides,
)

MAX_ALBUM_BULK_UPLOADS = 20
MAX_ALBUM_IMAGE_SIZE = 30 * 1024 * 1024


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.FileField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if not data:
            return []
        if isinstance(data, (list, tuple)):
            return [single_file_clean(item, initial) for item in data]
        return [single_file_clean(data, initial)]


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditorUploadingWidget(
            attrs={
                "style": "width: 100%;",
            }
        )
    )

    class Meta:
        model = Post
        exclude = ("is_published",)


class AlbumAdminForm(forms.ModelForm):
    bulk_photos = MultipleImageField(
        required=False,
        help_text="Upload up to 20 images at once. Maximum 30 MB per image.",
        widget=MultipleImageInput(attrs={"accept": "image/*"}),
        label="Bulk upload photos",
    )

    class Meta:
        model = Album
        fields = "__all__"

    def clean_bulk_photos(self):
        photos = self.cleaned_data.get("bulk_photos") or []
        if len(photos) > MAX_ALBUM_BULK_UPLOADS:
            raise ValidationError(f"You can upload a maximum of {MAX_ALBUM_BULK_UPLOADS} images at once.")
        for photo in photos:
            if photo.size > MAX_ALBUM_IMAGE_SIZE:
                raise ValidationError(f"{photo.name} is larger than 30 MB.")
        return photos


class PhotoInline(admin.TabularInline):  # of StackedInline als je meer ruimte wilt
    model = Photo
    extra = 1
    fields = ("image_preview", "image", "caption")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" alt="{}" style="width: 90px; height: 90px; object-fit: cover; border-radius: 6px;" />',
                obj.image.url,
                obj.caption or obj.album.title,
            )
        return "-"

    image_preview.short_description = "Preview"

class AlbumInline(admin.TabularInline):
    model = Album
    extra = 1

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    form = AlbumAdminForm
    list_display = ("title", "author", "post", "created_at")
    list_filter = ("author", "post", "created_at")
    search_fields = ("title", "description")
    inlines = [PhotoInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        bulk_photos = form.cleaned_data.get("bulk_photos") or []
        for photo in bulk_photos:
            Photo.objects.create(album=form.instance, image=photo)
        if bulk_photos:
            self.message_user(request, f"Uploaded {len(bulk_photos)} photos to this album.")


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
    form = PostAdminForm
    list_display = ('title', 'publication_status', 'author', 'windspeed', 'winddirection', 'seastate', 'created_at', 'image')
    list_filter = ('is_published', 'categories', 'windspeed', 'winddirection', 'seastate', 'author', 'created_at')
    search_fields = ('title', 'content')
    inlines = [AlbumInline]

    class Media:
        css = {"all": ("core/admin.css",)}

    def publication_status(self, obj):
        return "Published" if obj.is_published else "Draft"

    publication_status.short_description = "Status"

    def save_model(self, request, obj, form, change):
        if "_saveasdraft" in request.POST:
            obj.is_published = False
        elif any(key in request.POST for key in ("_save", "_continue", "_addanother", "_saveasnew")):
            obj.is_published = True
        super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        if "_saveasdraft" in request.POST:
            self.message_user(request, "The post was saved as a draft and is hidden from the website.")
            return HttpResponseRedirect(
                reverse(
                    f"admin:{self.opts.app_label}_{self.opts.model_name}_change",
                    args=(obj.pk,),
                    current_app=self.admin_site.name,
                )
            )
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if "_saveasdraft" in request.POST:
            self.message_user(request, "The post was saved as a draft and is hidden from the website.")
            return HttpResponseRedirect(
                reverse(
                    f"admin:{self.opts.app_label}_{self.opts.model_name}_change",
                    args=(obj.pk,),
                    current_app=self.admin_site.name,
                )
            )
        return super().response_change(request, obj)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at", "content_short")
    list_filter = ("created_at", "author")
    search_fields = ("content", "author__username", "post__title")
    ordering = ("-created_at",)

    def content_short(self, obj):
        return obj.content[:50] + ("..." if len(obj.content) > 50 else "")
    content_short.short_description = "Commentaar"

@admin.register(WeatherVlieland)
class WeatherVlielandAdmin(admin.ModelAdmin):
    list_display = (
        "recorded_at",
        "temperature",
        "wind_direction",
        "wind_speed",
        "wind_gusts",
        "sea_temperature",
        "sight",
        "wave_height",
    )
    list_filter = ("recorded_at",)
    search_fields = ("weather_warnings", "verwachting")


@admin.register(Tides)
class TidesAdmin(admin.ModelAdmin):
    list_display = ("location", "tide_type", "waterheight", "timestamp")
    list_filter = ("location", "tide_type")
    search_fields = ("location__location",)
    ordering = ("location__location", "timestamp")
