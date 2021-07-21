from hacker_app.models import MyUser, Comment, Post, Likes
from django.test import TestCase
from datetime import date


class TestModels(TestCase):
    """
    Creating one TestCase for all the models.
    """

    def setUp(self):
        # Creating the models.
        self.user = MyUser.objects.create(username="some_user")
        self.post = Post.objects.create(
            title="Some Title",
            link="https://somelink.co",
            author_name=self.user,
            creation_date=date.today(),
        )
        self.comment = Comment.objects.create(
            author=self.user,
            content="Some Comment",
            creation_date=date.today(),
            post=self.post,
        )
        self.likes = Likes.objects.create(
            user=self.user,
            post=self.post,
        )

    def test_user(self):
        # Testing user field.
        self.assertEqual(self.user.username, "some_user")

    def test_post(self):
        # Testing Post fields.
        self.assertEqual(self.post.title, "Some Title")
        self.assertEqual(self.post.link, "https://somelink.co")
        self.assertEqual(self.post.author_name.username, self.user.username)
        self.assertEqual(self.post.creation_date, date.today())

    def test_comment(self):
        # Testing Comment fields.
        self.assertEqual(self.comment.author.username, self.user.username)
        self.assertEqual(self.comment.content, "Some Comment")
        self.assertEqual(self.comment.creation_date, date.today())
        self.assertEqual(self.comment.post, self.post)

    def test_likes(self):
        # Testing Likes fields.
        self.assertEqual(self.likes.user, self.user)
        self.assertEqual(self.likes.post, self.post)
