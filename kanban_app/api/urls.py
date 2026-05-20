from django.urls import path

from .views import (
    BoardListCreateView,
    BoardDetailView,
    TaskAssignedToMeView,
    TaskReviewingView,
    TaskCreateView,
    TaskUpdateDestroyView,
    CommentListCreateView,
    CommentDestroyView,
)

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),

    path('tasks/assigned-to-me/', TaskAssignedToMeView.as_view(),
         name='tasks-assigned-to-me'),
    path('tasks/reviewing/', TaskReviewingView.as_view(), name='tasks-reviewing'),
    path('tasks/', TaskCreateView.as_view(), name='tasks-create'),
    path('tasks/<int:pk>/', TaskUpdateDestroyView.as_view(), name='task-detail'),

    path('tasks/<int:task_id>/comments/',
         CommentListCreateView.as_view(), name='comment-list-create'),
    path('tasks/<int:task_id>/comments/<int:pk>/',
         CommentDestroyView.as_view(), name='comment-destroy'),
]
