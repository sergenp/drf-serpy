from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    class Meta:
        ordering = ["-created"]

    name = models.CharField(max_length=120)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    class Meta:
        ordering = ["-created"]

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=240)
    content = models.TextField()
    image = models.ImageField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name="+")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    class Meta:
        ordering = ["-created"]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.CharField(max_length=240)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment
