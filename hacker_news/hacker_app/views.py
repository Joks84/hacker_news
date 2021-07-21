from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post, Comment, Likes, MyUser
from .serializers import (
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
    LikesSerializer,
    MyUserSerializer,
)
from rest_framework import generics


class HomePageViewSet(viewsets.ModelViewSet):
    """
    Creating the HomePage for listing all the Posts.
    Using ModelViewSet allows us to extend the viewset furthermore.
    """

    serializer_class = PostListSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "retrieve":
            self.serializer_class = PostDetailSerializer
        return self.serializer_class


class CommentViewSet(viewsets.ModelViewSet):
    """Viewset for Comments."""

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]


class LikesViewSet(viewsets.ModelViewSet):
    """Viewset for Likes."""

    queryset = Likes.objects.all()
    serializer_class = LikesSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class MyUserCreate(generics.CreateAPIView):
    """Viewset for creating users."""
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer
