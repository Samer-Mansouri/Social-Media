from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from blog.models import Post, PostLike, PostComment
from blog.api.serializers import PostSerializer, PostLikeSerializer, PostCommentSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.core.cache import cache




CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class ApiPostListView(ListAPIView):
  queryset = Post.objects.filter(status=1)
  serializer_class = PostSerializer
  authentication_classes = (JWTAuthentication,)
  permission_classes = (IsAuthenticated,)
  pagination_class = PageNumberPagination


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def api_all_blog_view(request):
  posts = Post.objects.filter(status=1)
  if request.method == "GET":
    data = []
    for post in posts:
      serializer = PostSerializer(post)
      data.append(serializer.data)
    return Response(data)

@permission_classes((IsAuthenticated,))
@api_view(['GET', ])
@cache_page(CACHE_TTL)
def api_detail_blog_view(request, id):

    if id in cache:
      post = cache.get(id)
      print("Cache")
    else:
      try:
        post = Post.objects.get(id=id)
        print("DB")
        cache.set(id, post)
      except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
      serializer = PostSerializer(post)
      data = serializer.data
      if data["username"] == request.user.username:
        data["owner"] = 1
      return Response(data)

@api_view(['PUT', ])
@permission_classes((IsAuthenticated,))
def api_update_blog_view(request, id):

    try:
      post = Post.objects.get(id=id)
    except Post.DoesNotExist:
      return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if post.author != user:
      return Response({'response' : "You don't have permission to edit that"})

    if request.method == "PUT":

      serializer = PostSerializer(post, data=request.data)
      data = {}
      if serializer.is_valid():
        serializer.save()
        data["success"] = "Updated Succesfuly"
        return Response(data=data)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
@permission_classes((IsAuthenticated,))
def api_delete_blog_view(request, id):

    try:
      post = Post.objects.get(id=id)
    except Post.DoesNotExist:
      return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if post.author != user:
      return Response({'response' : "You don't have permission to delete that"})

    if request.method == "DELETE":
      post.status = 0;
      post.save()
      data = {}
      print(post.status)
      if post.status == 0:
        data["success"] = "Deleted With Success"
      else:
        data["failure"] = "Delete Failed"
      return Response(data=data)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_create_blog_view(request):

  user = request.user
  post = Post(author=user)
  
  if request.method == "POST":
    serializer = PostSerializer(post, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostCreateView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    parser_classes = [MultiPartParser, FormParser]
  

    def post(self, request, format=None):

        print(request.data)
        user = request.user
        print(user)
        post = Post(author=user)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



###Like View
@api_view(['DELETE', ])
@permission_classes((IsAuthenticated,))
def api_post_unlike(request, id):

  try:
      postlike = PostLike.objects.get(user=request.user, post=id)
  except PostLike.DoesNotExist:
      return Response({"Error" : "This post like doesn't exist"},status=status.HTTP_404_NOT_FOUND)

  user = request.user
  if postlike.user != user:
      return Response({'response' : "You don't have permission to unlike that"})
      
  if request.method == "DELETE":
      operation = postlike.delete()
      data = {}
      if operation :
        data["unliked"] = "Unliked With Success"
      else:
        data["failure"] = "Unlike Failed"
      return Response(data=data)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_post_like(request, id):

  user = request.user
  postlike = PostLike(user=user,post_id=id)
  print(user)
  data = {
    "user": user.id,
    "post": id
  }
  
  if request.method == "POST":
      already_liked = PostLike.objects.filter(user=request.user, post=id).count()
      if already_liked == 0:
          serializer = PostLikeSerializer(postlike, data=data)
          if serializer.is_valid():
            serializer.save()
            data["like"] = "liked with success"
            return Response(data, status=status.HTTP_201_CREATED)
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      return Response({"Error" : "Already Liked"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', ])
@permission_classes((IsAuthenticated, ))
def get_like_state(request, id):
  if request.method == "GET": 
    like_state = PostLike.objects.filter(user=request.user, post=id).count()
    return Response({"status" : like_state}, status=status.HTTP_200_OK)

##Comment Views
@api_view(['POST', ])
@permission_classes((IsAuthenticated, ))
def api_post_comment(request,id):

  user = request.user
  postcomment = PostComment(user=user, post_id=id)
  
  data = {
    "user": user.id,
    "post": id,
    "comment": request.data.get("comment")
  }
  if request.method == "POST":
    serializer = PostCommentSerializer(postcomment, data=data)
    if serializer.is_valid():
      serializer.save()
      return Response({"comment" : "commented with success"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE', ])
@permission_classes((IsAuthenticated, ))
def api_post_uncomment(request, id):
  
  try:
      postcomment = PostComment.objects.get(id=id) #Comment id
  except PostComment.DoesNotExist:
      return Response({"Error" : "This comment doesn't exist"},status=status.HTTP_404_NOT_FOUND)

  user = request.user
  if postcomment.user != user:
      return Response({'response' : "You don't have permission to uncomment that"})
      
  if request.method == "DELETE":
      operation = postcomment.delete()
      data = {}
      if operation :
        data["unliked"] = "Unliked With Success"
      else:
        data["failure"] = "Unlike Failed"
      return Response(data=data)

@api_view(['GET', ])
@permission_classes((IsAuthenticated, ))
def get_post_comments(request, id):
  if request.method == "GET": 
    comments = PostComment.objects.filter(post=id).order_by("-created")
    data = []
    for comment in comments:
      serializer = PostCommentSerializer(comment)
      if request.user.id == serializer.data["user"]:
        dataSer = serializer.data
        dataSer["owner"] = 1
        data.append(dataSer)
      else:
        data.append(serializer.data)

    return Response(data, status=status.HTTP_200_OK)
