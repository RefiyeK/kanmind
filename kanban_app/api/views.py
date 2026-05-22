from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied

from kanban_app.models import Board, Task, Comment
from .permissions import (
    IsBoardMemberForTask,
    IsTaskCreatorOrBoardOwner,
    IsCommentAuthor,
    IsBoardMemberForComment,
    IsBoardOwner,
    IsBoardMemberOrOwner,
)
from .serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardUpdateSerializer,
    TaskSerializer,
    TaskUpdateSerializer,
    CommentSerializer,
)


class BoardListCreateView(generics.ListCreateAPIView):
    """View for listing and creating boards of the currently authenticated user."""

    serializer_class = BoardSerializer

    def get_queryset(self):
        """Returns only boards where the user is the owner or a member."""
        # Q allows OR conditions; .distinct() removes duplicates from the M2M join.
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        """Sets the currently authenticated user as the owner of the new board."""
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating, and deleting a single board."""

    def get_queryset(self):
        """Returns only boards; access is controlled by the permissions."""
        return Board.objects.all()

    def get_serializer_class(self):
        """Selects the appropriate serializer based on the HTTP method."""
        if self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def get_permissions(self):
        """Selects the appropriate permissions based on the HTTP method."""
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardMemberOrOwner()]


class TaskAssignedToMeView(generics.ListAPIView):
    """View that lists all tasks assigned to the currently authenticated user."""

    serializer_class = TaskSerializer

    def get_queryset(self):
        """Returns all tasks where the current user is the assignee."""
        user = self.request.user
        return Task.objects.filter(assignee=user)


class TaskReviewingView(generics.ListAPIView):
    """View that lists all tasks where the currently authenticated user is the reviewer."""

    serializer_class = TaskSerializer

    def get_queryset(self):
        """Returns all tasks where the current user is the reviewer."""
        user = self.request.user
        return Task.objects.filter(reviewer=user)


class TaskCreateView(generics.CreateAPIView):
    """View for creating a new task on a board."""

    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        """Sets the currently authenticated user as the creator of the new task."""
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        """Checks board existence (404) and membership (403) before creating the task."""
        board = Board.objects.filter(pk=request.data.get('board')).first()
        if board is None:
            raise NotFound("Board not found.")
        user = request.user
        if board.owner != user and not board.members.filter(id=user.id).exists():
            raise PermissionDenied(
                "You must be a member of the board to create a task.")
        return super().create(request, *args, **kwargs)


class TaskUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View for updating (PATCH) and deleting (DELETE) a task."""

    queryset = Task.objects.all()

    def get_serializer_class(self):
        """Selects the appropriate serializer based on the HTTP method."""
        if self.request.method == 'PATCH':
            return TaskUpdateSerializer
        return TaskSerializer

    def get_permissions(self):
        """Selects the appropriate permissions based on the HTTP method."""
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated(), IsBoardMemberForTask()]


class CommentListCreateView(generics.ListCreateAPIView):
    """View for listing and creating comments on a task."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberForComment]

    def get_queryset(self):
        """Returns all comments for the given task (sorted chronologically)."""
        task_id = self.kwargs.get('task_id')
        return Comment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        """Automatically sets the task from the URL and the author from the request."""
        task_id = self.kwargs.get('task_id')
        task = Task.objects.get(pk=task_id)
        serializer.save(author=self.request.user, task=task)


class CommentDestroyView(generics.DestroyAPIView):
    """View for deleting a comment (only by the author)."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_queryset(self):
        """Returns all comments for the given task."""
        task_id = self.kwargs.get('task_id')
        return Comment.objects.filter(task_id=task_id)
