"""Image processing utilities for automatic WebP conversion and optimization."""
from PIL import Image
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
import os


def convert_image_to_webp(image_field):
    """
    Convert an image field to WebP format.
    Replaces the file in-place with a WebP version if settings.CONVERT_TO_WEBP is True.
    """
    if not settings.CONVERT_TO_WEBP or not image_field:
        return

    try:
        # Open the uploaded image
        img = Image.open(image_field)

        # Skip if already WebP
        if img.format == 'WEBP':
            return

        # Convert RGBA to RGB if necessary (WebP handles both, but for better compat)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background

        # Save as WebP
        output = BytesIO()
        quality = getattr(settings, 'IMAGE_QUALITY', 85)
        img.save(output, format='WEBP', quality=quality, method=6)
        output.seek(0)

        # Replace the file: change name from .jpg/.png to .webp
        old_name = image_field.name
        new_name = os.path.splitext(old_name)[0] + '.webp'
        image_field.save(new_name, ContentFile(output.read()), save=False)

    except Exception as e:
        # Log error but don't break the upload
        print(f"Error converting image to WebP: {e}")
        return
