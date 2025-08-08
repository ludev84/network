from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User)

    def serialize(self):
        return {
            "user": self.user.username,
            "content": self.content,
            "created_at": self.created_at.strftime("%b %d %Y, %I:%M %p"),
        }

    def number_of_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}..."  # Display first 20 characters of content


class Follow(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
