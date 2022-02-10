from rest_framework import serializers
from django_restql.mixins import DynamicFieldsMixin

from blog.models import Post, PostLike, PostComment


class PostSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    #image_url = serializers.SerializerMethodField('get_image_url')
    username = serializers.SerializerMethodField('get_username_from_author')
    like_number = serializers.SerializerMethodField('post_like_count')
    comment_number = serializers.SerializerMethodField('post_comment_count')

    class Meta:
        model = Post
        fields = ['id', 'title',  'created_on', 'content', 'status', 'picture', 'username', 'like_number', 'comment_number']

    def get_username_from_author(self, post):
      username = post.author.username
      return username

    def post_like_count(self, post):
      like_number = PostLike.objects.filter(post=post).count()
      return like_number
    
    def post_comment_count(self, post):
      comment_number = PostComment.objects.filter(post=post).count()
      return comment_number

    """
    def get_image_url(self, post):
        request = self.context.get("request")
        return request.build_absolute_uri(post.picture.url)"""

class PostLikeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = PostLike
        fields = ['user', 'post']

class PostCommentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    username = serializers.SerializerMethodField('get_username_from_user')
    
    class Meta:
      model = PostComment
      fields = ['user', 'post', 'comment', 'created', 'username']

    def get_username_from_user(self, comment):
      first_name = comment.user.first_name
      last_name = comment.user.last_name
      name = first_name + " " + last_name
      return name
