from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, WindSpeedViewSet, WindDirectionViewSet,
    SeastateViewSet, PostViewSet, CommentViewSet, AlbumViewSet, PhotoViewSet
)
from django.urls import path
from .views import RegisterView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'windspeeds', WindSpeedViewSet)
router.register(r'winddirections', WindDirectionViewSet)
router.register(r'seastates', SeastateViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r"albums", AlbumViewSet)
router.register(r"photos", PhotoViewSet)


urlpatterns = router.urls
urlpatterns += [
    path('register/', RegisterView.as_view(), name='register'),
]
