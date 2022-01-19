from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from .models import Comment, Post, Tag, User


class ViewSetsTestCase(APITestCase):
    @staticmethod
    def create_image(name):
        if name % 7 == 0:
            return
        image_path = settings.BASE_DIR / "test.jpg"
        with image_path.open("rb") as fp:
            content = fp.read()
        return SimpleUploadedFile(
            name=f"{name}.png",
            content=content,
            content_type="image/jpeg",
        )

    @classmethod
    def setUpTestData(cls):
        for u in range(2):
            user = User.objects.create(
                username=f"test-{u}",
                email=f"test-{u}@test.com",
                first_name=f"First Test-{u}",
                last_name=f"Last Test-{u}",
            )

            for p in range(2):
                post = Post.objects.create(
                    author=user,
                    title=f"Post-{p}-{u}",
                    content=f"Content-{p}-{u}",
                    image=cls.create_image(u + p),
                )

                for t in range(2):
                    post.tags.add(Tag.objects.create(name=f"Tag-{t}"))

                for c in range(2):
                    Comment.objects.create(
                        user=user, post=post, comment=f"Comment-{c}-{p}-{u}"
                    )

    def test_post(self):
        response = self.client.get("/api/post/")
        print(response.data)

    def test_comment(self):
        response = self.client.get("/api/comment/")
        print(response.data)
