from rest_framework import serializers

from auth_app.models import User
from kanban_app.models import Board, Task, Comment


class BoardSerializer(serializers.ModelSerializer):
    """Serializer for boards with computed fields for members and tasks."""

    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id',
            'members',
        ]

    def get_member_count(self, obj):
        """Returns the number of members of the board."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Returns the total number of tasks of the board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Returns the number of tasks with status 'to-do'."""
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """Returns the number of tasks with priority 'high'."""
        return obj.tasks.filter(priority='high').count()

    def create(self, validated_data):
        """Creates a new board and assigns the provided members."""
        # Remove members from validated_data: M2M fields cannot be passed to .create() directly.
        members = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        if members:
            board.members.set(members)
        return board


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a board with nested owner and member data."""

    owner_data = serializers.SerializerMethodField()
    members_data = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data', 'members']

    def get_owner_data(self, obj):
        """Returns the full owner data as a nested object."""
        return {
            'id': obj.owner.id,
            'email': obj.owner.email,
            'fullname': obj.owner.fullname,
        }

    def get_members_data(self, obj):
        """Returns the full member data as a list of nested objects."""
        return [
            {'id': m.id, 'email': m.email, 'fullname': m.fullname}
            for m in obj.members.all()
        ]

    def update(self, instance, validated_data):
        """Updates the title and/or members of a board."""
        # Default is None (not []): None means "do not touch members", [] would clear all members.
        members = validated_data.pop('members', None)
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        if members is not None:
            instance.members.set(members)
        return instance


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for tasks with nested assignee/reviewer and writable user ID fields."""

    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    # source='assignee' lets the incoming 'assignee_id' (PK) write directly to the 'assignee' FK.
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
            'comments_count',
            'assignee_id',
            'reviewer_id',
        ]

    def get_assignee(self, obj):
        """Returns the assigned user as a nested object."""
        if obj.assignee:
            return {
                'id': obj.assignee.id,
                'email': obj.assignee.email,
                'fullname': obj.assignee.fullname,
            }
        return None

    def get_reviewer(self, obj):
        """Returns the reviewer as a nested object."""
        if obj.reviewer:
            return {
                'id': obj.reviewer.id,
                'email': obj.reviewer.email,
                'fullname': obj.reviewer.fullname,
            }
        return None

    def get_comments_count(self, obj):
        """Returns the total number of comments on the task."""
        return obj.comments.count()


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tasks without the 'board' and 'comments_count' fields."""

    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
            'assignee_id',
            'reviewer_id',
        ]

    def get_assignee(self, obj):
        """Returns the assigned user as a nested object."""
        if obj.assignee:
            return {
                'id': obj.assignee.id,
                'email': obj.assignee.email,
                'fullname': obj.assignee.fullname,
            }
        return None

    def get_reviewer(self, obj):
        """Returns the reviewer as a nested object."""
        if obj.reviewer:
            return {
                'id': obj.reviewer.id,
                'email': obj.reviewer.email,
                'fullname': obj.reviewer.fullname,
            }
        return None


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for task comments. 'author' is returned as the fullname string."""

    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        """Returns the full name of the author."""
        if obj.author:
            return obj.author.fullname
        return None
