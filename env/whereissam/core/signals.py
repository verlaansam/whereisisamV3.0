from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import Post, Album, Photo, Profile
from .image_utils import optimize_image_field
import os


def _should_skip_image_optimization(instance):
    return getattr(instance, "_skip_image_optimization", False)


@receiver(pre_save, sender=Post)
def convert_post_image_to_webp(sender, instance, **kwargs):
    if instance.image and not _should_skip_image_optimization(instance):
        optimize_image_field(instance.image, getattr(settings, "POST_IMAGE_MAX_WIDTH", 1600))

@receiver(pre_save, sender=Album)
def convert_album_cover_to_webp(sender, instance, **kwargs):
    if instance.cover_image and not _should_skip_image_optimization(instance):
        optimize_image_field(instance.cover_image, getattr(settings, "ALBUM_COVER_MAX_WIDTH", 1600))

@receiver(pre_save, sender=Photo)
def convert_photo_image_to_webp(sender, instance, **kwargs):
    if instance.image and not _should_skip_image_optimization(instance):
        optimize_image_field(instance.image, getattr(settings, "ALBUM_PHOTO_MAX_WIDTH", 1800))

@receiver(pre_save, sender=Profile)
def convert_profile_avatar_to_webp(sender, instance, **kwargs):
    if instance.avatar and not _should_skip_image_optimization(instance):
        optimize_image_field(instance.avatar, getattr(settings, "AVATAR_IMAGE_MAX_WIDTH", 512))

# 🔹 Post image verwijderen
@receiver(post_delete, sender=Post)
def delete_post_image(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

# 🔹 Album cover verwijderen
@receiver(post_delete, sender=Album)
def delete_album_cover(sender, instance, **kwargs):
    if instance.cover_image:
        if os.path.isfile(instance.cover_image.path):
            os.remove(instance.cover_image.path)

# 🔹 Photo image verwijderen
@receiver(post_delete, sender=Photo)
def delete_photo_image(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

# 🔹 Optioneel: oude bestanden verwijderen bij update
@receiver(pre_save, sender=Post)
def delete_old_post_image(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_image = Post.objects.get(pk=instance.pk).image
    except Post.DoesNotExist:
        return
    new_image = instance.image
    if old_image and old_image != new_image and os.path.isfile(old_image.path):
        os.remove(old_image.path)

# idem voor Album en Photo
