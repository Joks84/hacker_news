from django.contrib import admin
from .models import MyUser, Comment, Post, Likes

admin.site.register(MyUser)
admin.site.register(Comment)
admin.site.register(Post)
admin.site.register(Likes)
