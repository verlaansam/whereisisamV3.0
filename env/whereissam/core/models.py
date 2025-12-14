from ckeditor.fields import RichTextField
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class WindSpeed(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class WindDirection(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Seastate(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True) 
    content = RichTextField()
    categories = models.ManyToManyField(Category, blank=True)  # Meerdere categorieën
    windspeed = models.ForeignKey(WindSpeed, on_delete=models.SET_NULL, null=True, blank=True)
    winddirection = models.ForeignKey(WindDirection, on_delete=models.SET_NULL, null=True, blank=True)
    seastate = models.ForeignKey(Seastate, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)  # afbeelding
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)  # maak slug van de titel
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reactie van {self.author} op {self.post}"

class Album(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="albums")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="albums", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cover_image = models.ImageField(upload_to='album_covers/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} (Post: {self.post.title if self.post else 'Geen post'})"

class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="album_photos/")
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto in album: {self.album.title}"

class WeatherVlieland(models.Model):
    recorded_at = models.DateTimeField(db_index=True)
    wind_direction = models.CharField(max_length=50, null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    wind_speed = models.FloatField(null=True, blank=True)
    wind_gusts = models.FloatField(null=True, blank=True)
    sea_temperature = models.FloatField(null=True, blank=True)
    sight = models.CharField(max_length=50, null=True, blank=True)
    wave_height = models.FloatField(null=True, blank=True)
    verwachting = models.TextField(blank=True, default="")
    weather_warnings = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-recorded_at"]
        db_table = "weatherVlieland"
        verbose_name = "Weather Vlieland"
        verbose_name_plural = "Weather Vlieland"

    def __str__(self):
        return f"Vlieland {self.recorded_at:%Y-%m-%d %H:%M}"
    
class Location(models.Model):
    location = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.location
    
class Tides(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="tides", null=True, blank=True)
    tide_type = models.CharField(max_length=20)
    waterheight = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["timestamp"]
        verbose_name = "Tide"
        verbose_name_plural = "Tides"

    def __str__(self):
        return f"{self.location} {self.tide_type} @ {self.timestamp}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
