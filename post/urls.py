from django.urls import path
from .views import PostListAPIView, PostCreateAPIView, PostRetrieveUpdateDestroyAPIView, PostCommentListAPIView, \
    PostCommentCreateAPIView, CommentListCreateAPIView, PostLikeListCreateAPIView, CommentLikeListCreateAPIView, \
    PostLikeListAPIView, CommentRetrieveApiView, CommentLikeView, PostLikeApiView, CommentLikeCreateView

urlpatterns=[
    path('posts/',PostListAPIView.as_view(),name='index'),
    path('post_create/',PostCreateAPIView.as_view(),name='post_create'),
    path('post/<uuid:pk>/',PostRetrieveUpdateDestroyAPIView.as_view(),name='post_retrieve'),
    path('post/<uuid:pk>/comments',PostCommentListAPIView.as_view(),name='post_update'),
    path('post/<uuid:pk>/likes', PostLikeListAPIView.as_view(), name='likes'),

    path('post/<uuid:pk>/create/comment',PostCommentCreateAPIView.as_view(),name='post_create'),
    path('post/comments',CommentListCreateAPIView.as_view(),name='post_update'),
    path('comments/<uuid:pk>/',CommentRetrieveApiView.as_view(),name='comment'),
    path('comments/<uuid:pk>/likes',CommentLikeView.as_view(),name='comment_likes'),
    path('post/likes',PostLikeListCreateAPIView.as_view(),name='post_likes'),
    path('comment/likes',CommentLikeListCreateAPIView.as_view(),name='comment_likes'),
    path('<uuid:pk>/create-delete-like',PostLikeApiView.as_view(),name='post_liking'),
    path('<uuid:pk>/create-delete-commentlike',CommentLikeCreateView.as_view(),name='comment_liking'),

]
