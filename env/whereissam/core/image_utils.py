"""Image processing utilities for automatic WebP conversion and optimization."""
from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
import os


def _flatten_transparency(image):
    if image.mode not in ("RGBA", "LA", "P"):
        return image
    if image.mode == "P":
        image = image.convert("RGBA")
    background = Image.new("RGB", image.size, (255, 255, 255))
    background.paste(image, mask=image.split()[-1] if image.mode in ("RGBA", "LA") else None)
    return background


def resize_uploaded_image(uploaded_file, target_width):
    """
    Resize an uploaded image down to target_width while preserving aspect ratio.
    Returns the original file unchanged if it is already small enough or invalid.
    """
    if not uploaded_file or not target_width:
        return uploaded_file

    try:
        uploaded_file.seek(0)
        image = ImageOps.exif_transpose(Image.open(uploaded_file))
    except (AttributeError, OSError, UnidentifiedImageError):
        return uploaded_file

    if image.width <= target_width:
        try:
            uploaded_file.seek(0)
        except (AttributeError, OSError):
            pass
        return uploaded_file

    resized_height = round(image.height * (target_width / image.width))
    image = image.resize((target_width, resized_height), Image.Resampling.LANCZOS)

    original_name = uploaded_file.name
    original_stem = Path(original_name).stem or "upload"
    original_suffix = Path(original_name).suffix.lower()
    quality = getattr(settings, "IMAGE_QUALITY", 85)
    convert_to_webp = getattr(settings, "CONVERT_TO_WEBP", True)

    output = BytesIO()
    if convert_to_webp:
        new_name = f"{original_stem}.webp"
        content_type = "image/webp"
        image.save(output, format="WEBP", quality=quality, method=6)
    else:
        format_name = "PNG" if original_suffix == ".png" else "JPEG"
        if format_name == "JPEG":
            image = _flatten_transparency(image)
            new_name = f"{original_stem}.jpg"
            content_type = "image/jpeg"
            image.save(output, format=format_name, quality=quality, optimize=True)
        else:
            new_name = f"{original_stem}.png"
            content_type = "image/png"
            image.save(output, format=format_name, optimize=True)

    output.seek(0)
    return SimpleUploadedFile(new_name, output.read(), content_type=content_type)


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
        img = _flatten_transparency(img)

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
