import shutil
import tempfile
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient

from .models import Album, Photo


@override_settings(CONVERT_TO_WEBP=False)
class AlbumPhotoUploadAPITests(TestCase):
    def setUp(self):
        self.temp_media_dir = tempfile.mkdtemp()
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media_dir)
        self.media_override.enable()

        self.client = APIClient()
        self.owner = User.objects.create_user(username="owner", password="StrongPass123!")
        self.other_user = User.objects.create_user(username="other", password="StrongPass123!")
        self.album = Album.objects.create(title="Owner album", author=self.owner)

    def tearDown(self):
        self.media_override.disable()
        shutil.rmtree(self.temp_media_dir, ignore_errors=True)

    def _image_file(self, name="upload.png"):
        output = BytesIO()
        Image.new("RGB", (2, 2), color=(0, 128, 255)).save(output, format="PNG")
        output.seek(0)
        return SimpleUploadedFile(name, output.read(), content_type="image/png")

    def test_logged_in_backend_user_can_create_album_with_cover_image(self):
        self.assertTrue(self.client.login(username="owner", password="StrongPass123!"))

        response = self.client.post(
            reverse("album-list"),
            {"title": "New album", "cover_image": self._image_file("cover.png")},
            format="multipart",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["author"], self.owner.id)
        self.assertTrue(response.data["cover_image"].startswith("http://testserver/media/"))

    def test_logged_in_backend_user_can_upload_photo_to_owned_album(self):
        self.assertTrue(self.client.login(username="owner", password="StrongPass123!"))

        response = self.client.post(
            reverse("photo-list"),
            {
                "album": self.album.id,
                "caption": "Backend upload",
                "image": self._image_file("photo.png"),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(Photo.objects.count(), 1)
        self.assertEqual(response.data["album"], self.album.id)
        self.assertTrue(response.data["image"].startswith("http://testserver/media/"))

    def test_logged_in_backend_user_cannot_upload_photo_to_someone_elses_album(self):
        self.assertTrue(self.client.login(username="other", password="StrongPass123!"))

        response = self.client.post(
            reverse("photo-list"),
            {
                "album": self.album.id,
                "caption": "Should fail",
                "image": self._image_file("forbidden.png"),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 403, response.data)
        self.assertEqual(Photo.objects.count(), 0)
