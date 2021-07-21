from rest_framework import serializers
from .models import MyUser, Post, Comment, Likes


class MyUserSerializer(serializers.ModelSerializer):
    """MyUser serializer."""

    class Meta:
        model = MyUser
        fields = ["username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = super(MyUserSerializer, self).create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class CommentSerializer(serializers.ModelSerializer):
    """Serializer we will be using for nested serialization in PostDetailSerializer."""

    class Meta:
        model = Comment
        fields = (
            "author",
            "content",
            "creation_date",
            "post",
        )


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for listing Posts and their attributes."""

    author_username = serializers.SerializerMethodField()
    comments_number = serializers.SerializerMethodField()
    liked_by = serializers.PrimaryKeyRelatedField(
        many=True, queryset=MyUser.objects.all()
    )  # new

    class Meta:
        model = Post
        fields = (
            "author_name",
            "title",
            "author_username",
            "link",
            "creation_date",
            "comments_number",
            "liked_by",
        )

    def update(self, post: Post, validated_data):
        liked_by = validated_data.pop("validated_data")
        for i in liked_by:
            post.liked_by.add(i)
        post.save()
        return post

    def get_comments_number(self, post: Post):
        # Getting the number of comments on a post.
        return post.comment.count()

    def get_author_username(self, post: Post):
        # Getting the user's username.
        return post.author_name.username


class PostDetailSerializer(serializers.ModelSerializer):
    """Serializer for individual posts."""

    comment = CommentSerializer(many=True, read_only=True)
    author_username = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "title",
            "author_name",
            "author_username",
            "link",
            "creation_date",
            "comment",
        )

    def get_author_username(self, post: Post):
        # Getting the user's username.
        return post.author_name.username


class LikesSerializer(serializers.ModelSerializer):
    """Serializer for likes."""

    class Meta:
        model = Likes
        fields = ["user", "post"]
