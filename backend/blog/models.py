from django.db import models
from django.contrib.auth.models import User


STATUS = (
    (0,"Draft"),
    (1,"Publish")
)

class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete= models.CASCADE,related_name='blog_posts')
    content = models.TextField()
    picture = models.ImageField(upload_to='images/', default="default.jpeg")
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)


    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

class PostLike(models.Model):
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    post = models.ForeignKey(Post,  on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

class PostComment(models.Model):
    comment = models.CharField(max_length=255)
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    post = models.ForeignKey(Post,  on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)