import shutil
import tempfile
from io import BytesIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient

from .models import Album, Photo, Post


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


@override_settings(CONVERT_TO_WEBP=False)
class AlbumAdminUploadTests(TestCase):
    def setUp(self):
        self.temp_media_dir = tempfile.mkdtemp()
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media_dir)
        self.media_override.enable()

        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123!",
        )
        self.album = Album.objects.create(title="Admin album", author=self.admin_user)

    def tearDown(self):
        self.media_override.disable()
        shutil.rmtree(self.temp_media_dir, ignore_errors=True)

    def _image_file(self, name="upload.png", size=(2, 2)):
        output = BytesIO()
        Image.new("RGB", size, color=(0, 128, 255)).save(output, format="PNG")
        output.seek(0)
        return SimpleUploadedFile(name, output.read(), content_type="image/png")

    def test_admin_can_upload_photo_immediately_to_album(self):
        self.assertTrue(self.client.login(username="admin", password="StrongPass123!"))

        response = self.client.post(
            reverse("admin:core_album_upload_photo", args=[self.album.pk]),
            {"photo": self._image_file("instant.png")},
        )

        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(Photo.objects.count(), 1)
        payload = response.json()
        self.assertIn("image_url", payload)
        self.assertTrue(payload["image_url"].startswith("/media/"))

    def test_admin_upload_rejects_large_file(self):
        self.assertTrue(self.client.login(username="admin", password="StrongPass123!"))

        large_file = SimpleUploadedFile(
            "too-large.png",
            b"x" * (30 * 1024 * 1024 + 1),
            content_type="image/png",
        )
        response = self.client.post(
            reverse("admin:core_album_upload_photo", args=[self.album.pk]),
            {"photo": large_file},
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(Photo.objects.count(), 0)


@override_settings(CONVERT_TO_WEBP=False)
class AlbumListSerializerTests(TestCase):
    def setUp(self):
        self.temp_media_dir = tempfile.mkdtemp()
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media_dir)
        self.media_override.enable()

        self.client = APIClient()
        self.owner = User.objects.create_user(username="owner", password="StrongPass123!")
        self.album = Album.objects.create(
            title="Album with many photos",
            description="Only the three newest should be on the list view.",
            author=self.owner,
        )

    def tearDown(self):
        self.media_override.disable()
        shutil.rmtree(self.temp_media_dir, ignore_errors=True)

    def _image_file(self, name="upload.png", color=(0, 128, 255)):
        output = BytesIO()
        Image.new("RGB", (2, 2), color=color).save(output, format="PNG")
        output.seek(0)
        return SimpleUploadedFile(name, output.read(), content_type="image/png")

    def test_album_list_returns_only_three_most_recent_photos(self):
        photos = []
        for index in range(4):
            photo = Photo.objects.create(
                album=self.album,
                image=self._image_file(f"photo-{index}.png", color=(index, 128, 255)),
                caption=f"Photo {index}",
            )
            photos.append(photo)

        response = self.client.get(reverse("album-list"))

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(len(response.data), 1)
        payload = response.data[0]
        self.assertEqual(len(payload["photos"]), 3)
        self.assertEqual(
            [photo["id"] for photo in payload["photos"]],
            [photos[3].id, photos[2].id, photos[1].id],
        )

    def test_album_detail_still_returns_full_photo_list(self):
        for index in range(4):
            Photo.objects.create(
                album=self.album,
                image=self._image_file(f"detail-{index}.png", color=(index, 128, 255)),
                caption=f"Detail {index}",
            )

        response = self.client.get(reverse("album-detail", args=[self.album.pk]))

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(len(response.data["photos"]), 4)


@override_settings(CONVERT_TO_WEBP=False)
class PostListSerializerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(username="writer", password="StrongPass123!")
        self.post = Post.objects.create(
            title="Performance post",
            content="<p>Hello world</p><figure><img src='/media/test.png' /></figure><p>Extra text for preview.</p>",
            author=self.owner,
            is_published=True,
        )

    def test_post_list_returns_lightweight_preview_payload(self):
        response = self.client.get(reverse("post-list"))

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(len(response.data), 1)
        payload = response.data[0]
        self.assertEqual(payload["id"], self.post.id)
        self.assertIn("excerpt", payload)
        self.assertNotIn("content", payload)
        self.assertNotIn("comments", payload)
        self.assertNotIn("albums", payload)
        self.assertEqual(payload["excerpt"], "Hello world Extra text for preview.")


@override_settings(
    CONVERT_TO_WEBP=False,
    POST_IMAGE_MAX_WIDTH=100,
    ALBUM_COVER_MAX_WIDTH=100,
    ALBUM_PHOTO_MAX_WIDTH=120,
)
class ImageOptimizationTests(TestCase):
    def setUp(self):
        self.temp_media_dir = tempfile.mkdtemp()
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media_dir)
        self.media_override.enable()
        self.owner = User.objects.create_user(username="image-owner", password="StrongPass123!")

    def tearDown(self):
        self.media_override.disable()
        shutil.rmtree(self.temp_media_dir, ignore_errors=True)

    def _image_file(self, name="upload.png", size=(400, 200), color=(0, 128, 255)):
        output = BytesIO()
        Image.new("RGB", size, color=color).save(output, format="PNG")
        output.seek(0)
        return SimpleUploadedFile(name, output.read(), content_type="image/png")

    def test_new_uploads_are_resized_on_save(self):
        post = Post.objects.create(
            title="Resized image post",
            content="body",
            author=self.owner,
            image=self._image_file("post.png", size=(400, 200)),
        )
        album = Album.objects.create(
            title="Resized cover album",
            author=self.owner,
            cover_image=self._image_file("cover.png", size=(500, 250)),
        )
        photo = Photo.objects.create(
            album=album,
            image=self._image_file("photo.png", size=(360, 180)),
        )

        with Image.open(post.image.path) as image:
            self.assertLessEqual(image.width, 100)
        with Image.open(album.cover_image.path) as image:
            self.assertLessEqual(image.width, 100)
        with Image.open(photo.image.path) as image:
            self.assertLessEqual(image.width, 120)

    @override_settings(CONVERT_TO_WEBP=True, ALBUM_COVER_MAX_WIDTH=120)
    def test_management_command_optimizes_existing_cover_images(self):
        album = Album.objects.create(
            title="Existing cover album",
            author=self.owner,
            cover_image=self._image_file("legacy-cover.png", size=(600, 300)),
        )

        original_path = album.cover_image.path
        with Image.open(original_path) as image:
            self.assertLessEqual(image.width, 120)

        album.cover_image.delete(save=False)
        album.cover_image = self._image_file("legacy-cover.png", size=(600, 300))
        album._skip_image_optimization = True
        album.save(update_fields=["cover_image"])
        del album._skip_image_optimization

        with Image.open(album.cover_image.path) as image:
            self.assertEqual(image.width, 600)

        call_command("optimize_media_images")
        album.refresh_from_db()

        self.assertTrue(album.cover_image.name.endswith(".webp"))
        with Image.open(album.cover_image.path) as image:
            self.assertLessEqual(image.width, 120)
