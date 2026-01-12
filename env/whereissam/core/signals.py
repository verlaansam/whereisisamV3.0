from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Post, Album, Photo
from .image_utils import convert_image_to_webp
import os

# 🔹 Convert images to WebP before save (pre_save to avoid recursion)
@receiver(pre_save, sender=Post)
def convert_post_image_to_webp(sender, instance, **kwargs):
    if instance.image and not instance.image.name.endswith('.webp'):
        convert_image_to_webp(instance.image)

@receiver(pre_save, sender=Album)
def convert_album_cover_to_webp(sender, instance, **kwargs):
    if instance.cover_image and not instance.cover_image.name.endswith('.webp'):
        convert_image_to_webp(instance.cover_image)

@receiver(pre_save, sender=Photo)
def convert_photo_image_to_webp(sender, instance, **kwargs):
    if instance.image and not instance.image.name.endswith('.webp'):
        convert_image_to_webp(instance.image)

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
