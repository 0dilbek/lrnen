from rest_framework import serializers
from django.db import transaction
from .models import StudentGroup, User
from .permissions import is_platform_admin


def _levels_data(user):
    return [{'id': l.id, 'slug': l.slug, 'name': str(l)} for l in user.levels.all()]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class StudentGroupSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGroup
        fields = ['id', 'name']


class StudentGroupSerializer(serializers.ModelSerializer):
    student_ids = serializers.PrimaryKeyRelatedField(
        source='students', many=True, required=False,
        queryset=User.objects.filter(role='student', is_staff=False, is_superuser=False),
    )
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = StudentGroup
        fields = ['id', 'name', 'student_count', 'student_ids']
        read_only_fields = ['id']

    def get_student_count(self, obj):
        return obj.students.count()

    @staticmethod
    def _set_students(group, students):
        if students is None:
            return
        ids = [student.id for student in students]
        # A transfer changes membership only; levels and past results stay intact.
        User.objects.filter(study_group=group).exclude(id__in=ids).update(study_group=None)
        User.objects.filter(id__in=ids).update(study_group=group)
        if hasattr(group, '_prefetched_objects_cache'):
            group._prefetched_objects_cache.pop('students', None)

    @transaction.atomic
    def create(self, validated_data):
        students = validated_data.pop('students', None)
        group = StudentGroup.objects.create(**validated_data)
        self._set_students(group, students)
        return group

    @transaction.atomic
    def update(self, instance, validated_data):
        students = validated_data.pop('students', None)
        instance = super().update(instance, validated_data)
        self._set_students(instance, students)
        return instance


class UserSerializer(serializers.ModelSerializer):
    levels = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    group = StudentGroupSummarySerializer(source='study_group', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role', 'language', 'levels', 'group', 'created_at']
        read_only_fields = ['id', 'role', 'created_at']

    def get_levels(self, obj):
        return _levels_data(obj)

    def get_role(self, obj):
        return 'admin' if is_platform_admin(obj) else 'student'


class UserDetailSerializer(serializers.ModelSerializer):
    levels = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    group = StudentGroupSummarySerializer(source='study_group', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role', 'language', 'levels', 'group', 'created_at']

    def get_levels(self, obj):
        return _levels_data(obj)

    def get_role(self, obj):
        return 'admin' if is_platform_admin(obj) else 'student'


class CreateStudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)
    level_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, allow_empty=False
    )
    group_id = serializers.PrimaryKeyRelatedField(
        source='study_group', queryset=StudentGroup.objects.all(), required=False, allow_null=True,
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'password', 'language', 'level_ids', 'group_id']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Bu username band.")
        return value

    def validate_level_ids(self, value):
        from courses.models import Level
        if Level.objects.filter(id__in=value).count() != len(set(value)):
            raise serializers.ValidationError("Noto‘g‘ri daraja tanlangan.")
        return list(dict.fromkeys(value))

    def create(self, validated_data):
        password = validated_data.pop('password')
        level_ids = validated_data.pop('level_ids', [])
        user = User(role='student', **validated_data)
        user.set_password(password)
        user.save()
        if level_ids:
            from courses.models import Level
            user.levels.set(Level.objects.filter(id__in=level_ids))
        return user


class UpdateStudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4, required=False)
    level_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False, allow_empty=False
    )
    group_id = serializers.PrimaryKeyRelatedField(
        source='study_group', queryset=StudentGroup.objects.all(), required=False, allow_null=True,
    )

    class Meta:
        model = User
        fields = ['full_name', 'password', 'language', 'level_ids', 'group_id']

    def validate_level_ids(self, value):
        from courses.models import Level
        if Level.objects.filter(id__in=value).count() != len(set(value)):
            raise serializers.ValidationError("Noto‘g‘ri daraja tanlangan.")
        return list(dict.fromkeys(value))

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        level_ids = validated_data.pop('level_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        if level_ids is not None:
            from courses.models import Level
            instance.levels.set(Level.objects.filter(id__in=level_ids))
        return instance
