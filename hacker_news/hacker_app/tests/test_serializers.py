from django.test import TestCase
from hacker_app.models import MyUser, Comment, Post, Likes
from datetime import date
from collections import OrderedDict
from hacker_app.serializers import (
    MyUserSerializer,
    PostListSerializer,
    PostDetailSerializer,
    LikesSerializer,
)


class TestSerializers(TestCase):
    def setUp(self):
        # Creating the models.
        self.user = MyUser.objects.create(username="some_user")
        self.post = Post.objects.create(
            title="Some Title",
            link="https://somelink.co",
            author_name=self.user,
            creation_date=date.today(),
        )
        self.comment_1 = Comment.objects.create(
            author=self.user,
            content="First Comment",
            creation_date=date.today(),
            post=self.post,
        )
        self.comment_2 = Comment.objects.create(
            author=self.user,
            content="Second Comment",
            creation_date=date.today(),
            post=self.post,
        )
        self.like = Likes.objects.create(
            user=self.user,
            post=self.post,
        )

    def test_post_list_serializer(self):
        # Testing the fields and data of the PostListSerializer.
        serializer = PostListSerializer(self.post)
        expected_fields = {
            "title",
            "comments_number",
            "author_name",
            "link",
            "creation_date",
            "author_username",
            "liked_by",  # new
        }
        self.assertEqual(serializer.get_fields().keys(), expected_fields)

        data = serializer.data

        self.assertEqual(data["title"], self.post.title)
        self.assertEqual(data["comments_number"], 2)
        self.assertEqual(data["author_name"], self.user.id)
        self.assertEqual(data["link"], self.post.link)
        self.assertEqual(data["creation_date"], f"{date.today():%Y-%m-%d}")
        self.assertEqual(data["author_username"], self.user.username)
        self.assertEqual(data["liked_by"], [self.user.id])

    def test_post_detail_serializer(self):
        # Testing the fields and data for PostDetailSerializer.
        serializer = PostDetailSerializer(self.post)
        expected_fields = {
            "title",
            "author_name",
            "author_username",
            "link",
            "creation_date",
            "comment",
        }
        self.assertEqual(serializer.get_fields().keys(), expected_fields)

        # Checking serializer data.
        data = serializer.data

        self.assertEqual(data["title"], self.post.title)
        self.assertEqual(data["author_name"], self.post.author_name.id)
        self.assertEqual(data["link"], self.post.link)
        self.assertEqual(data["creation_date"], f"{date.today():%Y-%m-%d}")
        self.assertEqual(
            data["comment"],
            [
                OrderedDict(
                    [
                        ("author", self.comment_1.author.id),
                        ("content", self.comment_1.content),
                        ("creation_date", f"{date.today():%Y-%m-%d}"),
                        ("post", self.post.id),
                    ]
                ),
                OrderedDict(
                    [
                        ("author", self.comment_2.author.id),
                        ("content", self.comment_2.content),
                        ("creation_date", f"{date.today():%Y-%m-%d}"),
                        ("post", self.post.id),
                    ]
                ),
            ],
        )

    def test_likes_serializer(self):
        # Testing LikesSerializer with one like.
        serializer = LikesSerializer(self.like)
        expected_fields = {"user", "post"}

        self.assertEqual(serializer.get_fields().keys(), expected_fields)
        data = serializer.data
        self.assertEqual(data["user"], self.user.id)
        self.assertEqual(data["post"], self.post.id)
