from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, WindSpeedViewSet, WindDirectionViewSet,
    SeastateViewSet, PostViewSet, CommentViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'windspeeds', WindSpeedViewSet)
router.register(r'winddirections', WindDirectionViewSet)
router.register(r'seastates', SeastateViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = router.urls
