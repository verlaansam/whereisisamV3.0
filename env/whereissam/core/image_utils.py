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


def _build_optimized_image_file(source_file, original_name, target_width=None):
    try:
        source_file.seek(0)
        image = ImageOps.exif_transpose(Image.open(source_file))
    except (AttributeError, OSError, UnidentifiedImageError):
        return None

    original_stem = Path(original_name).stem or "upload"
    original_suffix = Path(original_name).suffix.lower()
    quality = getattr(settings, "IMAGE_QUALITY", 85)
    convert_to_webp = getattr(settings, "CONVERT_TO_WEBP", True)
    requires_resize = bool(target_width and image.width > target_width)
    image_format = (getattr(image, "format", None) or "").upper()
    already_webp = original_suffix == ".webp" or image_format == "WEBP"

    if not requires_resize and (already_webp or not convert_to_webp):
        return None

    if requires_resize:
        resized_height = round(image.height * (target_width / image.width))
        image = image.resize((target_width, resized_height), Image.Resampling.LANCZOS)

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


def resize_uploaded_image(uploaded_file, target_width):
    """
    Resize an uploaded image down to target_width while preserving aspect ratio.
    Returns the original file unchanged if no optimization is needed.
    """
    if not uploaded_file:
        return uploaded_file

    optimized_file = _build_optimized_image_file(uploaded_file, uploaded_file.name, target_width)
    return optimized_file or uploaded_file


def optimize_image_field(image_field, target_width=None):
    """
    Resize and/or convert an ImageField file in-place.
    Returns metadata when an optimization was applied, otherwise None.
    """
    if not image_field:
        return None

    try:
        old_name = image_field.name
        optimized_file = _build_optimized_image_file(image_field, old_name, target_width)
        if not optimized_file:
            return None
        image_field.save(optimized_file.name, ContentFile(optimized_file.read()), save=False)
        return {"old_name": old_name, "new_name": image_field.name}
    except Exception as e:
        print(f"Error converting image to WebP: {e}")
        return None
