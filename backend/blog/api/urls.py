from django.urls import path
from blog.api.views import (
  api_detail_blog_view,
  api_update_blog_view,
  api_delete_blog_view,
  api_create_blog_view,
  ApiPostListView,
  PostCreateView,
  api_post_like,
  api_post_unlike,
  get_like_state,
  api_post_comment,
  api_post_uncomment,
  get_post_comments,
  )



app_name = 'blog'

urlpatterns = [
  path('', ApiPostListView.as_view(), name="all"),
  path('create/', PostCreateView.as_view(), name="create"),
  path('<int:id>/', api_detail_blog_view, name="detail"),
  path('<int:id>/update', api_update_blog_view, name="update"),
  path('<int:id>/delete', api_delete_blog_view, name="delete"),
  path('<int:id>/like', api_post_like, name="like"),
  path('<int:id>/unlike', api_post_unlike, name="unlike"),
  path('<int:id>/like_state', get_like_state, name="like_state"),
  path('<int:id>/comment', api_post_comment, name="comment"),
  path('<int:id>/uncomment', api_post_uncomment, name="uncomment"),
  path('<int:id>/comments', get_post_comments, name="comment_number"),
]