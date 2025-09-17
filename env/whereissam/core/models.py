from ckeditor.fields import RichTextField
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

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
