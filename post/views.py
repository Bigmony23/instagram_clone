from django.shortcuts import render
from rest_framework import generics, permissions

from .models import Post,PostLike,CommentLike
from .serializers import PostSerializer
from shared.custom_pagination import CustomPageNumberPagination

class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Post.objects.all()



# Create your views here.
