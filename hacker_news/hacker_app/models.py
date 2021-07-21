from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    liked_posts = models.ManyToManyField("Post", through="likes")

    def __str__(self):
        return self.username


class Post(models.Model):
    """Post model."""

    title = models.CharField(max_length=250)
    link = models.URLField()
    author_name = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True)
    liked_by = models.ManyToManyField(MyUser, related_name="likes", through="likes")

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comment model."""

    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    content = models.TextField()
    creation_date = models.DateField(auto_now_add=True)
    post = models.ForeignKey(Post, related_name="comment", on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class Likes(models.Model):
    """Likes model."""

    user = models.ForeignKey(MyUser, related_name="liked_by", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.user
