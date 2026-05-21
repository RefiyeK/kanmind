from rest_framework.permissions import BasePermission

from kanban_app.models import Task


class IsBoardMemberForTask(BasePermission):
    """Allows only members or the owner of the board the task belongs to."""

    def has_object_permission(self, request, view, obj):
        """Checks whether the user is a member or owner of the task's board."""
        user = request.user
        return (
            obj.board.owner == user
            or obj.board.members.filter(id=user.id).exists()
        )


class IsTaskCreatorOrBoardOwner(BasePermission):
    """Allows only the task creator or the board owner to delete the task."""

    def has_object_permission(self, request, view, obj):
        """Checks whether the user is the task creator or the board owner."""
        user = request.user
        return obj.created_by == user or obj.board.owner == user


class IsCommentAuthor(BasePermission):
    """Allows only the author of the comment to delete it."""

    def has_object_permission(self, request, view, obj):
        """Checks whether the user is the author of the comment."""
        return obj.author == request.user


class IsBoardMemberForComment(BasePermission):
    """Allows only the owner or members of the task's board to list or create comments."""

    def has_permission(self, request, view):
        """Resolves the task via the URL's task_id and checks board membership."""
        # No object exists yet for list/create — look up the task from the URL kwargs.
        task_id = view.kwargs.get('task_id')
        task = Task.objects.filter(pk=task_id).first()
        if task is None:
            return False
        user = request.user
        return (
            task.board.owner == user
            or task.board.members.filter(id=user.id).exists()
        )



class IsBoardOwner(BasePermission):
    """Allows only the board owner to perform the action."""

    def has_object_permission(self, request, view, obj):
        """Checks whether the user is the owner of the board."""
        return obj.owner == request.user