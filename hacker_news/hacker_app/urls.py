from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(f"homepage", views.HomePageViewSet, basename="homepage")
router.register(f"comments", views.CommentViewSet, basename="comments")
router.register(f"likes", views.LikesViewSet, basename="likes")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", views.MyUserCreate.as_view(), name="register"),
]
