from hacker_app.models import MyUser, Comment, Post, Likes
from django.test import TestCase
from datetime import date
from django.urls import reverse
from rest_framework import status
from collections import OrderedDict


class TestViewSets(TestCase):
    def setUp(self):
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
        self.like = Likes.objects.create(
            user=self.user,
            post=self.post,
        )

    def test_homepage_viewset_list(self):
        # Testing the Homepage list viewset.
        response = self.client.get(reverse("homepage-list"))
        data = response.data[0]
        # Checking status code.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Checking data.
        self.assertEqual(data["title"], self.post.title)
        self.assertEqual(data["comments_number"], 1)
        self.assertEqual(data["author_name"], self.post.author_name.id)
        self.assertEqual(data["author_username"], self.post.author_name.username)
        self.assertEqual(data["link"], self.post.link)
        self.assertEqual(data["creation_date"], f"{date.today():%Y-%m-%d}")
        self.assertEqual(data["liked_by"], [self.user.id])

    def test_homepage_post_detail(self):
        # Testing detail view/retrieve method.
        response = self.client.get(reverse("homepage-detail", args=[self.post.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        # Testing Response data.
        self.assertEqual(data["title"], self.post.title)
        self.assertEqual(data["author_name"], self.post.author_name.id)
        self.assertEqual(data["author_username"], self.post.author_name.username)
        self.assertEqual(data["link"], self.post.link)
        self.assertEqual(data["creation_date"], f"{date.today():%Y-%m-%d}")
        self.assertEqual(
            data["comment"],
            [
                OrderedDict(
                    [
                        ("author", self.comment.author.id),
                        ("content", self.comment.content),
                        ("creation_date", f"{date.today():%Y-%m-%d}"),
                        ("post", self.post.id),
                    ]
                )
            ],
        )

    def test_homepage_viewset_create(self):

        create_data = {
            "title": "Second Post",
            "link": "https://google.com",
            "author_name": self.user.id,
        }
        # Testing if unauthenticated user can create post.
        response_forbidden = self.client.post(reverse("homepage-list"), create_data)
        self.assertEqual(response_forbidden.status_code, status.HTTP_403_FORBIDDEN)

        # Logging the user:
        self.client.force_login(self.user)
        response = self.client.post(reverse("homepage-list"), create_data)
        # Checking status code.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.data
        # Checking data.
        self.assertEqual(data["author_name"], self.user.id)
        self.assertEqual(data["title"], create_data["title"])
        self.assertEqual(data["comments_number"], 0)
        self.assertEqual(data["author_username"], self.user.username)
        self.assertEqual(data["link"], create_data["link"])
        self.assertEqual(data["creation_date"], f"{date.today():%Y-%m-%d}")
        self.assertEqual(data["liked_by"], [])

    def test_comments_list(self):
        # Firstly testing response and data provided in the setUp().
        response = self.client.get(reverse("comments-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data[0]

        self.assertEqual(data["author"], self.comment.author.id)
        self.assertEqual(data["content"], self.comment.content)
        self.assertEqual(data["creation_date"], f"{date.today():%Y-%m-%d}")
        self.assertEqual(data["post"], self.post.id)

        # Creating new user and adding comment the new user provided.
        new_user = MyUser.objects.create(username="jelena_jo")
        create_comment = {
            "author": new_user.id,
            "content": "Another Comment",
            "post": self.post.id,
        }
        # Testing if unauthenticated user can create comment.
        response_forbidden = self.client.post(reverse("comments-list"), create_comment)
        self.assertEqual(response_forbidden.status_code, status.HTTP_403_FORBIDDEN)

        # Logging the user and testing the status code and data.
        self.client.force_login(new_user)
        response = self.client.post(reverse("comments-list"), create_comment)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.data
        self.assertEqual(data["author"], new_user.id)
        self.assertEqual(data["content"], create_comment["content"])
        self.assertEqual(data["creation_date"], f"{date.today():%Y-%m-%d}")
        self.assertEqual(data["post"], self.post.id)

        # After creating the new comment, we are returning to a 'comments-list' url to check if new comment is being
        # saved.
        response = self.client.get(reverse("comments-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data[0]
        self.assertEqual(
            data,
            OrderedDict(
                [
                    ("author", self.comment.author.id),
                    ("content", self.comment.content),
                    ("creation_date", f"{date.today():%Y-%m-%d}"),
                    ("post", self.post.id),
                ]
            ),
            OrderedDict(
                [
                    ("author", new_user.id),
                    ("content", create_comment["content"]),
                    ("creation_date", f"{date.today():%Y-%m-%m}"),
                    ("post", self.post.id),
                ]
            ),
        )
        # Getting back to homepage to check if both comments are properly shown.
        homepage_response = self.client.get(reverse("homepage-list"))
        self.assertEqual(homepage_response.status_code, status.HTTP_200_OK)
        data = homepage_response.data[0]
        self.assertEqual(
            data,
            OrderedDict(
                [
                    ("author_name", self.post.author_name.id),
                    ("title", self.post.title),
                    ("author_username", self.post.author_name.username),
                    ("link", self.post.link),
                    ("creation_date", f"{date.today():%Y-%m-%d}"),
                    ("comments_number", 2),
                    ("liked_by", [self.user.id]),
                ]
            ),
        )

    def test_adding_comments(self):
        # Here we are testing multiple comments, from multiple users on multiple posts to see if the feature shows
        # comments properly on each place.
        user_2 = MyUser.objects.create(username="username")
        post_2 = Post.objects.create(
            title="New Title",
            link="https://newlink.co",
            author_name=user_2,
        )

        comment_1_data = {
            "author": user_2.id,
            "content": "Another Comment",
            "post": self.post.id,
        }
        comment_2_data = {
            "author": user_2.id,
            "content": "Another Comment",
            "post": post_2.id,
        }
        comment_3_data = {
            "author": self.user.id,
            "content": "Another Comment",
            "post": post_2.id,
        }

        # Firstly, we are testing if the unauthenticated user can post comments.
        forbidden_response_1 = self.client.post(
            reverse("comments-list"), comment_1_data
        )
        forbidden_response_2 = self.client.post(
            reverse("comments-list"), comment_2_data
        )
        forbidden_response_3 = self.client.post(
            reverse("comments-list"), comment_3_data
        )

        self.assertEqual(forbidden_response_1.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(forbidden_response_2.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(forbidden_response_3.status_code, status.HTTP_403_FORBIDDEN)

        # Logging the users.
        self.client.force_login(self.user)
        self.client.force_login(user_2)

        # Creating and saving comments.
        response_1 = self.client.post(reverse("comments-list"), comment_1_data)
        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)

        response_2 = self.client.post(reverse("comments-list"), comment_2_data)
        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)

        response_3 = self.client.post(reverse("comments-list"), comment_3_data)
        self.assertEqual(response_3.status_code, status.HTTP_201_CREATED)

        # Checking the data.
        homepage_response = self.client.get(reverse("homepage-list"))

        self.assertEqual(homepage_response.status_code, status.HTTP_200_OK)
        data_1 = homepage_response.data[0]
        data_2 = homepage_response.data[1]

        # data_1 -> first post and it's data.
        self.assertEqual(data_1["author_name"], self.post.author_name.id)
        self.assertEqual(data_1["title"], self.post.title)
        self.assertEqual(data_1["author_username"], self.post.author_name.username)
        self.assertEqual(data_1["link"], self.post.link)
        self.assertEqual(data_1["creation_date"], f"{date.today():%Y-%m-%d}")
        self.assertEqual(data_1["comments_number"], 2)
        self.assertEqual(data_1["liked_by"], [self.user.id])

        # data_2 -> second post and it's data.
        self.assertEqual(data_2["author_name"], post_2.author_name.id)
        self.assertEqual(data_2["title"], post_2.title)
        self.assertEqual(data_2["author_username"], post_2.author_name.username)
        self.assertEqual(data_2["link"], post_2.link)
        self.assertEqual(data_2["creation_date"], f"{date.today():%Y-%m-%d}")
        self.assertEqual(data_2["comments_number"], 2)
        self.assertEqual(data_2["liked_by"], [])

        # Checking the status and data of first post.
        first_post_response = self.client.get(
            reverse("homepage-detail", args=[self.post.id])
        )
        self.assertEqual(first_post_response.status_code, status.HTTP_200_OK)

        first_post_data = first_post_response.data

        self.assertEqual(first_post_data["title"], self.post.title)
        self.assertEqual(first_post_data["author_name"], self.post.author_name.id)
        self.assertEqual(
            first_post_data["author_username"], self.post.author_name.username
        )
        self.assertEqual(first_post_data["link"], self.post.link)
        self.assertEqual(first_post_data["creation_date"], f"{date.today():%Y-%m-%d}")
        self.assertEqual(
            first_post_data["comment"],
            [
                OrderedDict(
                    [
                        ("author", self.comment.author.id),
                        ("content", self.comment.content),
                        ("creation_date", f"{date.today():%Y-%m-%d}"),
                        ("post", self.post.id),
                    ]
                ),
                OrderedDict(
                    [
                        ("author", comment_1_data["author"]),
                        ("content", comment_1_data["content"]),
                        ("creation_date", f"{date.today():%Y-%m-%d}"),
                        ("post", self.post.id),
                    ]
                ),
            ],
        )

        second_post_response = self.client.get(
            reverse("homepage-detail", args=[post_2.id])
        )

        # Checking the status and data for the second post.
        self.assertEqual(second_post_response.status_code, status.HTTP_200_OK)

        second_post_data = second_post_response.data

        self.assertEqual(second_post_data["title"], post_2.title)
        self.assertEqual(second_post_data["author_name"], post_2.author_name.id)
        self.assertEqual(
            second_post_data["author_username"], post_2.author_name.username
        )
        self.assertEqual(second_post_data["link"], post_2.link)
        self.assertEqual(second_post_data["creation_date"], f"{date.today():%Y-%m-%d}")
        self.assertEqual(
            second_post_data["comment"],
            [
                OrderedDict(
                    [
                        ("author", comment_2_data["author"]),
                        ("content", comment_2_data["content"]),
                        ("creation_date", f"{date.today():%Y-%m-%d}"),
                        ("post", post_2.id),
                    ]
                ),
                OrderedDict(
                    [
                        ("author", comment_3_data["author"]),
                        ("content", comment_3_data["content"]),
                        ("creation_date", f"{date.today():%Y-%m-%d}"),
                        ("post", post_2.id),
                    ]
                ),
            ],
        )

    def test_adding_likes(self):
        # Testing Likes viewset with the data defined in the setUp().
        response = self.client.get(reverse("likes-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data[0]
        self.assertEqual(data["user"], self.user.id)
        self.assertEqual(data["post"], self.post.id)

        # Testing Likes viewset with additional data.
        user_2 = MyUser.objects.create(username="joks")
        post_2 = Post.objects.create(
            title="Likes Post",
            link="https://link.co",
            author_name=user_2,
        )
        likes_2 = {
            "user": user_2.id,
            "post": post_2.id,
        }
        likes_3 = {
            "user": user_2.id,
            "post": self.post.id,
        }

        # Testing if unauthenticated users can like posts.
        forbidden_response_2 = self.client.post(reverse("likes-list"), likes_2)
        forbidden_response_3 = self.client.post(reverse("likes-list"), likes_3)

        self.assertEqual(forbidden_response_2.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(forbidden_response_3.status_code, status.HTTP_403_FORBIDDEN)

        # Logging the new user:
        self.client.force_login(user_2)

        # Testing the response's status codes and data.
        response_2 = self.client.post(reverse("likes-list"), likes_2)
        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)

        data_2 = response_2.data
        self.assertEqual(data_2["user"], user_2.id)
        self.assertEqual(data_2["post"], post_2.id)

        response_3 = self.client.post(reverse("likes-list"), likes_3)
        self.assertEqual(response_3.status_code, status.HTTP_201_CREATED)

        data_3 = response_3.data
        self.assertEqual(data_3["user"], user_2.id)
        self.assertEqual(data_3["post"], self.post.id)

    def test_user_create(self):
        # Testing user create view.
        response = self.client.post(
            reverse("register"), {"username": "me", "password": "my_password"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
