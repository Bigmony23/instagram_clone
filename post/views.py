from django.shortcuts import render

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Post, PostLike, CommentLike, PostComment
from .serializers import PostSerializer, CommentLikeSerializer, CommentSerializer, PostLikeSerializer
from shared.custom_pagination import CustomPageNumberPagination

class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Post.objects.all()

class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def put(self, request, *args, **kwargs):

        post=self.get_object()
        serializer = self.serializer_class(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'code': status.HTTP_200_OK,
            'message': 'Post successfully updated',
            'data': serializer.data

        })
    def delete(self, request, *args, **kwargs):
        post=self.get_object()
        post.delete()
        return Response({
            'success': True,
            'code': status.HTTP_204_NO_CONTENT,
            'message': 'Post successfully deleted',

        })
class PostCommentListAPIView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        post_id =self.kwargs['pk']
        queryset = PostComment.objects.filter(post__id=post_id)
        return queryset

class PostCommentCreateAPIView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_id=self.kwargs['pk']
        serializer.save(author=self.request.user,post_id=post_id)

# class CommentCreateView(generics.CreateAPIView):
#     serializer_class = CommentSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)
class CommentListCreateAPIView(generics.ListCreateAPIView):
    queryset = PostComment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPageNumberPagination


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostLikeListCreateAPIView(generics.ListCreateAPIView):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentLikeListCreateAPIView(generics.ListCreateAPIView):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)